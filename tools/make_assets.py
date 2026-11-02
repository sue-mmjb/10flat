"""Make the light-weight images the hand-built pages use (website review, 2 Nov 2026):
- assets/step-{1,2,3}.webp: the three step drawings at display size,
- favicon.ico, favicon-32.png, apple-touch-icon.png, icon-512.png,
- og.png: the 1200x630 link-preview image ("10% fee. Even at trial."),
- share/<amount>.jpg: the preview image for a shared calculator result (share_image, called by build_home).
Fonts are Windows system fonts (Segoe UI Black / Bold), so the images carry no third-party font licence.
Run once after changing a source drawing or the brand line; the outputs are committed.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = SITE / "assets"
SRC = ROOT / "source" / "media"   # source drawings and retired media; not published
YELLOW, INK, CREAM = (255, 228, 53), (20, 12, 10), (247, 245, 239)
BLACK_FONT = r"C:\Windows\Fonts\seguibl.ttf"
BOLD_FONT = r"C:\Windows\Fonts\segoeuib.ttf"


def steps():
    for n in (1, 2, 3):
        im = Image.open(SRC / f"step-{n}.png").convert("RGBA")
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
    drawing = Image.open(SRC / "step-3.png").convert("RGBA")
    drawing.thumbnail((360, 300))
    im.paste(drawing, (W - drawing.width - 60, 60), drawing)
    im.save(SITE / "og.png", optimize=True)
    print("og.png", (SITE / "og.png").stat().st_size)


def _fit(d, text, font_path, start, max_w):
    size = start
    while size > 30:
        f = ImageFont.truetype(font_path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(font_path, size)


def share_image(amount, more, out):
    """1200x630 preview for a shared result: "On a $100,000 settlement:" / "keep $23,000 more"."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(im)
    line1 = f"On a ${round(amount):,} settlement:"
    line2 = f"keep ${round(more):,} more"
    d.text((80, 80), line1, font=_fit(d, line1, BOLD_FONT, 64, W - 160), fill=INK)
    f2 = _fit(d, line2, BLACK_FONT, 150, W - 152)
    d.text((76, 170), line2, font=f2, fill=INK)
    bottom = d.textbbox((76, 170), line2, font=f2)[3]
    d.text((80, bottom + 44), "than with a one-third fee. Our fee is 10%, even at trial.", font=ImageFont.truetype(BOLD_FONT, 34), fill=INK)
    d.text((80, 520), "10flat Law", font=ImageFont.truetype(BLACK_FONT, 46), fill=INK)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    steps()
    icons()
    og()
