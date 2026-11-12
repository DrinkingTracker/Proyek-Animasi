import _path  # noqa: F401
import random
from manim import *
from helpers import (load_trees, load_sun, load_map, summon_trees, load_thermometer, merkuri_termometer)
 
# hijau (normal) -> kuning -> oranye -> merah (panas)
WARNA_PANAS = ["#6F9C76", "#C9C75A", "#F2C230", "#F08A24", "#D7301F"]

sebaran = {
    "IDAC": 2, "IDSU": 3, "IDSB": 2, "IDRI": 3, "IDJA": 2, "IDSS": 3, "IDBE": 1, "IDLA": 1,
    "IDKB": 4, "IDKT": 4, "IDKS": 2, "IDKI": 4, "IDKU": 2,
    "IDJB": 1, "IDJT": 2, "IDJI": 2, "IDNB": 1, "IDNT": 2,
    "IDSN": 2, "IDST": 3, "IDSG": 2, "IDSA": 1,
    "IDMA": 2, "IDMU": 1, "IDPA": 5, "IDPB": 2,
}
 
def warna_panas(t):
    """Warna di skala panas untuk t = 0..1."""
    t = min(max(t, 0), 1)
    n = len(WARNA_PANAS) - 1
    i = min(int(t * n), n - 1)
    return interpolate_color(ManimColor(WARNA_PANAS[i]), ManimColor(WARNA_PANAS[i + 1]), t * n - i)
 
 
class kemarau1(Scene):
    def construct(self):
        suhu = ValueTracker(0)          # 0 = normal, 1 = puncak kemarau
        t = suhu.get_value
 
        # ---------------- objek ----------------
        latar = Rectangle(width=config.frame_width + 1, height=config.frame_height + 1, fill_color=BLACK, fill_opacity=1, stroke_width=0).set_z_index(-10)
        pohon, _ = load_trees()
        peta, provinsi = load_map(lebar=12)                       # warna asli (hijau)
        hutan = summon_trees(pohon, provinsi, sebaran)      # sama persis dengan adegan 1
        matahari = load_sun(2, 0.5)
        termo = load_thermometer(tinggi=4).move_to(LEFT * 6.2 + DOWN * 0.3)
        merkuri = always_redraw(lambda: merkuri_termometer(termo, t()))
 
        # ---------------- updater: semua bereaksi pada suhu ----------------
        rng = random.Random(3)
        for prov in peta:                                         # tiap provinsi memanas sedikit berbeda waktu
            tunda = rng.uniform(0, 0.25)
            prov.add_updater(lambda m, d=tunda: m.set_fill(warna_panas((t() - d) / (1 - d))))
 
        hutan.add_updater(lambda g: [p[0].set_fill(
            interpolate_color(ManimColor("#009933"), ManimColor("#C8A040"), min(t() * 1.5, 1))) for p in g])
 
        latar.add_updater(lambda m: m.set_fill(interpolate_color(ManimColor("#000000"), ManimColor("#3A1208"), t())))
 
        skala = [1.0]
        def ubah_matahari(m, dt):
            m.rotate(0.5 * dt)
            m.set_color(interpolate_color(ManimColor("#F7CA11"), ManimColor("#FF4500"), t()))
            target = 1 + 0.3 * t()
            m.scale(target / skala[0])
            skala[0] = target
 
        # ---------------- keadaan akhir adegan 1 ----------------
        self.add(latar, peta, hutan)
        judul = Text("Musim Kemarau", font_size=44).to_edge(UP)
 
        # ---------------- masuknya musim kemarau ----------------
        self.play(
            VGroup(peta, hutan).animate.scale(0.8).shift(RIGHT * 1.0 + DOWN * 0.5),
            FadeIn(termo), FadeIn(merkuri), FadeIn(matahari, shift=DOWN * 0.5),
            Write(judul),
            run_time=2,
        )
        matahari.add_updater(ubah_matahari)
        self.wait(1)
        self.play(FadeOut(judul), run_time=0.6)
 
        # ---------------- suhu meningkat ----------------
        self.play(suhu.animate.set_value(1), run_time=9, rate_func=smooth)
        self.wait(2)