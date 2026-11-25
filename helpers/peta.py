import random
import re
import numpy as np
from manim import *
from .utils import PATH_PETA
from .pohon import ambil_pohon


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
 
 
KALIMANTAN = ["IDKB", "IDKT", "IDKS", "IDKI", "IDKU"]

# pohon di peta (kode daerah dari SVG), sama dengan scene 1
SEBARAN = {
    "IDAC": 2, "IDSU": 3, "IDSB": 2, "IDRI": 3, "IDJA": 2, "IDSS": 3, "IDBE": 1, "IDLA": 1,
    "IDKB": 4, "IDKT": 4, "IDKS": 2, "IDKI": 4, "IDKU": 2,
    "IDJB": 1, "IDJT": 2, "IDJI": 2, "IDNB": 1, "IDNT": 2,
    "IDSN": 2, "IDST": 3, "IDSG": 2, "IDSA": 1,
    "IDMA": 2, "IDMU": 1, "IDPA": 5, "IDPB": 2,
}


def hutan_padat(pohon, provinsi, ids, jumlah=14, jarak_min=0.12, tinggi=(0.3, 0.55), seed=7):
    """Hutan rapat di beberapa provinsi. Kembalikan (hutan, titik dasar tiap pohon)."""
    rng = random.Random(seed)
    nama_pohon = list(pohon.keys())
    daftar = []
    for k, id_prov in enumerate(ids):
        for (x, y) in random_point(provinsi[id_prov], jumlah, jarak_min=jarak_min, seed=seed + k):
            p = ambil_pohon(pohon, rng.choice(nama_pohon), rng.uniform(*tinggi))
            p.move_to([x, y, 0], aligned_edge=DOWN)
            daftar.append((p, p.get_bottom().copy()))
    # urut belakang -> depan: y besar = jauh = digambar dulu
    daftar.sort(key=lambda d: -d[1][1])
    return VGroup(*[p for p, _ in daftar]), [b for _, b in daftar]


def hutan_akhir_opening(pohon, provinsi):
    """Hutan persis seperti frame terakhir scene 1: hutan Kalimantan (sudah rebah, skala 0.7)
    lalu pohon di pulau-pulau lain."""
    drone, dasar = hutan_padat(pohon, provinsi, KALIMANTAN)
    for p, b in zip(drone, dasar):
        p.scale(0.7, about_point=b)
    sebaran = {k: v for k, v in SEBARAN.items() if k not in KALIMANTAN}
    return VGroup(*drone, *summon_trees(pohon, provinsi, sebaran))


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