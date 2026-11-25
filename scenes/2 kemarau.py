import _path  # noqa: F401
from manim import *
from helpers import load_trees, load_sun, load_map, hutan_akhir_opening, load_thermometer, merkuri_termometer

WARNA_PETA = "#E6EDE0"          # sama dengan akhir scene 1, tidak berubah

# tone latar: hitam (normal) -> merah-oranye gelap (panas)
LATAR_ATAS = ["#000000", "#5A1A08", "#8C2E0C"]
LATAR_BAWAH = ["#000000", "#2A0A04", "#45120A"]
WARNA_PIJAR = "#FF6A1A"          # pendar panas di sekitar peta


def skala_warna(daftar, t):
    """Warna di sepanjang daftar warna untuk t = 0..1."""
    t = min(max(t, 0), 1)
    n = len(daftar) - 1
    i = min(int(t * n), n - 1)
    return interpolate_color(ManimColor(daftar[i]), ManimColor(daftar[i + 1]), t * n - i)


def pijar_panas(lebar=15, tinggi=8, lapisan=30):
    """Pendar lembut di belakang peta: elips bertumpuk, makin ke tengah makin pekat."""
    return VGroup(*[
        Ellipse(width=lebar * (1 - 0.021 * k), height=tinggi * (1 - 0.021 * k), stroke_width=0, fill_color=WARNA_PIJAR, fill_opacity=0)
        for k in range(lapisan)
    ])


class kemarau1(Scene):
    def construct(self):
        suhu = ValueTracker(0)          # 0 = normal, 1 = puncak kemarau
        t = suhu.get_value

        # ---------------- keadaan akhir scene 1 (view sama, tanpa statistik) ----------------
        latar = Rectangle(width=config.frame_width + 1, height=config.frame_height + 1, stroke_width=0, fill_opacity=1)
        latar.set_fill([BLACK, BLACK]).set_sheen_direction(DOWN)
        pijar = pijar_panas()
        pohon, _ = load_trees()
        peta, provinsi = load_map(lebar=12, warna=WARNA_PETA)
        hutan = hutan_akhir_opening(pohon, provinsi)
        self.add(latar, pijar, peta, hutan)
        self.wait(0.5)

        # ---------------- objek kemarau ----------------
        termo = load_thermometer(tinggi=2.8).move_to([-6.1, -2.3, 0])
        merkuri = always_redraw(lambda: merkuri_termometer(termo, t()))
        label_suhu = Text("Suhu", font_size=22, color=GRAY_A).next_to(termo, UP, buff=0.15)
        matahari = load_sun(1.8, 0.4)
        judul = Text("Musim Kemarau", font_size=36).to_edge(UP, buff=0.35)

        # ---------------- updater: sekitar peta bereaksi pada suhu ----------------
        latar.add_updater(lambda m: m.set_fill([skala_warna(LATAR_ATAS, t()), skala_warna(LATAR_BAWAH, t())]))
        pijar.add_updater(lambda g: [e.set_fill(opacity=0.017 * t()) for e in g])

        # vegetasi mengering: tajuk hijau -> kuning kecokelatan
        hijau = [ManimColor(p[0].get_fill_color()) for p in hutan]
        hutan.add_updater(lambda g: [p[0].set_fill(interpolate_color(h, ManimColor("#B8A14A"), 0.75 * t())) for p, h in zip(g, hijau)])

        skala = [1.0]
        def ubah_matahari(m, dt):
            m.rotate(0.5 * dt)
            m.set_color(interpolate_color(ManimColor("#F7CA11"), ManimColor("#FF4500"), t()))
            target = 1 + 0.25 * t()
            m.scale(target / skala[0])
            skala[0] = target

        # ---------------- masuknya musim kemarau ----------------
        self.play(
            FadeIn(termo, shift=RIGHT * 0.3), FadeIn(merkuri, shift=RIGHT * 0.3), FadeIn(label_suhu),
            FadeIn(matahari, shift=DOWN * 0.5), Write(judul),
            run_time=1.5,
        )
        matahari.add_updater(ubah_matahari)
        self.wait(1)

        # ---------------- suhu meningkat, sekitar peta memanas ----------------
        self.play(suhu.animate.set_value(1), run_time=10, rate_func=smooth)
        self.wait(2)
