"""Проверить распространяемый пакет средствами стандартной библиотеки Python."""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zhb-blender-studio"


def check():
    entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert entry.startswith("---\nname: zhb-blender-studio\n"), "Имя скилла не совпадает"
    assert "description:" in entry.split("---", 2)[1], "Отсутствует описание"
    count = 0
    for file in ROOT.rglob("*"):
        if any(p in {".git", "dist", "__pycache__"} for p in file.relative_to(ROOT).parts) or not file.is_file():
            continue
        if file.suffix == ".py":
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        if file.suffix in {".py", ".md", ".yaml", ".svg"}:
            text = file.read_text(encoding="utf-8")
            assert not re.search(r"C:[/\\]Users[/\\]|Desktop[/\\]|\.claude[/\\]", text), f"Личный путь в файле {file}"
            assert not re.search(r"\[TO" + "DO:", text), f"Незаполненный шаблон в файле {file}"
        if file.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                assert (file.parent / target).exists(), f"Нерабочая ссылка в файле {file}: {target}"
        count += 1
    for name in ("poster.svg", "poster.png"):
        assert (ROOT / "media" / name).stat().st_size > 1000, f"Отсутствует постер: {name}"
    print(f"Структура, ссылки, отсутствие личных путей и синтаксис Python: в порядке ({count} файлов)")


if __name__ == "__main__":
    check()
