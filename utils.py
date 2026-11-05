from pathlib import Path
from manim import *

ROOT = Path(__file__).resolve().parent      # utils.py ada di PROJEK/
SVG_DIR = ROOT / "assets" / "SVG"

PATH_POHON    = str(SVG_DIR / "pohon.svg")
PATH_API      = str(SVG_DIR / "api.svg")
PATH_PETA     = str(SVG_DIR / "peta.svg")
PATH_AWAN     = str(SVG_DIR / "awan.svg")
PATH_MATAHARI = str(SVG_DIR / "matahari.svg")

# ==================================  utility pohon ==================================  
NAMA_POHON = [ "pohon1", "pohon2", "pohon3", "pohon4", "pohon5", "pohon6", "pohon7", "pohon8" ]

def load_trees(path=PATH_POHON):
    svg = SVGMobject(path)
    crowns, trunks, leaves = [], [], []

    for m in svg.submobjects:
        r, g, b = m.get_fill_color().to_rgb()
        if r > 0.9:                    # hilangkan background
            continue
        elif r < 0.1 and g > 0.5:      # tajuk hijau tua
            crowns.append(m)
        elif r < 0.3 and g < 0.2:      # batang cokelat
            trunks.append(m)
        else:                          # daun kecil hijau muda
            leaves.append(m)

    pohon = {}
    for nama, c in zip(NAMA_POHON, crowns):
        # batang di baris yang sama (atas/bawah), lalu pilih x terdekat
        same_row = [t for t in trunks if (t.get_y() > 0) == (c.get_y() > 0)]
        t = min(same_row, key=lambda t: abs(t.get_x() - c.get_x()))
        pohon[nama] = VGroup(c, t)     # [0] = tajuk, [1] = batang

    return pohon, VGroup(*leaves)

def ambil_pohon(pohon, nama, tinggi):
    """Salinan satu pohon utuh dengan tinggi tertentu."""
    return pohon[nama].copy().scale_to_fit_height(tinggi)
# ==================================  utility pohon ==================================  

# ==================================  utility matahari ==================================
def load_sun(tinggi, buff, buang_latar=True, path=PATH_MATAHARI):
    svg = SVGMobject(path)
    bagian = list(svg.submobjects)

    if buang_latar and len(bagian) > 1:
        w, h = svg.width, svg.height
        bagian = [m for m in bagian if not (m.width > 0.98 * w and m.height > 0.98 * h)]

    matahari = VGroup(*bagian)
    matahari.scale_to_fit_height(tinggi)
    matahari.to_corner(UR, buff=buff)
    return matahari
# ==================================  utility matahari ==================================