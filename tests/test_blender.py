"""Integration checks on generated scratch files, never the user's projects."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import bpy

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get("STUDIO_HELPER_PATH", ROOT / "zhb-blender-studio" / "scripts" / "studio.py"))
spec = importlib.util.spec_from_file_location("studio", SCRIPT)
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class StudioChecks(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.root = Path(tempfile.mkdtemp(prefix="zhb-studio-test-"))
        self.source = self.root / "source"
        self.source.mkdir()
        self.blend = self.source / "scene.blend"
        self.images = []
        for folder, color in (("a", (1, 0, 0, 1)), ("b", (0, 1, 0, 1))):
            directory = self.source / folder
            directory.mkdir()
            im = bpy.data.images.new(folder, width=64, height=32)
            im.generated_color = color
            im.filepath_raw = str(directory / "same-name.png")
            im.file_format = "PNG"
            im.save()
            bpy.data.images.remove(im)
            im = bpy.data.images.load(str(directory / "same-name.png"), check_existing=False)
            im.use_fake_user = True
            self.images.append(im)
        bpy.data.texts.new("Keep this script").write("important project notes")
        (self.source / "cache").mkdir()
        (self.source / "cache" / "frame.cache").write_bytes(b"cache fixture")
        bpy.ops.wm.save_as_mainfile(filepath=str(self.blend))
        self.source_digest = studio.sha256(self.blend)

    def test_report_is_read_only_and_has_no_project_canon(self):
        before = (bpy.context.scene.render.resolution_x, len(bpy.data.images), len(bpy.data.texts))
        rep = studio.report()
        self.assertEqual(len(rep["resources"]), 2)
        self.assertTrue(all(not r["missing"] for r in rep["resources"]))
        self.assertEqual(before, (bpy.context.scene.render.resolution_x, len(bpy.data.images), len(bpy.data.texts)))
        self.assertEqual(studio.sha256(self.blend), self.source_digest)

    def test_prepare_keeps_unspecified_settings_and_validates_before_mutation(self):
        height = bpy.context.scene.render.resolution_y
        studio.prepare(width=1280, fps=29.97, start=5, end=90)
        self.assertEqual(bpy.context.scene.render.resolution_y, height)
        self.assertAlmostEqual(studio.report()["settings"]["fps"], 29.97, places=4)
        with self.assertRaises(ValueError):
            studio.prepare(width=640, start=100, end=50)
        self.assertEqual(bpy.context.scene.render.resolution_x, 1280)
        with self.assertRaises(ValueError):
            studio.prepare(start=-99999999)

    def test_proxy_collisions_and_restoration(self):
        original_paths = [str(studio.absolute(im.filepath, im)) for im in self.images]
        original_hashes = [studio.sha256(p) for p in original_paths]
        result = studio.make_proxies(max_px=32)
        self.assertEqual(len(result["made"]), 2)
        self.assertNotEqual(self.images[0].filepath, self.images[1].filepath)
        self.assertTrue(all(tuple(im.size) == (32, 16) for im in self.images))
        self.assertEqual(len(studio.make_proxies(max_px=32)["made"]), 0)
        studio.restore_proxies()
        self.assertEqual([im.filepath for im in self.images], original_paths)
        self.assertTrue(all(tuple(im.size) == (64, 32) for im in self.images))
        self.assertEqual([studio.sha256(p) for p in original_paths], original_hashes)

    def test_restore_missing_original_does_not_drop_recovery_metadata(self):
        studio.make_proxies(max_px=32)
        original = Path(self.images[1][studio.PROXY_KEY])
        original.rename(original.with_suffix(".hidden"))
        with self.assertRaises(FileNotFoundError):
            studio.restore_proxies()
        self.assertTrue(all(studio.PROXY_KEY in im for im in self.images))

    def test_collect_survives_source_isolation_and_preserves_text(self):
        studio.make_proxies(max_px=32)
        dest = self.root / "delivery"
        result = studio.collect(dest, ["cache"])
        self.assertTrue(result["verification"]["fresh_open"])
        self.assertEqual(studio.sha256(self.blend), self.source_digest)
        self.assertTrue((dest / "cache" / "frame.cache").is_file())
        self.source.rename(self.root / "source-hidden")
        proc = subprocess.run([bpy.app.binary_path, "--background", str(dest / "scene.blend"),
                               "--python-exit-code", "1", "--python", str(SCRIPT), "--", "report"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        rep = json.loads(next(x[len("STUDIO_JSON "):] for x in proc.stdout.splitlines() if x.startswith("STUDIO_JSON ")))
        self.assertTrue(all(not r["missing"] for r in rep["resources"]))
        self.assertEqual(rep["datablocks"]["texts"], 1)
        self.assertFalse(rep["proxies"])
        manifest = json.loads((dest / "manifest.json").read_text())
        for row in manifest["resources"] + manifest["extras"]:
            self.assertEqual(studio.sha256(dest / row["path"]), row["sha256"])

    def test_collect_refuses_missing_resources_before_creating_output(self):
        studio.absolute(self.images[0].filepath, self.images[0]).rename(self.source / "missing.png")
        dest = self.root / "delivery"
        with self.assertRaises(ValueError):
            studio.collect(dest)
        self.assertFalse(dest.exists())
        self.assertFalse(list(self.root.glob(".studio-collect-*")))

    def test_collect_rejects_extra_traversal_and_existing_output(self):
        with self.assertRaises(ValueError):
            studio.collect(self.root / "delivery", ["../escape"])
        with self.assertRaises(ValueError):
            studio.collect(self.source / "cache" / "delivery", ["cache"])
        with self.assertRaises(ValueError):
            studio.collect(self.source)
        with self.assertRaises(ValueError):
            studio.new_file(self.blend)

    def test_sequence_gap_is_not_silently_collected(self):
        image = self.images[0]
        original = studio.absolute(image.filepath, image)
        import shutil
        for number in (1, 3):
            shutil.copy2(original, original.parent / f"frame{number:04d}.png")
        image.filepath = str(original.parent / "frame0001.png")
        image.source = "SEQUENCE"
        with self.assertRaises(ValueError):
            studio.collect(self.root / "delivery")

    def test_sequence_and_packed_resources_are_preserved(self):
        image = self.images[0]
        original = studio.absolute(image.filepath, image)
        import shutil
        for number in (1, 2, 3):
            shutil.copy2(original, original.parent / f"frame{number:04d}.png")
        image.filepath = str(original.parent / "frame0001.png")
        image.source = "SEQUENCE"
        self.images[1].pack()
        result = studio.collect(self.root / "delivery")
        self.assertEqual(len(result["resources"]), 3)
        self.assertTrue(self.images[1].packed_file)

    def test_collect_rejects_linked_libraries(self):
        mesh = bpy.data.meshes.new("LinkedMesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
        library_path = self.root / "library.blend"
        bpy.data.libraries.write(str(library_path), {mesh})
        with bpy.data.libraries.load(str(library_path), link=True) as (_, target):
            target.meshes = ["LinkedMesh"]
        with self.assertRaises(ValueError):
            studio.collect(self.root / "delivery")

    def test_cli_saves_new_copy_and_refuses_overwrite(self):
        output = self.root / "prepared.blend"
        command = [bpy.app.binary_path, "--background", str(self.blend), "--python-exit-code", "1",
                   "--python", str(SCRIPT), "--", "prepare", "--width", "1280", "--save", str(output)]
        proc = subprocess.run(command, capture_output=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(output.is_file())
        digest = studio.sha256(output)
        proc = subprocess.run(command, capture_output=True, timeout=120)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(digest, studio.sha256(output))
        self.assertEqual(self.source_digest, studio.sha256(self.blend))


suite = unittest.defaultTestLoader.loadTestsFromTestCase(StudioChecks)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise RuntimeError("Studio integration tests failed")
print(f"STUDIO_TESTS_PASSED {result.testsRun}")
