from manim import *
from .utils import PATH_TERMOMETER
 
 
def load_thermometer(tinggi=4, path=PATH_TERMOMETER):
    """Termometer tanpa isi merkuri. Mengembalikan VGroup(kaca, skala).
    Merkurinya dibuat terpisah oleh merkuri_termometer() supaya tingginya bisa dianimasikan.
    """
    svg = SVGMobject(path)
    kaca = svg[1]                  # garis luar tabung + bola
    skala = VGroup(*svg[2:])       # 6 garis skala (svg[0] = merkuri penuh, tidak dipakai)
 
    kaca.set_stroke("#EEEEEE", width=3).set_fill("#222222", opacity=1)
    skala.set_stroke("#EEEEEE", width=3)
    kaca.set_z_index(0)
    skala.set_z_index(2)           # skala di atas merkuri
 
    termo = VGroup(kaca, skala)
    termo.scale_to_fit_height(tinggi)
    return termo
 
 
def merkuri_termometer(termo, level):
    """Merkuri untuk level 0..1 (0 = hampir kosong, 1 = penuh), mengikuti posisi dan ukuran termo."""
    kaca = termo[0]
    d = kaca.width                         # diameter bola
    r = d / 2
    lebar_tabung = d * 1.625 / 4.625       # perbandingan tabung : bola pada SVG asli
    pusat_bola = np.array([kaca.get_center()[0], kaca.get_bottom()[1] + r, 0])
    atas_maks = kaca.get_top()[1] - lebar_tabung / 2
 
    level = min(max(level, 0), 1)
    tinggi = 0.05 + (atas_maks - pusat_bola[1] - 0.05) * level
    warna = interpolate_color(ManimColor("#FFB000"), ManimColor("#E01010"), level)
 
    bola = Circle(radius=r * 0.78).move_to(pusat_bola)
    tabung = Rectangle(width=lebar_tabung * 0.5, height=tinggi).move_to(pusat_bola, aligned_edge=DOWN)
    merkuri = VGroup(bola, tabung).set_fill(warna, opacity=1).set_stroke(width=0)
    merkuri.set_z_index(1)
    return merkuri