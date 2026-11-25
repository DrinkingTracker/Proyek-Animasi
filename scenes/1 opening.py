import _path  # noqa: F401
import random
import cairo
from manim import *
from helpers import load_trees, ambil_pohon, load_sun, load_map, random_point, summon_trees

WARNA_TANAH = "#1E3A24"     # peta saat close-up: terlihat seperti tanah hutan
WARNA_PETA = "#E6EDE0"      # peta setelah zoom out
KALIMANTAN = ["IDKB", "IDKT", "IDKS", "IDKI", "IDKU"]

# pohon di peta (kode daerah dari SVG), Kalimantan diisi oleh hutan drone
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
    # urut belakang -> depan: kamera melihat dari arah -y, jadi y besar = jauh = digambar dulu
    daftar.sort(key=lambda d: -d[1][1])
    return VGroup(*[p for p, _ in daftar]), [b for _, b in daftar]


def rebah(pohon, dasar, skala_akhir):
    """Animasi pohon tegak -> rebah jadi ikon 2D di peta, sambil mengecil."""
    awal = pohon.copy()

    def update(m, a):
        m.become(awal)
        m.rotate(-PI / 2 * a, axis=RIGHT, about_point=dasar)
        m.scale(interpolate(1, skala_akhir, a), about_point=dasar)

    return UpdateFromAlphaFunc(pohon, update)


class KameraDrone(ThreeDCamera):
    """ThreeDCamera (Cairo) menggeser titik sesuai frame_center di project_points, tetapi
    Camera dasar juga memasukkan frame_center ke konteks cairo yang di-cache. Akibatnya
    pergeseran dihitung dua kali dan 'nyangkut' di nilai lama. Di sini konteks cairo selalu
    berpusat di ORIGIN, jadi frame_center hanya diurus oleh project_points."""

    def get_cairo_context(self, pixel_array):
        ctx = self.get_cached_cairo_context(pixel_array)
        if ctx:
            return ctx
        pw, ph = self.pixel_width, self.pixel_height
        fw, fh = self.frame_width, self.frame_height
        surface = cairo.ImageSurface.create_for_data(pixel_array.data, cairo.FORMAT_ARGB32, pw, ph)
        ctx = cairo.Context(surface)
        ctx.scale(pw, ph)
        ctx.set_matrix(cairo.Matrix(pw / fw, 0, 0, -(ph / fh), pw / 2, ph / 2))
        self.cache_cairo_context(pixel_array, ctx)
        return ctx


class opening1(ThreeDScene):
    def __init__(self, **kwargs):
        super().__init__(camera_class=KameraDrone, **kwargs)

    def construct(self):
        pohon, _ = load_trees()
        peta, provinsi = load_map(lebar=12, warna=WARNA_TANAH)
        fokus = VGroup(*[provinsi[i] for i in KALIMANTAN]).get_center()

        # 1. layar gelap, kamera drone rendah di atas Kalimantan
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES, zoom=4, frame_center=fokus)
        self.wait(1)
        self.play(FadeIn(peta), run_time=1.5)

        # 2. hutan tumbuh dari tanah (drone view 3D)
        hutan_drone, dasar = hutan_padat(pohon, provinsi, KALIMANTAN)
        for p, b in zip(hutan_drone, dasar):
            p.rotate(PI / 2, axis=RIGHT, about_point=b)     # berdiri tegak di bidang tanah

        matahari = load_sun(2, 0.5)
        self.add_fixed_in_frame_mobjects(matahari)
        self.remove(matahari)

        self.begin_ambient_camera_rotation(rate=0.04)
        self.play(
            LaggedStart(*[GrowFromPoint(p, b) for p, b in zip(hutan_drone, dasar)], lag_ratio=0.03),
            run_time=4,
        )
        self.play(FadeIn(matahari, shift=DOWN * 0.5))
        matahari.add_updater(lambda m, dt: m.rotate(0.5 * dt))
        self.wait(2.5)
        self.stop_ambient_camera_rotation()

        # 3. smooth zoom out: kamera naik ke tampilan atas, pohon rebah, tanah jadi peta
        matahari.clear_updaters()
        self.play(FadeOut(matahari, shift=UP * 0.5), run_time=0.8)
        self.move_camera(
            phi=0, theta=-90 * DEGREES, zoom=1, frame_center=ORIGIN,
            added_anims=[peta.animate.set_fill(WARNA_PETA)]
                        + [rebah(p, b, 0.7) for p, b in zip(hutan_drone, dasar)],
            run_time=5, rate_func=smooth,
        )
        self.wait(0.5)

        # 4. pohon mengisi pulau-pulau lain
        sebaran = {k: v for k, v in SEBARAN.items() if k not in KALIMANTAN}
        hutan_peta = summon_trees(pohon, provinsi, sebaran)
        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in hutan_peta], lag_ratio=0.05), run_time=4)
        self.wait(1)

        # 5. statistik luas tutupan hutan di tengah layar
        redup = Rectangle(width=config.frame_width + 1, height=config.frame_height + 1, fill_color=BLACK, fill_opacity=0.5, stroke_width=0)
        panel = RoundedRectangle(width=7.6, height=3.4, corner_radius=0.3,fill_color=BLACK, fill_opacity=0.75, stroke_color="#7CD992", stroke_width=2)
        judul = Text("Luas Tutupan Hutan Indonesia · 2024", font_size=28, color=GRAY_A)
        judul.move_to(panel.get_top() + DOWN * 0.6)

        luas = ValueTracker(0)
        persen = ValueTracker(0)
        angka = always_redraw(lambda: Text(
            f"{luas.get_value():.1f}".replace(".", ",") + " juta ha", font_size=64, color="#7CD992", weight=BOLD,
        ).move_to(panel.get_center() + DOWN * 0.05))
        sub = always_redraw(lambda: Text(
            "≈ " + f"{persen.get_value():.1f}".replace(".", ",") + "% dari total daratan", font_size=30,
        ).move_to(panel.get_bottom() + UP * 0.6))

        self.play(FadeIn(redup), FadeIn(panel, scale=0.9), Write(judul), run_time=1.2)
        self.add(angka, sub)
        self.play(luas.animate.set_value(95.5), persen.animate.set_value(51.1), run_time=2.5, rate_func=rate_functions.ease_out_cubic)
        self.wait(3)

        angka.clear_updaters()
        sub.clear_updaters()
        self.play(FadeOut(VGroup(panel, judul, angka, sub)), FadeOut(redup), run_time=1)
        self.wait(1)
