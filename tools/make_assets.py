"""Make the light-weight images the hand-built pages use (website review, 2 Nov 2026):
- assets/step-{1,2,3}.webp: the three step drawings at display size,
- favicon.ico, favicon-32.png, apple-touch-icon.png, icon-512.png,
- og.png: the 1200x630 link-preview image ("10% fee. Even at trial.").
Fonts are Windows system fonts (Segoe UI Black / Bold), so the images carry no third-party font licence.
Run once after changing a source drawing or the brand line; the outputs are committed.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = SITE / "assets"
YELLOW, INK, CREAM = (255, 228, 53), (20, 12, 10), (247, 245, 239)
BLACK_FONT = r"C:\Windows\Fonts\seguibl.ttf"
BOLD_FONT = r"C:\Windows\Fonts\segoeuib.ttf"


def steps():
    for n in (1, 2, 3):
        im = Image.open(ASSETS / f"step-{n}.png").convert("RGBA")
        w = 640
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out = ASSETS / f"step-{n}.webp"
        im.save(out, "WEBP", quality=82, method=6)
        print(out.name, out.stat().st_size)


def icon(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=round(size * 0.22), fill=YELLOW)
    f = ImageFont.truetype(BLACK_FONT, round(size * 0.56))
    box = d.textbbox((0, 0), "10", font=f)
    d.text(((size - (box[2] - box[0])) / 2 - box[0], (size - (box[3] - box[1])) / 2 - box[1]), "10", font=f, fill=INK)
    return im


def icons():
    big = icon(512)
    big.save(SITE / "icon-512.png")
    icon(180).convert("RGB").save(SITE / "apple-touch-icon.png")
    icon(32).save(SITE / "favicon-32.png")
    big.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("icons done")


def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(BLACK_FONT, 150)
    mid = ImageFont.truetype(BOLD_FONT, 34)
    mark = ImageFont.truetype(BLACK_FONT, 46)
    d.text((80, 70), "10% fee.", font=big, fill=INK)
    d.text((80, 245), "Even at trial.", font=big, fill=INK)
    d.text((80, 468), "Texas injury lawyers. No fee and no costs without a recovery.", font=mid, fill=INK)
    d.text((80, 538), "10flat Law", font=mark, fill=INK)
    drawing = Image.open(ASSETS / "step-3.png").convert("RGBA")
    drawing.thumbnail((360, 300))
    im.paste(drawing, (W - drawing.width - 60, 60), drawing)
    im.save(SITE / "og.png", optimize=True)
    print("og.png", (SITE / "og.png").stat().st_size)


if __name__ == "__main__":
    steps()
    icons()
    og()
