from manim import *
import numpy as np
import random

ASSET = "assets/scene 4"
ASSET_ROOT = "assets"

# Palet warna
HIJAU_SEGAR    = "#2d6a2d"
HIJAU_PUCAT    = "#8aad3a"
KUNING_KERING  = "#c8a040"
COKELAT_KERING = "#5e3c19"
COKELAT_GAMBUT = "#754b2b"
LANGIT_BIRU    = "#87ceeb"
LANGIT_SENJA   = "#e88020"


# ─── Helper 1: Memisahkan 8 Pohon dari SVG (Hanya parse 1x) ──────────────────
def load_trees_scene4(path=f"{ASSET}/pohon.svg"):
    svg = SVGMobject(path)
    crowns, trunks = [], []

    for m in svg.submobjects:
        r, g, b = m.get_fill_color().to_rgb()
        # Abaikan kotak latar krem/putih terang agar tidak menutupi layar
        if r > 0.85 and g > 0.85 and b > 0.70:
            continue
        # Tajuk pohon (dominan hijau)
        elif g > r and g > 0.35:
            crowns.append(m)
        # Batang pohon (cokelat gelap)
        elif r < 0.45 and g < 0.35:
            trunks.append(m)

    # Urutkan tajuk dari kiri ke kanan, baris atas lalu baris bawah
    crowns.sort(key=lambda m: (0 if m.get_y() > 0 else 1, m.get_x()))

    pohon_dict = {}
    for i, c in enumerate(crowns):
        if trunks:
            same_row = [t for t in trunks if (t.get_y() > 0) == (c.get_y() > 0)]
            kandidat = same_row if same_row else trunks
            t = min(kandidat, key=lambda tr: abs(tr.get_x() - c.get_x()))
            # VGroup([0] = tajuk daun, [1] = batang)
            pohon_dict[f"pohon{i+1}"] = VGroup(c.copy(), t.copy())
        else:
            pohon_dict[f"pohon{i+1}"] = VGroup(c.copy())

    return pohon_dict


def ambil_pohon(pohon_dict, nama, tinggi, flip=False):
    if nama not in pohon_dict:
        kunci = list(pohon_dict.keys())
        idx = int("".join(filter(str.isdigit, nama))) - 1
        nama = kunci[idx % len(kunci)]

    salinan = pohon_dict[nama].copy()
    salinan.scale_to_fit_height(tinggi)
    if flip:
        salinan.flip(UP)
    return salinan


# ─── Helper 2: Retakan tanah (crack lines) menyebar & terkunci di dalam tanah ──
def buat_retakan(cx, cy, panjang=1.1, kedalaman=3, seed=0):
    rng = random.Random(seed)
    grup = VGroup()

    def cabang(start, sudut, pjg, depth):
        if depth == 0 or pjg < 0.10:
            return
        end = start + np.array([np.cos(sudut), np.sin(sudut), 0]) * pjg
        # Kunci koordinat Y agar retakan tetap berada di dalam permukaan tanah depan
        end[1] = np.clip(end[1], -3.85, -1.70)

        ctrl = (start + end) / 2 + np.array([
            rng.uniform(-0.08, 0.08),
            rng.uniform(-0.08, 0.08), 0
        ]) * pjg
        garis = CubicBezier(start, ctrl, ctrl, end)
        garis.set_stroke(color="#2b1605", width=max(1.0, depth * 1.1), opacity=0.9)
        grup.add(garis)

        for _ in range(2):
            sudut_baru = sudut + rng.uniform(-PI / 2.6, PI / 2.6)
            cabang(end, sudut_baru, pjg * rng.uniform(0.50, 0.70), depth - 1)

    pusat = np.array([cx, cy, 0])
    for _ in range(3):
        arah = rng.uniform(0, TAU)
        cabang(pusat, arah, panjang * rng.uniform(0.65, 1.0), kedalaman)

    return grup


