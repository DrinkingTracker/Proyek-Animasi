import random
import re
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

# ==================================  utility peta ==================================
def load_map(lebar=12, warna=None, path=PATH_PETA):
    teks = open(path, encoding="utf-8").read()
    ids = re.findall(r'<path\b[^>]*?\bid="([^"]+)"', teks)   # urutan id = urutan bentuk
 
    svg = SVGMobject(path)
    bagian = list(svg.submobjects)[:len(ids)]   # sisanya lingkaran penanda, dibuang
 
    peta = VGroup(*bagian)
    peta.scale_to_fit_width(lebar).move_to(ORIGIN)
    if warna is not None:
        peta.set_fill(warna)
    return peta, dict(zip(ids, bagian))
 
 
def _di_dalam(titik, poligon_list):
    """Uji titik di dalam bentuk (ray casting, aturan even-odd)."""
    x, y = titik
    di_dalam = False
    for poly in poligon_list:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                di_dalam = not di_dalam
    return di_dalam
 
 
def random_point(provinsi, jumlah, jarak_min=0.3, seed=0):
    """Titik-titik acak (x, y) yang berada di dalam satu provinsi."""
    rng = random.Random(seed)
    poligon = [sp[::4, :2] for sp in provinsi.get_subpaths()]   # titik jangkar tiap kurva
    semua = np.vstack(poligon)
    x_min, y_min = semua.min(axis=0)
    x_max, y_max = semua.max(axis=0)
 
    hasil = []
    for _ in range(2000):
        if len(hasil) >= jumlah:
            break
        t = (rng.uniform(x_min, x_max), rng.uniform(y_min, y_max))
        if not _di_dalam(t, poligon):
            continue
        if all((t[0] - h[0]) ** 2 + (t[1] - h[1]) ** 2 > jarak_min ** 2 for h in hasil):
            hasil.append(t)
    return hasil
 
 
def summon_trees(pohon, provinsi, sebaran, tinggi=(0.35, 0.6), seed=1):
    rng = random.Random(seed)
    nama_pohon = list(pohon.keys())
    hutan = VGroup()
    for k, (id_prov, jumlah) in enumerate(sebaran.items()):
        for (x, y) in random_point(provinsi[id_prov], jumlah, seed=seed + k):
            p = ambil_pohon(pohon, rng.choice(nama_pohon), rng.uniform(*tinggi))
            p.move_to([x, y, 0], aligned_edge=DOWN)   # dasar pohon di titik itu
            hutan.add(p)
    hutan.submobjects.sort(key=lambda p: -p.get_bottom()[1])
    return hutan
# ==================================  utility peta ==================================