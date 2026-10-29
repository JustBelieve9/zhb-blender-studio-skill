"""Validate the shareable package with the Python standard library."""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zhb-blender-studio"


def check():
    entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert entry.startswith("---\nname: zhb-blender-studio\n"), "Skill identity mismatch"
    assert "description:" in entry.split("---", 2)[1], "Missing description"
    count = 0
    for file in ROOT.rglob("*"):
        if any(p in {".git", "dist", "__pycache__"} for p in file.relative_to(ROOT).parts) or not file.is_file():
            continue
        if file.suffix == ".py":
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        if file.suffix in {".py", ".md", ".yaml", ".svg"}:
            text = file.read_text(encoding="utf-8")
            assert not re.search(r"C:[/\\]Users[/\\]|Desktop[/\\]|\.claude[/\\]", text), f"Private path in {file}"
            assert not re.search(r"\[TO" + "DO:", text), f"Unfinished template in {file}"
        if file.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                assert (file.parent / target).exists(), f"Broken link in {file}: {target}"
        count += 1
    for name in ("poster.svg", "poster.png"):
        assert (ROOT / "media" / name).stat().st_size > 1000, f"Missing poster: {name}"
    print(f"Package structure, links, privacy scan and Python syntax: OK ({count} files)")


if __name__ == "__main__":
    check()
