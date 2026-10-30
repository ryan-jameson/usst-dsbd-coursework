from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "笔记补充"
OUTPUT = ROOT / "tmp" / "pdfs" / "notes_contact"
OUTPUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT = ImageFont.truetype(str(FONT_PATH), 20) if FONT_PATH.exists() else ImageFont.load_default()
images = sorted(SOURCE.glob("*.jpg"), key=lambda p: p.name)

cols, rows = 3, 2
cell_w, cell_h = 560, 760
label_h, gap = 44, 14
sheet_w = cols * cell_w + (cols + 1) * gap
sheet_h = rows * (cell_h + label_h) + (rows + 1) * gap

inventory = []
for start in range(0, len(images), cols * rows):
    batch = images[start : start + cols * rows]
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#DDE4E8")
    draw = ImageDraw.Draw(sheet)
    for offset, path in enumerate(batch):
        row, col = divmod(offset, cols)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + label_h + gap)
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        inventory.append((path.name, image.width, image.height))
        image.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        px = x + (cell_w - image.width) // 2
        py = y + (cell_h - image.height) // 2
        sheet.paste(image, (px, py))
        label = f"{start + offset + 1:02d}  {path.stem[-16:]}"
        draw.text((x + 4, y + cell_h + 6), label, font=FONT, fill="#173F5F")
    end = start + len(batch)
    sheet.save(OUTPUT / f"notes-{start + 1:03d}-{end:03d}.jpg", quality=92, optimize=True)

for name, width, height in inventory:
    print(f"{name}\t{width}x{height}")
print(f"created {((len(images) - 1) // (cols * rows)) + 1} contact sheets")
