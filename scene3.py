from manim import *
import numpy as np
import random


def buat_pohon_gundul(tinggi=4.0, warna="#080503", seed=1, flip=False):
    """
    Membuat 1 pohon gundul bercabang organik vektor yang ringan dirender.
    Kedalaman diatur ke 4 dengan kurva efisien agar render cepat namun tetap detail.
    """
    rng = random.Random(seed)
    pohon = VGroup()

    def tambah_cabang(titik_awal, sudut, panjang, tebal, kedalaman):
        if kedalaman == 0:
            return

        arah = np.array([np.cos(sudut), np.sin(sudut), 0])
        tegak_lurus = np.array([-np.sin(sudut), np.cos(sudut), 0])
        belokan = rng.uniform(-0.12, 0.12) * panjang

        titik_tengah = titik_awal + arah * (panjang * 0.5) + tegak_lurus * belokan
        titik_akhir = titik_awal + arah * panjang

        cabang = VMobject()
        cabang.set_points_as_corners([titik_awal, titik_tengah, titik_akhir])
        cabang.make_smooth()
        cabang.set_stroke(color=warna, width=tebal)
        cabang.set_cap_style(CapStyleType.ROUND)
        pohon.add(cabang)

        jumlah_anak = 2 if kedalaman > 1 else rng.choice([1, 2])
        for i in range(jumlah_anak):
            sisi = -1 if i == 0 else 1
            sudut_baru = sudut + sisi * rng.uniform(0.28, 0.58) + rng.uniform(-0.1, 0.1)
            panjang_baru = panjang * rng.uniform(0.62, 0.78)
            tebal_baru = max(1.4, tebal * 0.62)
            tambah_cabang(titik_akhir, sudut_baru, panjang_baru, tebal_baru, kedalaman - 1)

    sudut_awal = PI / 2 + rng.uniform(-0.08, 0.08)
    tambah_cabang(ORIGIN, sudut_awal, panjang=1.4, tebal=15, kedalaman=4)

    pohon.scale_to_fit_height(tinggi)
    if flip:
        pohon.flip(UP)

    pohon.shift(DOWN * pohon.get_bottom()[1])
    return pohon


