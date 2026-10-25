"""Genera versiones encuadradas (cara y hombros) de cada expresión para usar en círculos.
Sale kit/picos/circ_<expresion>.png (600x600, transparente). Uso: python3 kit/tio_circulos.py"""
import glob, os
import numpy as np
from PIL import Image

KIT = os.path.dirname(os.path.abspath(__file__))
for f in glob.glob(os.path.join(KIT, "picos", "*.png")):
    name = os.path.basename(f)
    if name.startswith("circ_"):
        continue
    im = Image.open(f)
    a = np.asarray(im.getchannel("A")) > 40
    rows = np.where(a.any(axis=1))[0]
    top = rows[0]
    # ancho de la cabeza: medido un poco abajo de la coronilla
    probe = top + int(im.height * 0.16)
    cols = np.where(a[probe])[0]
    cx = (cols[0] + cols[-1]) // 2
    head_w = cols[-1] - cols[0]
    side = int(head_w * 2.3)
    y0 = max(0, top - int(side * 0.10))
    x0 = cx - side // 2
    crop = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    crop.paste(im.crop((x0, y0, x0 + side, y0 + side)), (0, 0))
    crop.resize((600, 600), Image.LANCZOS).save(os.path.join(KIT, "picos", "circ_" + name))
    print("ok", name)
