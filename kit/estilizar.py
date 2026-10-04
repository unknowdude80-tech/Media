"""Estiliza una foto con los colores de la marca.

Uso:  python3 kit/estilizar.py fotos/original.jpg salida.png [estilo] [ancho alto]
Estilos: duotono (por defecto) | poster | grabado
Tamaño por defecto 1080x760 (la franja de foto de la diapositiva tipo "foto").
Recorta al centro para llenar el tamaño pedido, con ligero sesgo hacia arriba (caras).
"""
import sys
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance

NAVY, MID, GOLD, PAPER = (15, 35, 64), (42, 63, 99), (212, 160, 23), (245, 242, 235)


def fit(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    img = img.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = int((img.height - h) * 0.35)        # sesgo hacia arriba
    return img.crop((x, y, x + w, y + h))


def gray(img):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1)
    return ImageEnhance.Contrast(g).enhance(1.15)


def ramp(stops):
    """Mapa de 256 colores interpolando entre (posición, color)."""
    lut = []
    for i in range(256):
        t = i / 255
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0)
                lut.append(tuple(round(a + (b - a) * k) for a, b in zip(c0, c1)))
                break
    return lut


def apply_lut(g, lut):
    r = g.point([c[0] for c in lut]); gg = g.point([c[1] for c in lut]); b = g.point([c[2] for c in lut])
    return Image.merge("RGB", (r, gg, b))


def duotono(g):
    return apply_lut(g, ramp([(0, NAVY), (0.55, MID), (0.85, (190, 160, 90)), (1, PAPER)]))


def poster(g):
    g = g.filter(ImageFilter.MedianFilter(5))
    levels = [NAVY, MID, GOLD, PAPER]
    cuts = [0.30, 0.55, 0.80]
    lut = []
    for i in range(256):
        t = i / 255
        lut.append(levels[sum(t > c for c in cuts)])
    return apply_lut(g, lut)


def grabado(g, cell=10):
    w, h = g.size
    out = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(out)
    small = g.resize((w // cell, h // cell), Image.BILINEAR)
    for y in range(small.height):
        for x in range(small.width):
            darkness = 1 - small.getpixel((x, y)) / 255
            r = (cell * 0.64) * darkness ** 1.1
            if r > 0.6:
                cx, cy = x * cell + cell / 2, y * cell + cell / 2
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY)
    return out


STYLES = {"duotono": duotono, "poster": poster, "grabado": grabado}


def estilizar(src, dst, estilo="duotono", w=1080, h=760):
    img = Image.open(src).convert("RGB")
    img = fit(img, w, h)
    out = STYLES[estilo](gray(img))
    out.save(dst)
    return dst


if __name__ == "__main__":
    a = sys.argv[1:]
    estilizar(a[0], a[1], a[2] if len(a) > 2 else "duotono",
              int(a[3]) if len(a) > 3 else 1080, int(a[4]) if len(a) > 4 else 760)
    print("ok", a[1])