class FireScene(MovingCameraScene):
    def construct(self):
        # =====================================================================
        # BAGIAN 1: PETA INDONESIA & TITIK API (100% DI DARATAN)
        # =====================================================================
        self.camera.background_color = "#0b1236"

        peta = SVGMobject("assets/peta.svg")
        peta.scale_to_fit_width(12.5)
        peta.set_fill(WHITE, opacity=1)
        peta.set_stroke("#cbd5e1", width=1.0)
        peta.move_to(ORIGIN)

        self.play(FadeIn(peta, run_time=1.3))

        def ambil_titik_daratan(jumlah_awal=10, jumlah_padat=22):
            """Mengambil titik dari dalam poligon daratan peta.svg (anti-nyasar ke laut)."""
            rng = random.Random(42)
            daratan_semua = []
            daratan_sumatra_kalimantan = []

            for sub in peta.family_members_with_points():
                if sub.width < 0.18 and sub.height < 0.18:
                    continue

                cx, cy, _ = sub.get_center()
                pts = sub.get_all_points()
                kandidat = [np.array([cx, cy, 0])]
                if len(pts) > 0:
                    for idx in np.linspace(0, len(pts) - 1, min(6, len(pts)), dtype=int):
                        titik_aman = pts[idx] * 0.45 + np.array([cx, cy, 0]) * 0.55
                        titik_aman[2] = 0
                        kandidat.append(titik_aman)

                daratan_semua.extend(kandidat)

                # Fokus daratan Sumatra & Kalimantan (cy >= -0.20 agar tidak masuk Laut Jawa)
                if (-5.8 <= cx <= -3.2 and -1.0 <= cy <= 2.0) or (-2.2 <= cx <= 0.1 and -0.20 <= cy <= 1.3):
                    daratan_sumatra_kalimantan.extend(kandidat)

            rng.shuffle(daratan_semua)
            rng.shuffle(daratan_sumatra_kalimantan)

            def saring_jarak(pool, target, min_dist=0.30):
                hasil = []
                for p in pool:
                    if all(np.linalg.norm(p - h) >= min_dist for h in hasil):
                        hasil.append(p)
                    if len(hasil) >= target:
                        break
                return hasil

            awal = saring_jarak(daratan_semua, jumlah_awal, min_dist=0.75)
            padat = saring_jarak(daratan_sumatra_kalimantan, jumlah_padat, min_dist=0.28)
            return awal, padat

        koordinat_awal, koordinat_padat = ambil_titik_daratan(jumlah_awal=10, jumlah_padat=22)

        def buat_titik_api(pos):
            inti = Dot(point=pos, radius=0.042, color="#ff1e00")
            pendar = Dot(point=pos, radius=0.10, color="#ff6600").set_opacity(0.45)
            grup_titik = VGroup(pendar, inti)
            fase = random.uniform(0, TAU)

            # Optimasi: ubah opacity saja tanpa scale_to_fit_width tiap frame (jauh lebih cepat!)
            def kedip(mob, dt, f=fase):
                t = self.renderer.time
                mob[0].set_opacity(0.32 + 0.28 * np.sin(t * 7 + f))

            grup_titik.add_updater(kedip)
            return grup_titik

        titik_api_group = VGroup()
        animasi_awal = []
        for pos in koordinat_awal:
            titik = buat_titik_api(pos)
            titik_api_group.add(titik)
            animasi_awal.append(GrowFromCenter(titik))

        self.play(LaggedStart(*animasi_awal, lag_ratio=0.12), run_time=1.8)

        animasi_tambah = []
        for pos in koordinat_padat:
            titik = buat_titik_api(pos)
            titik_api_group.add(titik)
            animasi_tambah.append(GrowFromCenter(titik))

        self.play(LaggedStart(*animasi_tambah, lag_ratio=0.05), run_time=2.2)
        self.wait(0.6)

        self.play(
            self.camera.frame.animate.scale(0.44).move_to([-2.3, 0.2, 0]),
            run_time=2.0,
            rate_func=smooth
        )
        self.wait(0.4)

        # =====================================================================
        # BAGIAN 2: TRANSISI BERSIH KE SCENE HUTAN TERBAKAR
        # =====================================================================
        for titik in titik_api_group:
            titik.clear_updaters()

        self.play(
            FadeOut(peta, run_time=0.9),
            FadeOut(titik_api_group, run_time=0.9),
        )
        self.camera.frame.scale(1 / 0.44).move_to(ORIGIN)

        # =====================================================================
        # BAGIAN 3: ADEGAN HUTAN TERBAKAR (OPTIMASI RENDER CEPAT)
        # =====================================================================
        tanah_belakang = ImageMobject("assets/tanah.png")
        tanah_belakang.scale_to_fit_width(config.frame_width)
        tanah_belakang.to_edge(DOWN, buff=0)
        tanah_belakang.set_color("#080503")
        tanah_belakang.set_z_index(2)

        tanah_depan = ImageMobject("assets/tanah1.png")
        tanah_depan.scale_to_fit_width(config.frame_width)
        tanah_depan.to_edge(DOWN, buff=0)
        tanah_depan.set_color("#080503")
        tanah_depan.set_z_index(3)

        tata_letak_pohon = [
            (-5.8, -3.5, 3.4, 11, False, 2.5),
            (-4.1, -3.2, 4.9, 22, False, 3.5),
            (-2.3, -3.1, 3.1, 33, True,  2.5),
            (-0.6, -3.2, 4.5, 44, False, 3.5),
            ( 1.2, -3.4, 3.3, 55, True,  2.5),
            ( 2.9, -3.6, 4.4, 66, False, 3.5),
            ( 4.6, -3.8, 5.2, 77, True,  3.5),
            ( 6.0, -3.9, 3.5, 88, False, 2.5),
        ]

        pohon_group = VGroup()
        for px, akar_y, tinggi, seed_val, flip, z_idx in tata_letak_pohon:
            p = buat_pohon_gundul(tinggi=tinggi, warna="#080503", seed=seed_val, flip=flip)
            p.move_to([px, akar_y, 0], aligned_edge=DOWN)
            p.set_z_index(z_idx)
            pohon_group.add(p)

        # Optimasi: jumlah bola dikurangi dari 10 -> 5 per lapis & hapus resize tiap frame
        blobs = Group()
        configs = [
            ("assets/fire_orange.png", -5.2, 1.2, 1,   4.8, 0.85),
            ("assets/fire_red.png",    -5.0, 2.2, 1.2, 5.6, 0.80),
            ("assets/smoke_gray.png",  -4.8, 3.5, 4,   7.5, 0.35),
        ]

        for filename, y_start_min, y_end_max, z_idx, base_s, max_op in configs:
            jumlah_bola = 5
            for i in range(jumlah_bola):
                blob = ImageMobject(filename)
                blob.scale_to_fit_width(base_s * random.uniform(0.9, 1.3))

                start_x = random.uniform(-6.5, 6.5)
                start_y = y_start_min + (i / jumlah_bola) * (y_end_max - y_start_min)

                blob.move_to([start_x, start_y, 0])
                blob.set_z_index(z_idx)
                blob.set_opacity(0)

                speed_y = random.uniform(0.55, 0.95)
                drift_speed = random.uniform(0.7, 1.3)
                phase = random.uniform(0, TAU)

                def update_blob(
                    mob, dt,
                    sy=speed_y, ds=drift_speed, p=phase,
                    ymin=y_start_min, ymax=y_end_max, mop=max_op
                ):
                    t = self.renderer.time
                    dx = 0.28 * np.cos(t * ds + p) * dt
                    mob.shift(UP * sy * dt + RIGHT * dx)

                    curr_y = mob.get_y()
                    progress = (curr_y - ymin) / (ymax - ymin)

                    if progress <= 0.0 or progress >= 1.0:
                        mob.set_opacity(0.0)
                    else:
                        smooth_alpha = np.sin(progress * PI) ** 0.7
                        mob.set_opacity(mop * smooth_alpha)

                    if curr_y >= ymax:
                        mob.set_y(ymin)
                        mob.set_x(random.uniform(-6.5, 6.5))

                blob.add_updater(update_blob)
                blobs.add(blob)

        # Optimasi: jumlah percikan bara disesuaikan ke 18 (tetap ramai, setengah beban render)
        embers = VGroup()
        for _ in range(18):
            ember = Line(
                ORIGIN,
                UP * random.uniform(0.14, 0.26) + RIGHT * 0.04,
                stroke_width=random.uniform(1.5, 2.5),
                color=random.choice(["#ff9900", "#ffcc33", "#ff5500"])
            )
            ember.set_opacity(random.uniform(0.55, 0.9))
            ember.move_to([random.uniform(-6.5, 6.5), random.uniform(-4.5, 4.0), 0])
            ember.set_z_index(5)

            e_speed = random.uniform(1.5, 2.8)
            def update_ember(mob, dt, es=e_speed):
                mob.shift((UP * es + RIGHT * 0.35) * dt)
                if mob.get_y() > 4.3:
                    mob.move_to([random.uniform(-6.5, 6.5), -4.3, 0])

            ember.add_updater(update_ember)
            embers.add(ember)

        self.add(blobs, embers)
        self.play(
            FadeIn(tanah_belakang, run_time=1.0),
            FadeIn(tanah_depan, run_time=1.0),
            FadeIn(pohon_group, run_time=1.0),
        )

        self.wait(10)