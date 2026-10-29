"""Standalone Blender project helpers. Run in Blender; see --help after `--`."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import bpy

VERSION = "0.1.0"
PROXY_KEY = "zhb_studio_original_v1"
KINDS = ("images", "sounds", "fonts", "movieclips", "cache_files", "volumes")


def absolute(raw, block=None):
    return Path(bpy.path.abspath(raw, library=getattr(block, "library", None))).absolute()


def packed(block):
    return bool(getattr(block, "packed_file", None) or getattr(block, "packed_files", None))


def file_set(block, raw):
    """Expand supported image sets; never silently collect a partial set."""
    path = absolute(raw, block)
    if isinstance(block, bpy.types.Image) and block.source == "TILED":
        if "<UDIM>" not in str(path):
            raise ValueError(f"{block.name}: tiled image has no <UDIM> pattern")
        return [Path(str(path).replace("<UDIM>", str(t.number))) for t in block.tiles]
    if isinstance(block, bpy.types.Image) and block.source == "SEQUENCE":
        match = re.fullmatch(r"(.*?)(\d+)(\.[^.]+)", path.name)
        if not match:
            raise ValueError(f"{block.name}: cannot identify sequence pattern")
        regex = re.compile(re.escape(match[1]) + r"\d{" + str(len(match[2])) + r"}" + re.escape(match[3]))
        members = sorted(p for p in path.parent.iterdir() if regex.fullmatch(p.name)) if path.parent.is_dir() else []
        if path not in members:
            members.append(path)
        numbers = sorted(int(re.search(r"(\d+)(\.[^.]+)$", p.name)[1]) for p in members)
        if numbers and numbers != list(range(numbers[0], numbers[-1] + 1)):
            raise ValueError(f"{block.name}: image sequence has gaps")
        return members
    return [path]


def resource_plan(originals=False):
    rows = []
    for kind in KINDS:
        for block in getattr(bpy.data, kind):
            raw = block.get(PROXY_KEY, block.filepath) if originals and kind == "images" else block.filepath
            if not raw or raw == "<builtin>" or packed(block):
                continue
            if kind == "images" and block.source in {"GENERATED", "VIEWER"}:
                continue
            issue = None
            if kind == "movieclips" and block.source == "SEQUENCE":
                issue = "movie clip sequences need a dedicated collector"
            if kind == "volumes" and block.is_sequence:
                issue = "volume sequences need a dedicated collector"
            try:
                files = file_set(block, raw)
            except (ValueError, OSError) as exc:
                files, issue = [], str(exc)
            rows.append({"kind": kind, "name": block.name, "raw": raw,
                         "files": [str(p) for p in files],
                         "missing": [str(p) for p in files if not p.is_file()],
                         "issue": issue, "linked": bool(block.library)})
    return rows


def report():
    sc = bpy.context.scene
    heavy = []
    for ob in sc.objects:
        for mod in ob.modifiers:
            if mod.type == "SUBSURF" and mod.render_levels > 2:
                heavy.append({"object": ob.name, "modifier": mod.name, "render_levels": mod.render_levels})
    for mat in bpy.data.materials:
        if mat.node_tree and mat.users:
            nodes = [n.bl_idname for n in mat.node_tree.nodes if n.type in {"BUMP", "DISPLACEMENT"}]
            if nodes:
                heavy.append({"material": mat.name, "nodes": nodes})
    return {"version": VERSION, "blender": bpy.app.version_string, "file": bpy.data.filepath,
            "scene": sc.name, "scene_objects": len(sc.objects),
            "datablocks": {k: len(getattr(bpy.data, k)) for k in (*KINDS, "meshes", "materials", "node_groups", "texts")},
            "settings": {"width": sc.render.resolution_x, "height": sc.render.resolution_y,
                         "percentage": sc.render.resolution_percentage,
                         "fps": sc.render.fps / sc.render.fps_base,
                         "frames": [sc.frame_start, sc.frame_end], "engine": sc.render.engine,
                         "view_transform": sc.view_settings.view_transform},
            "resources": resource_plan(),
            "libraries": [{"path": str(absolute(lib.filepath)), "exists": absolute(lib.filepath).is_file()}
                          for lib in bpy.data.libraries],
            "heavy_candidates": heavy,
            "proxies": [im.name for im in bpy.data.images if PROXY_KEY in im],
            "cache_note": "Provider-specific cache freshness and custom resource paths are not checked."}


def prepare(width=None, height=None, fps=None, start=None, end=None, engine=None):
    sc = bpy.context.scene
    if any(v is not None and not 4 <= v <= 65536 for v in (width, height)):
        raise ValueError("Resolution must be between 4 and 65536")
    if fps is not None and (not math.isfinite(fps) or not 1 <= fps <= 32767):
        raise ValueError("FPS must be between 1 and 32767")
    if (start if start is not None else sc.frame_start) > (end if end is not None else sc.frame_end):
        raise ValueError("Start frame is after end frame")
    for key, value in (("frame_start", start), ("frame_end", end)):
        prop = sc.bl_rna.properties[key]
        if value is not None and not prop.hard_min <= value <= prop.hard_max:
            raise ValueError(f"{key} is outside Blender's supported range")
    if engine is not None and engine not in {"BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"}:
        raise ValueError("Unsupported engine")
    if engine is not None:
        sc.render.engine = engine
    for key, value in (("resolution_x", width), ("resolution_y", height)):
        if value is not None:
            setattr(sc.render, key, value)
    if fps is not None:
        sc.render.fps = round(fps)
        sc.render.fps_base = round(fps) / fps
    if start is not None:
        sc.frame_start = start
    if end is not None:
        sc.frame_end = end
    return report()["settings"]


def make_proxies(max_px=1024, names=None):
    if not bpy.data.filepath:
        raise ValueError("Save the project before creating proxies")
    if not 16 <= max_px <= 16384:
        raise ValueError("Proxy limit must be between 16 and 16384")
    if names and set(names) - set(bpy.data.images.keys()):
        raise ValueError("Unknown image name in proxy selection")
    result = {"made": [], "skipped": [], "folder": None}
    for im in list(bpy.data.images):
        if names and im.name not in names:
            continue
        reason = None
        if im.library or packed(im) or im.source != "FILE" or PROXY_KEY in im:
            reason = "linked, packed, non-FILE or already proxied"
        elif im.is_float:
            reason = "floating-point/HDR texture"
        elif max(im.size) <= max_px:
            reason = "already small enough"
        if reason:
            result["skipped"].append({"image": im.name, "reason": reason})
            continue
        src = absolute(im.filepath, im)
        if not src.is_file():
            raise FileNotFoundError(str(src))
        if result["folder"] is None:
            result["folder"] = tempfile.mkdtemp(prefix="studio-proxies-", dir=Path(bpy.data.filepath).parent)
        digest = hashlib.sha256(str(src.resolve()).encode()).hexdigest()[:16]
        dst = Path(result["folder"]) / f"{src.stem[:64]}-{digest}-{max_px}.png"
        if not dst.exists():
            temp = bpy.data.images.load(str(src), check_existing=False)
            try:
                ratio = max_px / max(temp.size)
                temp.scale(max(1, round(temp.size[0] * ratio)), max(1, round(temp.size[1] * ratio)))
                temp.filepath_raw, temp.file_format = str(dst), "PNG"
                temp.save()
            finally:
                bpy.data.images.remove(temp)
        im[PROXY_KEY] = str(src)
        im.filepath = str(dst)
        im.reload()
        result["made"].append({"image": im.name, "path": str(dst), "size": list(im.size)})
    return result


def restore_proxies():
    targets = [im for im in bpy.data.images if PROXY_KEY in im]
    for im in targets:
        if not absolute(im[PROXY_KEY], im).is_file():
            raise FileNotFoundError(f"Original unavailable: {im.name}: {im[PROXY_KEY]}")
    names = []
    for im in targets:
        im.filepath = im[PROXY_KEY]
        im.reload()
        del im[PROXY_KEY]
        names.append(im.name)
    return {"restored": names}


def new_file(path):
    dst = Path(path).absolute()
    if dst.exists() or not dst.parent.is_dir():
        raise ValueError(f"Output must be a new file in an existing folder: {dst}")
    if bpy.data.filepath and dst.resolve() == Path(bpy.data.filepath).resolve():
        raise ValueError("Refusing to overwrite the source")
    return dst


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(output, extras=()):
    if not bpy.app.background or not bpy.data.filepath:
        raise ValueError("Collect requires a saved source in a fresh background Blender process")
    source = Path(bpy.data.filepath).resolve()
    dest = Path(output).absolute()
    if dest.exists() or not dest.parent.is_dir():
        raise ValueError("Collect destination must be new, with an existing parent")
    if bpy.data.libraries:
        raise ValueError("Linked libraries require a deliberate localization workflow before Collect")
    rows = resource_plan(originals=True)
    problems = [r for r in rows if r["missing"] or r["issue"] or r["linked"]]
    if problems:
        raise ValueError("Resource preflight failed: " + json.dumps(problems))
    extra_plan = []
    reserved = {"resources", "manifest.json", source.name.lower()}
    for raw in extras:
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0].lower() in reserved:
            raise ValueError(f"Invalid extra relative path: {raw}")
        item = source.parent / rel
        if not item.exists() or not item.resolve().is_relative_to(source.parent):
            raise ValueError(f"Extra must exist inside the source folder: {raw}")
        if item.is_dir() and dest.parent.resolve().is_relative_to(item.resolve()):
            raise ValueError("Collect staging cannot be inside an extra resource directory")
        chain = [source.parent.joinpath(*rel.parts[:i]) for i in range(1, len(rel.parts) + 1)]
        nested = list(item.rglob("*")) if item.is_dir() else []
        if any(p.is_symlink() or p.is_junction() for p in [*chain, *nested]):
            raise ValueError(f"Extra contains a symlink/junction: {raw}")
        if any(item == previous or item in previous.parents or previous in item.parents for previous, _ in extra_plan):
            raise ValueError(f"Overlapping extra paths: {raw}")
        extra_plan.append((item, rel))
    staging = Path(tempfile.mkdtemp(prefix=".studio-collect-", dir=dest.parent))
    manifest = {"version": VERSION, "blend": source.name, "resources": [], "extras": [],
                "cache_freshness": "Not checked; validate with the scene's simulation providers."}
    try:
        restore_proxies()
        for index, row in enumerate(rows):
            block = getattr(bpy.data, row["kind"])[row["name"]]
            sub = Path("resources") / f"{index:04d}-{row['kind']}"
            (staging / sub).mkdir(parents=True)
            for src_raw in row["files"]:
                src = Path(src_raw)
                target = staging / sub / src.name
                shutil.copy2(src, target)
                manifest["resources"].append({"path": (sub / src.name).as_posix(), "sha256": sha256(target)})
            block.filepath = "//" + (sub / absolute(row["raw"], block).name).as_posix()
        for item, rel in extra_plan:
            target = staging / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
            copied = target.rglob("*") if target.is_dir() else [target]
            for path in copied:
                if path.is_file():
                    manifest["extras"].append({"path": path.relative_to(staging).as_posix(), "sha256": sha256(path)})
        bpy.context.scene.render.filepath = "//render/"
        blend = staging / source.name
        bpy.ops.wm.save_as_mainfile(filepath=str(blend), copy=True, relative_remap=False)
        proc = subprocess.run([bpy.app.binary_path, "--background", str(blend), "--python-exit-code", "1",
                               "--python", str(Path(__file__).resolve()), "--", "report"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        lines = [line[len("STUDIO_JSON "):] for line in proc.stdout.splitlines() if line.startswith("STUDIO_JSON ")]
        if proc.returncode or not lines:
            raise RuntimeError("Fresh-open verification failed: " + (proc.stderr + proc.stdout)[-1500:])
        verification = json.loads(lines[-1])
        if verification["libraries"] or verification["proxies"] or any(r["missing"] or r["issue"] for r in verification["resources"]):
            raise RuntimeError("Collected project has unresolved resources")
        manifest["verification"] = {"fresh_open": True, "supported_paths_resolve": True,
                                    "source_isolation_test": False}
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        staging.rename(dest)
    except Exception as exc:
        raise RuntimeError(f"Collect failed; staging retained at {staging}: {exc}") from exc
    return {"output": str(dest), **manifest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspection = commands.add_parser("report")
    inspection.add_argument("--json")
    setup = commands.add_parser("prepare")
    for key in ("width", "height", "start", "end"):
        setup.add_argument("--" + key, type=int)
    setup.add_argument("--fps", type=float)
    setup.add_argument("--engine", choices=["CYCLES", "BLENDER_EEVEE", "BLENDER_WORKBENCH"])
    proxy = commands.add_parser("proxies")
    proxy.add_argument("--max-px", type=int, default=1024)
    proxy.add_argument("--image", action="append")
    restore = commands.add_parser("restore-proxies")
    for command in (setup, proxy, restore):
        command.add_argument("--save", required=True)
    delivery = commands.add_parser("collect")
    delivery.add_argument("--output", required=True)
    delivery.add_argument("--extra", action="append", default=[])
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    save = new_file(args.save) if hasattr(args, "save") else None
    if save and save.suffix.lower() != ".blend":
        raise ValueError("--save must name a new .blend file")
    if args.command == "report":
        result = report()
        if args.json:
            path = new_file(args.json)
            with path.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
    elif args.command == "prepare":
        result = prepare(**{k: getattr(args, k) for k in ("width", "height", "fps", "start", "end", "engine")})
    elif args.command == "proxies":
        result = make_proxies(args.max_px, args.image)
    elif args.command == "restore-proxies":
        result = restore_proxies()
    else:
        result = collect(args.output, args.extra)
    if save:
        bpy.ops.wm.save_as_mainfile(filepath=str(save), copy=True)
    print("STUDIO_JSON " + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
