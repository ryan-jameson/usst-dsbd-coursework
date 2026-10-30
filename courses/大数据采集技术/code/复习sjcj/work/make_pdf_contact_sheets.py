from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tmp" / "pdfs" / "supplement_v2_pages_round3"
OUTPUT = ROOT / "tmp" / "pdfs" / "supplement_v2_contact_round3"
OUTPUT.mkdir(parents=True, exist_ok=True)

font_path = Path(r"C:\Windows\Fonts\msyhbd.ttc")
font = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default()
pages = sorted(SOURCE.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))

cols, rows = 4, 2
cell_w, cell_h, label_h, gap = 390, 552, 34, 12
for start in range(0, len(pages), cols * rows):
    batch = pages[start : start + cols * rows]
    canvas = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * (cell_h + label_h) + (rows + 1) * gap), "#DCE3E7")
    draw = ImageDraw.Draw(canvas)
    for offset, path in enumerate(batch):
        row, col = divmod(offset, cols)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + label_h + gap)
        page = Image.open(path).convert("RGB")
        page.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        canvas.paste(page, (x + (cell_w - page.width) // 2, y + (cell_h - page.height) // 2))
        draw.text((x + 5, y + cell_h + 4), f"PDF page {start + offset + 1}", font=font, fill="#173F5F")
    end = start + len(batch)
    canvas.save(OUTPUT / f"contact-{start + 1:02d}-{end:02d}.jpg", quality=92)

print(f"pages={len(pages)} contacts={(len(pages)+cols*rows-1)//(cols*rows)}")
