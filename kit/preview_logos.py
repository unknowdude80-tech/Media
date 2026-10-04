"""Hoja de comparación: cada logo en círculo a tamaño real de IG (110 px) y FB (170 px), grande, y la portada."""
import os
from PIL import Image, ImageDraw, ImageFont

KIT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(KIT), "logo", "propuestas")
NAMES = [("1_globo", "1 · Globo"), ("2_monograma", "2 · Monograma ¿Y?"), ("3_dos_lados", "3 · Dos lados")]
BG, INK = (245, 242, 235), (15, 35, 64)
font = ImageFont.truetype(os.path.join(KIT, "fonts", "Archivo.ttf"), 30)
small = ImageFont.truetype(os.path.join(KIT, "fonts", "Archivo.ttf"), 20)


def circle(img, d):
    img = img.resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * 4, d * 4), fill=255)
    out = Image.new("RGBA", (d, d))
    out.paste(img, (0, 0), m.resize((d, d), Image.LANCZOS))
    return out


ROW = 420
sheet = Image.new("RGB", (1900, ROW * 3 + 40), BG)
d = ImageDraw.Draw(sheet)
for i, (key, label) in enumerate(NAMES):
    y = 20 + i * ROW
    logo = Image.open(f"{DIR}/{key}_perfil.png").convert("RGB")
    d.text((30, y), label, font=font, fill=INK)
    big = circle(logo, 300)
    sheet.paste(big, (30, y + 60), big)
    fb = circle(logo, 170)
    sheet.paste(fb, (370, y + 120), fb)
    d.text((370, y + 300), "FB 170 px", font=small, fill=INK)
    ig = circle(logo, 110)
    sheet.paste(ig, (580, y + 150), ig)
    d.text((580, y + 300), "IG 110 px", font=small, fill=INK)
    tiny = circle(logo, 40)
    sheet.paste(tiny, (730, y + 185), tiny)
    d.text((715, y + 300), "comentario", font=small, fill=INK)
    cov = Image.open(f"{DIR}/{key}_portada_fb.png").convert("RGB").resize((984, 374), Image.LANCZOS)
    sheet.paste(cov, (880, y + 30))
    d.text((880, y + 412 - 5), "Portada de Facebook", font=small, fill=INK)
sheet.save(os.path.join(DIR, "comparacion.png"))
print("ok")
