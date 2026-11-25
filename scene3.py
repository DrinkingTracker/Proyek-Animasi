from manim import *
import numpy as np
import random


def buat_pohon_gundul(tinggi=4.0, warna="#080503", seed=1, flip=False):
    """
    Membuat 1 pohon gundul bercabang organik murni vektor di Manim.
    Pangkal akar otomatis berada tepat di y = 0 (titik lokal) agar mudah ditancapkan ke tanah.
    """
    rng = random.Random(seed)
    pohon = VGroup()

    def tambah_cabang(titik_awal, sudut, panjang, tebal, kedalaman):
        if kedalaman == 0:
            return

        # Sedikit lengkungan organik di tengah cabang
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

        # Percabangan berikutnya
        jumlah_anak = 2 if kedalaman > 1 else rng.choice([1, 2])
        for i in range(jumlah_anak):
            sisi = -1 if i == 0 else 1
            sudut_baru = sudut + sisi * rng.uniform(0.28, 0.58) + rng.uniform(-0.1, 0.1)
            panjang_baru = panjang * rng.uniform(0.62, 0.78)
            tebal_baru = max(1.2, tebal * 0.62)
            tambah_cabang(titik_akhir, sudut_baru, panjang_baru, tebal_baru, kedalaman - 1)

    # Mulai tumbuh dari titik (0, 0, 0) lurus ke atas (PI/2)
    sudut_awal = PI / 2 + rng.uniform(-0.08, 0.08)
    tambah_cabang(ORIGIN, sudut_awal, panjang=1.4, tebal=15, kedalaman=5)

    pohon.scale_to_fit_height(tinggi)
    if flip:
        pohon.flip(UP)

    # Pastikan titik paling bawah (akar) selalu berada di y = 0
    pohon.shift(DOWN * pohon.get_bottom()[1])
    return pohon


