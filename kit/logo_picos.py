"""3 propuestas de foto de perfil con El Picos en ambiente de barrio (1080x1080) + hoja de comparación."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar import cerro, colonia, KIT, CSS, NAVY, GOLD, PAPER, TEAL
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(KIT), "logo", "propuestas_picos")
PIC = f"file://{KIT}/picos/circ_principal.png"
BADGE = lambda bg, ring: (f'<div style="position:absolute;right:120px;bottom:120px;width:230px;height:230px;border-radius:50%;background:{bg};'
                          f'box-shadow:0 0 0 12px {ring};display:flex;align-items:center;justify-content:center;font-family:SS4,serif;font-weight:900;font-size:118px;letter-spacing:-4px;z-index:5">'
                          f'<span style="color:{GOLD}">¿</span><span style="color:{PAPER}">Y</span><span style="color:{GOLD}">?</span></div>')
FACE = '<img src="{}" style="position:absolute;left:90px;top:120px;width:900px;z-index:3">'.format(PIC)
P = {
 "1_atardecer": f'''<div style="width:1080px;height:1080px;position:relative;overflow:hidden;background:linear-gradient(180deg,#24183F 0%,#5B2A6E 35%,#B8477A 62%,#F2B33D 90%)">
   <div style="position:absolute;left:-200px;bottom:120px;opacity:.95">{cerro("#3A1F4D",1500,583)}</div>
   <div style="position:absolute;left:0;bottom:-80px">{colonia(NAVY)}</div>{FACE}{BADGE(NAVY, GOLD)}</div>''',
 "2_barda": f'''<div class="barda" style="width:1080px;height:1080px;position:relative;overflow:hidden">
   <div style="position:absolute;left:-200px;bottom:-20px;opacity:.3">{cerro(TEAL,1500,583)}</div>{FACE}{BADGE(TEAL, PAPER)}</div>''',
 "3_noche": f'''<div style="width:1080px;height:1080px;position:relative;overflow:hidden;background:radial-gradient(ellipse at 50% 20%,#25386A 0%,#0F1B33 60%,#0A1222 100%)">
   <div style="position:absolute;inset:40px;border-radius:50%;box-shadow:0 0 0 18px {GOLD};z-index:4"></div>
   <div style="position:absolute;left:-200px;bottom:60px">{cerro("#22386B",1500,583)}</div>
   <div style="position:absolute;left:0;bottom:-90px">{colonia("#05080F", GOLD)}</div>{FACE}{BADGE(NAVY, GOLD)}</div>''',
}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1080})
    for k, body in P.items():
        f = os.path.join(OUT, k + ".html")
        open(f, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="margin:0">{body}</body></html>')
        pg.goto("file://" + f); pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, k + ".jpg"), type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        os.remove(f)
    b.close()

def circle(img, d):
    img = img.resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 4, d * 4), fill=255)
    out = Image.new("RGBA", (d, d)); out.paste(img, (0, 0), m.resize((d, d), Image.LANCZOS)); return out

font = ImageFont.truetype(os.path.join(KIT, "fonts", "Archivo.ttf"), 30)
sheet = Image.new("RGB", (1000, 3 * 360 + 20), (245, 242, 235)); d = ImageDraw.Draw(sheet)
for i, k in enumerate(P):
    y = 20 + i * 360; im = Image.open(os.path.join(OUT, k + ".jpg"))
    d.text((30, y), k.replace("_", " · ", 1).title(), font=font, fill=NAVY)
    for x, s in [(30, 280), (360, 170), (580, 110), (740, 40)]:
        c = circle(im, s); sheet.paste(c, (x, y + 50 + (280 - s) // 2), c)
sheet.save(os.path.join(OUT, "comparacion.jpg"), quality=90)
print("ok")
