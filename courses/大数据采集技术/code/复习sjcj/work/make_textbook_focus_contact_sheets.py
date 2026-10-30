from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tmp" / "pdfs" / "textbook_focus"
PAGES = sorted(SOURCE.glob("page-*.png"), key=lambda path: int(path.stem.split("-")[-1]))
FONT_PATH = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT = ImageFont.truetype(str(FONT_PATH), 22) if FONT_PATH.exists() else ImageFont.load_default()

cols, rows = 3, 2
thumb_w, thumb_h = 560, 792
label_h, gap = 32, 14
sheet_w = cols * thumb_w + (cols + 1) * gap
sheet_h = rows * (thumb_h + label_h) + (rows + 1) * gap

for start in range(0, len(PAGES), cols * rows):
    batch = PAGES[start : start + cols * rows]
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#DDE4E8")
    draw = ImageDraw.Draw(sheet)
    for offset, page in enumerate(batch):
        row, col = divmod(offset, cols)
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        image = Image.open(page).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        px = x + (thumb_w - image.width) // 2
        sheet.paste(image, (px, y))
        draw.text((x + 6, y + thumb_h + 3), f"PDF {start + offset + 1}", font=FONT, fill="#173F5F")
    end = start + len(batch)
    sheet.save(SOURCE / f"contact-{start + 1:03d}-{end:03d}.jpg", quality=91, optimize=True)

print(f"created {((len(PAGES) - 1) // (cols * rows)) + 1} contact sheets")
