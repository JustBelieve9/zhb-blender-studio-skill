"""Собрать архив с одной папкой скилла и лицензией."""
import hashlib
from pathlib import Path
import zipfile

from check_package import check, ROOT, SKILL

check()
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
archive = dist / "zhb-blender-studio-v0.1.1.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
    for path in sorted(SKILL.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            package.write(path, path.relative_to(ROOT))
    package.write(ROOT / "LICENSE", "zhb-blender-studio/LICENSE")
    package.write(ROOT / "LICENSE.ru.md", "zhb-blender-studio/LICENSE.ru.md")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
sums = [f"{digest}  {archive.name}"]
for name in ("poster.png", "poster.svg"):
    sums.append(f"{hashlib.sha256((ROOT / 'media' / name).read_bytes()).hexdigest()}  {name}")
(dist / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
print(f"Собран {archive.name}: {archive.stat().st_size} байт, SHA256 {digest}")
