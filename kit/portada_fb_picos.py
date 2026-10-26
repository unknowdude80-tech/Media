"""Portada de Facebook 1640x624 estilo atardecer con El Picos. Lo importante va al centro (FB recorta lados en móvil)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar import cerro, colonia, KIT, CSS, NAVY, GOLD, PAPER
from playwright.sync_api import sync_playwright
OUT = os.path.join(os.path.dirname(KIT), "logo")
html = f'''<div style="width:1640px;height:624px;position:relative;overflow:hidden;background:linear-gradient(180deg,#24183F 0%,#5B2A6E 35%,#B8477A 65%,#F2B33D 95%)">
<div style="position:absolute;left:0;bottom:-90px;opacity:.95">{cerro("#3A1F4D",1640,638)}</div>
<div style="position:absolute;left:0;bottom:-120px">{colonia(NAVY)}</div><div style="position:absolute;left:1080px;bottom:-120px">{colonia(NAVY)}</div>
<img src="file://{KIT}/picos/principal.png" style="position:absolute;left:960px;bottom:-30px;width:470px;z-index:3">
<div style="position:absolute;left:290px;top:130px;z-index:4;width:700px">
 <div style="font-family:Pirata,serif;font-size:64px;color:{GOLD};line-height:1">Con El Picos</div>
 <div style="font-family:Bebas,sans-serif;font-size:150px;line-height:.9;color:{PAPER};margin-top:8px">¿Y USTED QUÉ <span style="color:{GOLD}">OPINA</span>?</div>
 <div style="font-family:Bebas,sans-serif;font-size:34px;letter-spacing:3px;white-space:nowrap;color:{PAPER};margin-top:18px">LAS NOTICIAS QUE IMPORTAN, CONTADAS SIN CUENTOS</div>
</div></div>'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1640, "height": 624})
    f = os.path.join(OUT, ".tmp.html")
    open(f, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="margin:0">{html}</body></html>')
    pg.goto("file://" + f); pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(OUT, "portada_facebook_picos.jpg"), type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1640, "height": 624})
    os.remove(f); b.close()
print("ok")