class ForestFireScene(MovingCameraScene):
    def construct(self):
        self.camera.background_color = "#1a110a"

        # =====================================================================
        # BAGIAN 1 : HUTAN SEGAR MULAI MENGERING (HIJAU -> COKELAT KEMARAU)
        # =====================================================================
        # Langit dibuat ekstra lebar & tinggi agar tidak pernah bocor saat kamera bergerak
        langit = Rectangle(
            width=28, height=18,
            fill_color=[LANGIT_BIRU, "#d4eefc"], fill_opacity=1
        ).set_stroke(width=0).move_to(ORIGIN).set_z_index(0)

        # Daratan bukit belakang (awalnya hijau segar)
        daratan = SVGMobject(f"{ASSET}/daratan_hijau.svg")
        daratan.scale_to_fit_width(config.frame_width + 2.5)
        daratan.move_to(DOWN * 1.0)
        daratan.set_fill("#245924", opacity=1)
        daratan.set_stroke(width=0)
        daratan.set_z_index(1)

        # Tanah depan bergelombang (awalnya HIJAU SEGAR, buff=-0.4 menutup penuh dasar layar)
        tanah_depan = SVGMobject(f"{ASSET}/tanah_bergelombang.svg")
        tanah_depan.scale_to_fit_width(config.frame_width + 2.5)
        tanah_depan.to_edge(DOWN, buff=-0.4)
        tanah_depan.set_fill(HIJAU_SEGAR, opacity=1)
        tanah_depan.set_stroke(width=0)
        tanah_depan.set_z_index(2)

        # Muat & pisahkan 8 pohon dari pohon.svg
        kumpulan_pohon = load_trees_scene4(f"{ASSET}/pohon.svg")

        # Format: (nama_pohon, pos_x, dasar_y, tinggi, flip, z_idx)
        tata_pohon = [
            ("pohon1", -5.8, -1.9, 2.5, False, 3),
            ("pohon2", -4.1, -2.0, 3.1, False, 4),
            ("pohon3", -2.2, -1.8, 2.7, True,  3),
            ("pohon4", -0.3, -2.0, 3.3, False, 4),
            ("pohon5",  1.6, -1.9, 2.6, True,  3),
            ("pohon6",  3.3, -2.0, 3.0, False, 4),
            ("pohon7",  5.0, -1.9, 2.8, True,  3),
            ("pohon8",  6.3, -1.8, 2.5, False, 3),
        ]

        pohon_group = VGroup()
        for nama, px, dasar_y, tinggi, flip, z in tata_pohon:
            p = ambil_pohon(kumpulan_pohon, nama, tinggi=tinggi, flip=flip)
            p.move_to([px, dasar_y, 0], aligned_edge=DOWN)
            p.set_z_index(z)
            pohon_group.add(p)

        self.add(langit)
        self.play(
            FadeIn(daratan, run_time=0.8),
            FadeIn(tanah_depan, run_time=0.8),
            FadeIn(pohon_group, run_time=1.0),
        )
        self.wait(0.5)

        # Perubahan musim kemarau:
        # Tanah depan hijau -> cokelat gambut, daratan -> cokelat tua, daun -> kuning kering
        anim_daun_kering = [
            p[0].animate.set_fill(random.choice([HIJAU_PUCAT, KUNING_KERING]))
            for p in pohon_group
        ]

        self.play(
            daratan.animate.set_fill(COKELAT_KERING),
            tanah_depan.animate.set_fill(COKELAT_GAMBUT),
            langit.animate.set_color([LANGIT_SENJA, "#f5c060"]),
            *anim_daun_kering,
            run_time=2.5,
            rate_func=smooth,
        )
        self.wait(0.5)

        # =====================================================================
        # BAGIAN 2 : KAMERA ZOOM KE LAHAN GAMBUT + RETAKAN MENYEBAR MERATA
        # =====================================================================
        retakan_group = VGroup()
        posisi_retakan = [
            # Baris atas lahan gambut (dari ujung kiri -6.3 sampai ujung kanan +6.3)
            (-6.3, -2.1, 0.95, 11),
            (-4.2, -2.2, 1.05, 12),
            (-2.0, -2.0, 0.90, 13),
            ( 0.1, -2.2, 1.10, 14),
            ( 2.3, -2.1, 0.95, 15),
            ( 4.5, -2.2, 1.05, 16),
            ( 6.3, -2.1, 0.90, 17),

            # Baris bawah lahan gambut (mengisi area bawah secara merata)
            (-5.4, -2.9, 0.85, 21),
            (-3.1, -3.0, 0.95, 22),
            (-0.9, -2.9, 0.90, 23),
            ( 1.2, -3.0, 0.95, 24),
            ( 3.4, -2.9, 0.85, 25),
            ( 5.5, -3.0, 0.90, 26),
        ]

        for cx, cy, pjg, seed in posisi_retakan:
            crack = buat_retakan(cx, cy, panjang=pjg, kedalaman=3, seed=seed)
            crack.set_z_index(2.5)
            retakan_group.add(crack)

        # Zoom kamera ke tengah-bawah lahan gambut
        self.play(
            self.camera.frame.animate.scale(0.62).move_to([0, -2.3, 0]),
            run_time=1.8,
            rate_func=smooth,
        )

        # Animasikan retakan merekah secara acak di seluruh lebar layar
        daftar_retakan = list(retakan_group)
        random.Random(99).shuffle(daftar_retakan)
        self.play(
            LaggedStart(*[Create(crack) for crack in daftar_retakan], lag_ratio=0.08),
            run_time=2.2,
        )
        self.wait(0.5)

        # =====================================================================
        # BAGIAN 3 : SILUET OKNUM MANUSIA BERJALAN MASUK
        # =====================================================================
        self.play(
            self.camera.frame.animate.scale(1 / 0.62).move_to(ORIGIN),
            run_time=1.2,
            rate_func=smooth,
        )

        def muat_pose_oknum(nama, tinggi=2.1):
            mob = SVGMobject(f"{ASSET}/{nama}.svg")
            mob.scale_to_fit_height(tinggi)
            # Warnai hanya siluet gelap, biarkan api obor tetap menyala kuning-oranye
            for sub in mob.submobjects:
                r, g, b = sub.get_fill_color().to_rgb()
                if r < 0.3 and g < 0.3 and b < 0.3:
                    sub.set_fill("#0a0603", opacity=1)
                    sub.set_stroke(width=0)
            mob.set_z_index(6)
            return mob

        pose_diam   = muat_pose_oknum("oknum",  tinggi=2.1)
        pose_jalan1 = muat_pose_oknum("oknum1", tinggi=2.1)
        pose_jalan2 = muat_pose_oknum("oknum2", tinggi=2.1)
        siklus_pose = [pose_jalan1, pose_diam, pose_jalan2, pose_diam]

        start_x = -7.8
        end_x   = -1.2
        kaki_y  = -2.3

        oknum = pose_diam.copy()
        oknum.move_to([start_x, kaki_y, 0], aligned_edge=DOWN)
        self.add(oknum)

        progres_jalan = ValueTracker(0.0)

        def update_jalan(mob):
            p = progres_jalan.get_value()
            curr_x = interpolate(start_x, end_x, p)
            if p < 1.0:
                idx = int(p * 14) % len(siklus_pose)
                mob.become(siklus_pose[idx])
            else:
                mob.become(pose_diam)
            mob.move_to([curr_x, kaki_y, 0], aligned_edge=DOWN)
            mob.set_z_index(6)

        oknum.add_updater(update_jalan)
        self.play(progres_jalan.animate.set_value(1.0), run_time=3.0, rate_func=linear)
        oknum.remove_updater(update_jalan)
        self.wait(0.6)

        # =====================================================================
        # BAGIAN 4 : API MULAI MUNCUL DAN ASAP MEMENUHI LAYAR
        # =====================================================================
        def buat_api_svg(px, py, lebar, z=5):
            api = SVGMobject("assets/SVG/api.svg")
            api.scale_to_fit_width(lebar)
            api.set_fill("#ff6600", opacity=1)
            api.set_stroke(width=0)
            api.move_to([px, py, 0], aligned_edge=DOWN)
            api.set_z_index(z)
            return api

        template_api = buat_api_svg(0, 0, lebar=1.0, z=5)

        api_pertama = template_api.copy().scale_to_fit_width(0.9)
        api_pertama.move_to([end_x + 0.6, kaki_y - 0.1, 0], aligned_edge=DOWN)

        # Oknum menundukkan obor ke tanah -> api pertama menyala -> oknum keluar layar
        self.play(
            oknum.animate.rotate(-0.18, about_point=oknum.get_bottom()),
            run_time=0.5
        )
        self.play(
            FadeIn(api_pertama, scale=0.6, run_time=0.5),
            FadeOut(oknum, shift=LEFT * 0.4, run_time=0.6),
        )

        # --- Blob api & asap ---
        blobs = Group()
        api_configs = [
            ("assets/fire_orange.png", -4.5, 1.5, 4, 3.8, 0.85),
            ("assets/fire_red.png",    -4.2, 2.5, 4, 4.5, 0.80),
            ("assets/smoke_gray.png",  -3.8, 5.0, 7, 6.5, 0.50),
        ]

        for filename, y_min, y_max, z_idx, base_s, max_op in api_configs:
            jumlah = 4
            for i in range(jumlah):
                blob = ImageMobject(filename)
                blob.scale_to_fit_width(base_s * random.uniform(0.85, 1.25))
                start_x_b = random.uniform(-6.5, 6.5)
                start_y_b = y_min + (i / jumlah) * (y_max - y_min)

                blob.move_to([start_x_b, start_y_b, 0])
                blob.set_z_index(z_idx)
                blob.set_opacity(0)

                speed_y   = random.uniform(0.55, 0.90)
                drift_spd = random.uniform(0.6, 1.2)
                phase     = random.uniform(0, TAU)
                base_w    = blob.width

                def make_updater(sy, ds, p, bw, ymin, ymax, mop):
                    def upd(mob, dt):
                        t  = self.renderer.time
                        dx = 0.25 * np.cos(t * ds + p) * dt
                        mob.shift(UP * sy * dt + RIGHT * dx)
                        cy = mob.get_y()
                        progress = (cy - ymin) / (ymax - ymin)
                        if progress <= 0.0 or progress >= 1.0:
                            mob.set_opacity(0.0)
                        else:
                            alpha = np.sin(progress * PI) ** 0.7
                            mob.set_opacity(mop * alpha)
                        if cy >= ymax:
                            mob.set_y(ymin)
                            mob.set_x(random.uniform(-6.5, 6.5))
                    return upd

                blob.add_updater(make_updater(speed_y, drift_spd, phase, base_w, y_min, y_max, max_op))
                blobs.add(blob)

        embers = VGroup()
        for _ in range(10):
            ember = Line(
                ORIGIN,
                UP * random.uniform(0.12, 0.22) + RIGHT * 0.03,
                stroke_width=random.uniform(1.5, 2.2),
                color=random.choice(["#ff9900", "#ffcc33", "#ff5500"])
            )
            ember.set_opacity(random.uniform(0.6, 0.95))
            ember.move_to([random.uniform(-6.5, 6.5), random.uniform(-4.5, 3.5), 0])
            ember.set_z_index(8)
            e_speed = random.uniform(1.5, 2.4)

            def make_ember_updater(es):
                def upd(mob, dt):
                    mob.shift((UP * es + RIGHT * 0.3) * dt)
                    if mob.get_y() > 4.5:
                        mob.move_to([random.uniform(-6.5, 6.5), -4.3, 0])
                return upd

            ember.add_updater(make_ember_updater(e_speed))
            embers.add(ember)

        self.add(blobs, embers)

        # Api menyebar di lahan gambut
        semua_api_sebar = VGroup()
        koordinat_api = [
            (-4.2, -2.4, 1.0), (-2.8, -2.6, 0.8), (-1.8, -2.4, 1.1),
            ( 0.2, -2.5, 1.2), ( 1.6, -2.6, 0.9), ( 3.0, -2.4, 1.1),
            ( 4.4, -2.5, 0.9),
        ]
        for ax, ay, aw in koordinat_api:
            a = template_api.copy().scale_to_fit_width(aw)
            a.move_to([ax, ay, 0], aligned_edge=DOWN)
            semua_api_sebar.add(a)

        self.play(
            LaggedStart(*[FadeIn(a, scale=0.5) for a in semua_api_sebar], lag_ratio=0.15),
            run_time=2.5,
        )
        self.wait(1.2)

        # =====================================================================
        # BAGIAN 5 : LAYAR MENGGELAP + TEKS PESAN UTAMA
        # =====================================================================
        overlay_gelap = Rectangle(
            width=28, height=18,
            fill_color=BLACK,
            fill_opacity=0,
        ).set_stroke(width=0).move_to(ORIGIN).set_z_index(10)
        self.add(overlay_gelap)

        teks_baris1 = Text(
            "KEMARAU MEMPERPARAH,",
            font_size=52,
            color=WHITE,
            weight=BOLD,
        )
        teks_baris2 = Text(
            "AKTIVITAS MANUSIA MEMICU.",
            font_size=52,
            color=WHITE,
            weight=BOLD,
        )
        teks_group = VGroup(teks_baris1, teks_baris2).arrange(DOWN, buff=0.3)
        teks_group.move_to(ORIGIN).set_z_index(12)

        self.play(
            overlay_gelap.animate.set_opacity(0.88),
            run_time=1.8,
            rate_func=smooth,
        )
        self.play(
            FadeIn(teks_group, shift=UP * 0.2),
            run_time=1.0,
        )
        self.wait(2.2)

        self.play(
            FadeOut(teks_group),
            overlay_gelap.animate.set_opacity(1.0),
            run_time=1.2,
        )
        self.wait(0.4)