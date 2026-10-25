"""Quita fondo verde (croma) y deja PNG transparente cuadrado.
Uso: python3 kit/croma.py entrada.jpg salida.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
# qué tan "verde de croma" es cada pixel
green = g - np.maximum(r, b)
alpha = np.clip(1 - (green - 40) / 60, 0, 1)          # >100 de dominancia verde = transparente
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
# quitar el reflejo verde en los bordes
g2 = np.where(g > np.maximum(r, b), np.maximum(r, b), g)
out = np.dstack([r, g2, b, alpha * 255]).astype(np.uint8)
img = Image.fromarray(out, "RGBA")
bbox = img.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
img = img.crop(bbox)
# lienzo cuadrado, personaje abajo-centro con margen arriba
side = int(max(img.width, img.height) * 1.08)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(img, ((side - img.width) // 2, side - img.height), img)
canvas.resize((1024, 1024), Image.LANCZOS).save(dst)
print("ok", dst)
