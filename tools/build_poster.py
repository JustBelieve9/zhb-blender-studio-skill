"""Создать минималистичный постер возможностей в редактируемом SVG и PNG."""
import argparse
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--font")
parser.add_argument("--bold-font")
args = parser.parse_args()


def find_font(explicit, names):
    if explicit:
        return explicit
    roots = [Path.home().anchor and Path(Path.home().anchor) / "Windows/Fonts",
             Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")]
    for root in roots:
        if root:
            for name in names:
                candidate = root / name
                if candidate.is_file():
                    return str(candidate)
    raise SystemExit("Укажите --font и --bold-font: пути к установленным шрифтам с кириллицей")


regular = find_font(args.font, ["segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf"])
bold = find_font(args.bold_font, ["segoeuib.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"])
BG, INK, MUTED, RULE, GREEN, MINT = "#F6F6F0", "#19221C", "#5B665E", "#CDD4CA", "#155B3D", "#D6E8D8"
im = Image.new("RGB", (1600, 2000), BG)
draw = ImageDraw.Draw(im)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2000" viewBox="0 0 1600 2000" role="img" aria-labelledby="title desc">',
       '<title id="title">ZHB Studio — скилл для Blender</title>',
       '<desc id="desc">Подготовка проекта, диагностика, чистка, прокси, варианты и сборка проекта. Инструкции и Python-помощники для ИИ-агента.</desc>',
       f'<rect width="1600" height="2000" fill="{BG}"/>']


def text(x, y, content, size, fill=INK, weight=False):
    font = ImageFont.truetype(bold if weight else regular, size)
    bbox = draw.textbbox((0, 0), content, font=font)
    if x + bbox[2] - bbox[0] > 1500:
        raise ValueError(f"Текст постера выходит за границы: {content}")
    draw.text((x, y), content, font=font, fill=fill, anchor="lt")
    # Текст в SVG остаётся редактируемым; начало строки привязано к верхнему краю.
    svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="Segoe UI, DejaVu Sans, sans-serif" font-size="{size}" font-weight="{700 if weight else 400}" fill="{fill}">{escape(content)}</text>')


def line(y):
    draw.line((100, y, 1500, y), fill=RULE, width=2)
    svg.append(f'<path d="M100 {y}H1500" stroke="{RULE}" stroke-width="2"/>')


text(100, 83, "zhb / studio", 42, weight=True)
text(1230, 94, "СКИЛЛ  0.1.1", 25, MUTED)
line(169)
text(94, 245, "Порядок", 136, weight=True)
text(94, 401, "в Blender-проекте.", 126, weight=True)
text(100, 586, "От проверки сцены до передачи файлов.", 43, MUTED)

features = [
    ("Подготовка проекта", "Размер, частота кадров, диапазон и движок.", "ПОМОЩНИК"),
    ("Диагностика сцены", "Состав, ресурсы и отсутствующие файлы.", "ПОМОЩНИК"),
    ("Чистка", "Проверка дублей и план удаления лишнего.", "СЦЕНАРИЙ"),
    ("Текстурные прокси", "Рабочие копии с возвратом оригиналов.", "ПОМОЩНИК"),
    ("Варианты сцены", "Отдельные файлы или переключение драйверами.", "СЦЕНАРИЙ"),
    ("Сборка проекта", "Копия проекта, ресурсы и проверка путей.", "ПОМОЩНИК"),
]
for index, (title, description, mode) in enumerate(features):
    y = 748 + index * 154
    line(y - 21)
    draw.rounded_rectangle((100, y + 2, 164, y + 62), radius=12, fill=MINT)
    svg.append(f'<rect x="100" y="{y + 2}" width="64" height="60" rx="12" fill="{MINT}"/>')
    text(114, y + 17, f"{index + 1:02d}", 26, GREEN, True)
    text(208, y, title, 45, weight=True)
    text(210, y + 69, description, 32, MUTED)
    text(1280, y + 15, mode, 21, GREEN)
line(1687)
text(100, 1765, "Blender 5.2", 36, weight=True)
text(480, 1765, "Без zhb-аддонов", 36, GREEN, True)
text(100, 1844, "Инструкции + Python-помощники для ИИ-агента", 31, MUTED)
text(100, 1920, "github.com/JustBelieve9/zhb-blender-studio-skill", 24, MUTED)
svg.append("</svg>")
out = ROOT / "media"
out.mkdir(exist_ok=True)
(out / "poster.svg").write_text("\n".join(svg) + "\n", encoding="utf-8", newline="\n")
im.save(out / "poster.png", optimize=True)
print("Постер: media/poster.svg и media/poster.png (1600 × 2000)")