class FireScene(MovingCameraScene):
    def construct(self):
        # =====================================================================
        # BAGIAN 1: PETA INDONESIA & TITIK API MENYEBAR (DETIK 0 - 10)
        # =====================================================================
        self.camera.background_color = "#0b1236"

        peta = SVGMobject("assets/peta.svg")
        peta.scale_to_fit_width(12.5)
        peta.set_fill(WHITE, opacity=1)
        peta.set_stroke("#cbd5e1", width=1.0)
        peta.move_to(ORIGIN)

        self.play(FadeIn(peta, run_time=1.5))

        # Titik api awal menyebar di berbagai pulau (Sumatra, Kalimantan, Jawa, Sulawesi, Nusa Tenggara, Papua)
        koordinat_awal = [
            [-5.2,  1.6, 0], # Aceh
            [-4.4,  0.8, 0], # Riau
            [-3.7, -0.4, 0], # Sumatra Selatan
            [-1.7,  0.2, 0], # Kalimantan Barat
            [-0.7,  0.1, 0], # Kalimantan Timur
            [-2.2, -1.5, 0], # Jawa Barat
            [-1.0, -1.7, 0], # Jawa Timur
            [ 0.9, -0.2, 0], # Sulawesi Tengah
            [ 1.2, -1.0, 0], # Sulawesi Selatan
            [ 1.3, -2.0, 0], # NTT / Nusa Tenggara
            [ 4.2, -0.7, 0], # Papua Barat
            [ 5.1, -1.1, 0], # Papua Selatan
        ]

        # Titik api susulan menyebar merata di seluruh Sumatra & Kalimantan
        koordinat_padat = [
            # Sebaran Sumatra
            [-4.9,  1.3, 0], [-4.6,  1.0, 0], [-4.2,  0.5, 0], [-4.0,  0.2, 0],
            [-3.8,  0.0, 0], [-3.5, -0.2, 0], [-3.9, -0.6, 0], [-3.4, -0.8, 0],
            [-4.5,  0.4, 0], [-4.1, -0.2, 0],
            # Sebaran Kalimantan
            [-1.9,  0.5, 0], [-1.5,  0.6, 0], [-1.2,  0.8, 0], [-1.4,  0.1, 0],
            [-1.1, -0.3, 0], [-0.8, -0.4, 0], [-0.5, -0.2, 0], [-0.3,  0.3, 0],
            [-0.6,  0.6, 0], [-0.9,  0.4, 0], [-1.3, -0.5, 0], [-0.2,  0.7, 0],
        ]

        def buat_titik_api(pos):
            inti = Dot(point=pos, radius=0.042, color="#ff1e00")
            pendar = Dot(point=pos, radius=0.10, color="#ff6600").set_opacity(0.45)
            grup_titik = VGroup(pendar, inti)
            fase = random.uniform(0, 2 * np.pi)

            def kedip(mob, dt, f=fase):
                t = self.renderer.time
                skala = 1.0 + 0.35 * np.sin(t * 7 + f)
                mob[0].scale_to_fit_width(0.20 * skala)
                mob[0].set_opacity(0.30 + 0.25 * np.sin(t * 7 + f))

            grup_titik.add_updater(kedip)
            return grup_titik

        # Munculkan titik api awal menyebar
        titik_api_group = VGroup()
        animasi_awal = []
        for pos in koordinat_awal:
            titik = buat_titik_api(pos)
            titik_api_group.add(titik)
            animasi_awal.append(GrowFromCenter(titik))

        self.play(LaggedStart(*animasi_awal, lag_ratio=0.12), run_time=2.0)

        # Titik api bertambah banyak & berkedip
        animasi_tambah = []
        for pos in koordinat_padat:
            titik = buat_titik_api(pos)
            titik_api_group.add(titik)
            animasi_tambah.append(GrowFromCenter(titik))

        self.play(LaggedStart(*animasi_tambah, lag_ratio=0.05), run_time=2.5)
        self.wait(0.8)

        # Zoom ke arah Sumatra dan Kalimantan
        self.play(
            self.camera.frame.animate.scale(0.44).move_to([-2.3, 0.2, 0]),
            run_time=2.2,
            rate_func=smooth
        )
        self.wait(0.5)

        # =====================================================================
        # BAGIAN 2: TRANSISI BERSIH KE SCENE HUTAN TERBAKAR (TANPA TIMPA-MENIMPA)
        # =====================================================================
        for titik in titik_api_group:
            titik.clear_updaters()

        # Bersihkan peta & titik api terlebih dahulu sambil reset kamera
        self.play(
            FadeOut(peta, run_time=1.0),
            FadeOut(titik_api_group, run_time=1.0),
        )
        self.camera.frame.scale(1 / 0.44).move_to(ORIGIN)

        # =====================================================================
        # BAGIAN 3: ADEGAN HUTAN TERBAKAR (DURASI ~13 DETIK)
        # =====================================================================
        # 1. Dua Lapis Tanah (Sama-sama gelap pekat #080503)
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

        # 2. Susunan Pohon Gundul Vektor (Dijamin menancap sempurna di tanah)
        # Format: (pos_x, akar_y, tinggi, seed_bentuk, flip, z_index)
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

        # 3. Bola Cahaya Api & Asap (Di belakang & sedikit menyelimuti pohon agar siluet tetap tegas)
        blobs = Group()
        configs = [
            # (file, batas_bawah, batas_atas, z_index, ukuran_dasar, max_opacity)
            ("assets/fire_orange.png", -5.2, 1.2, 1,   4.4, 0.85), # Cahaya api terang di belakang pohon
            ("assets/fire_red.png",    -5.0, 2.2, 1.2, 5.2, 0.80), # Bara merah di belakang pohon
            ("assets/smoke_gray.png",  -4.8, 3.5, 4,   7.2, 0.35), # Kabut asap tipis di depan pohon
        ]

        for filename, y_start_min, y_end_max, z_idx, base_s, max_op in configs:
            jumlah_bola = 10
            for i in range(jumlah_bola):
                blob = ImageMobject(filename)
                scale_factor = base_s * random.uniform(0.85, 1.25)
                blob.scale_to_fit_width(scale_factor)

                start_x = random.uniform(-6.8, 6.8)
                offset_bertahap = (i / jumlah_bola) * (y_end_max - y_start_min)
                start_y = y_start_min + offset_bertahap

                blob.move_to([start_x, start_y, 0])
                blob.set_z_index(z_idx)
                blob.set_opacity(0)

                speed_y = random.uniform(0.55, 0.95)
                drift_speed = random.uniform(0.7, 1.3)
                phase = random.uniform(0, 2 * np.pi)
                base_w = blob.width

                def update_blob(
                    mob, dt,
                    sy=speed_y, ds=drift_speed, p=phase, bw=base_w,
                    ymin=y_start_min, ymax=y_end_max, mop=max_op
                ):
                    t = self.renderer.time
                    dx = 0.3 * np.cos(t * ds + p) * dt
                    mob.shift(UP * sy * dt + RIGHT * dx)

                    pulse = 1.0 + 0.06 * np.sin(t * 2.2 + p)
                    mob.scale_to_fit_width(bw * pulse)

                    curr_y = mob.get_y()
                    progress = (curr_y - ymin) / (ymax - ymin)

                    if progress <= 0.0 or progress >= 1.0:
                        mob.set_opacity(0.0)
                    else:
                        smooth_alpha = np.sin(progress * np.pi) ** 0.7
                        mob.set_opacity(mop * smooth_alpha)

                    if curr_y >= ymax:
                        mob.set_y(ymin)
                        mob.set_x(random.uniform(-6.8, 6.8))

                blob.add_updater(update_blob)
                blobs.add(blob)

        # 4. Percikan Bara Api / Embers di Layer Paling Depan (z_index = 5)
        embers = VGroup()
        for _ in range(35):
            ember = Line(
                ORIGIN,
                UP * random.uniform(0.12, 0.25) + RIGHT * 0.04,
                stroke_width=random.uniform(1.5, 2.5),
                color=random.choice(["#ff9900", "#ffcc33", "#ff5500"])
            )
            ember.set_opacity(random.uniform(0.5, 0.9))
            ember.move_to([random.uniform(-6.8, 6.8), random.uniform(-4.5, 4.0), 0])
            ember.set_z_index(5)

            e_speed = random.uniform(1.5, 2.8)
            def update_ember(mob, dt, es=e_speed):
                mob.shift((UP * es + RIGHT * 0.35) * dt)
                if mob.get_y() > 4.3:
                    mob.move_to([random.uniform(-6.8, 6.8), -4.3, 0])

            ember.add_updater(update_ember)
            embers.add(ember)

        # Munculkan siluet tanah & pohon secara halus, lalu biarkan api & asap berkobar
        self.add(blobs, embers)
        self.play(
            FadeIn(tanah_belakang, run_time=1.2),
            FadeIn(tanah_depan, run_time=1.2),
            FadeIn(pohon_group, run_time=1.2),
        )

        # Jalankan animasi kebakaran selama 12 detik (total video ~23 detik)
        self.wait(12)