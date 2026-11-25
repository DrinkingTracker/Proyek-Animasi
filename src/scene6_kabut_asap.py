"""Scene 6 — Dampak Lanjutan: Kabut Asap Lintas Negara.

Animasi edukasi 2D bergaya editorial ("Kok Bisa!") menggunakan Manim Community + Pycairo SVG:
  - Bagian A: Hutan terbakar & hewan mengungsi, kabut asap makin tebal menutupi kanvas.
  - Bagian B: Asap menyelimuti SELURUH KOTA secara realistis (atap, gedung, jalan, tiang listrik).
              Stickman batuk sesak hebat (tremor, onomatopoeia Uhuk! Uhuk!), memakai masker N95,
              cut-in diagram paru-paru meradang & kartu darurat ISPA.
  - Bagian C: PETA ASIA TENGGARA jernih & tajam dari gambar kiriman pengguna (ImageMobject),
              dilengkapi simulasi kabut asap lintas negara (transboundary haze plume) yang sangat
              organik, natural, dan realistis menyelimuti Singapura, Malaysia, dan Brunei,
              diikuti kartu indikator kualitas udara dan transisi ke KTT Diplomatik ASEAN.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

# Pastikan import berjalan baik via `python main.py` maupun `manim src/scene6_kabut_asap.py`
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from manim import (
    DOWN,
    IN,
    LEFT,
    ORIGIN,
    OUT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    CurvedArrow,
    Dot,
    DoubleArrow,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    ImageMobject,
    LaggedStart,
    Line,
    MovingCameraScene,
    Rectangle,
    RoundedRectangle,
    SVGMobject,
    Text,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    ValueTracker,
    config,
    rate_functions,
)

from src.cairo_assets import PANORAMA_H, PANORAMA_W, ensure_all_assets
from src.config import (
    BADGE_ISPA_PATH,
    CONFERENCE_SUMMIT_PATH,
    DUBBING_SEGMENTS,
    HOTSPOTS_SEA_PX,
    LUNGS_DAMAGED_PATH,
    LUNGS_HEALTHY_PATH,
    MAP_SEA_PATH,
    PALETTE,
    SEA_MAP_SIZE,
    SETTLEMENT_LAYER_PATH,
    SHOW_SUBTITLES,
    STICKMAN_COUGH_PATH,
    STICKMAN_MASKED_PATH,
    STICKMAN_NORMAL_PATH,
    SVG_DIR,
    TARGET_COUNTRIES_SEA_PX,
)

PANORAMA_SCENE_HEIGHT = 8.0
PANORAMA_SCENE_WIDTH = PANORAMA_SCENE_HEIGHT * (PANORAMA_W / PANORAMA_H)


def smooth_step(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def build_subtitle_pill(text: str) -> VGroup:
    """Membuat kartu subtitle editorial bersih di bagian bawah layar."""
    label = Text(
        text,
        font="Segoe UI",
        font_size=20,
        color=PALETTE["text_light"],
        line_spacing=1.22,
    )
    pad_x, pad_y = 0.65, 0.28
    pill = RoundedRectangle(
        corner_radius=0.18,
        width=min(config.frame_width - 1.2, label.width + pad_x),
        height=label.height + pad_y,
        fill_color=PALETTE["card_bg"],
        fill_opacity=0.86,
        stroke_color="#FFFFFF",
        stroke_opacity=0.20,
        stroke_width=1.2,
    )
    if label.width > pill.width - 0.35:
        label.scale_to_fit_width(pill.width - 0.35)
    label.move_to(pill.get_center())
    group = VGroup(pill, label)
    group.to_edge(DOWN, buff=0.26)
    group.set_z_index(250)
    return group


class ForestFireParticles:
    """Partikel api & asap untuk Bagian A (Hutan Terbakar)."""

    def __init__(self, asset_paths: dict[str, Path], seed: int = 101) -> None:
        self.rng = random.Random(seed)
        self.asset_paths = asset_paths
        self.fire_intensity = ValueTracker(0.85)
        self.smoke_intensity = ValueTracker(0.85)
        self.clock = ValueTracker(0.0)

        self.flames: list[tuple[SVGMobject, dict]] = []
        self.smokes: list[tuple[SVGMobject, dict]] = []
        self.group = VGroup()
        self._init_particles()
        self._bind_updater()

    def _init_particles(self) -> None:
        for i in range(12):
            v = i % 3
            flame = SVGMobject(str(self.asset_paths[f"flame_{v}"]), use_svg_cache=False)
            flame.set_height(self.rng.uniform(0.7, 1.4))
            bx = self.rng.uniform(-7.0, 7.0)
            by = self.rng.uniform(-3.5, -1.8)
            flame.move_to([bx, by, 0.0])
            meta = {
                "base_x": bx,
                "base_y": by,
                "base_h": flame.height,
                "phase": self.rng.uniform(0, math.tau),
                "speed": self.rng.uniform(4.0, 7.5),
            }
            self.flames.append((flame, meta))
            self.group.add(flame)

        for i in range(20):
            smoke = SVGMobject(str(self.asset_paths["smoke_puff"]), use_svg_cache=False)
            smoke.set_height(self.rng.uniform(1.2, 2.6))
            sx = self.rng.uniform(-8.0, 8.0)
            sy = self.rng.uniform(-2.5, 3.2)
            smoke.move_to([sx, sy, 0.0])
            meta = {
                "base_x": sx,
                "base_y": sy,
                "speed_x": self.rng.uniform(0.18, 0.45),
                "speed_y": self.rng.uniform(0.25, 0.60),
            }
            self.smokes.append((smoke, meta))
            self.group.add(smoke)

    def _bind_updater(self) -> None:
        def update_sys(_mob, dt: float) -> None:
            self.clock.increment_value(dt)
            t = self.clock.get_value()
            f_int = self.fire_intensity.get_value()
            s_int = self.smoke_intensity.get_value()

            for flame, meta in self.flames:
                flicker = 0.85 + 0.25 * math.sin(t * meta["speed"] + meta["phase"])
                target_h = max(0.1, meta["base_h"] * flicker * f_int)
                flame.stretch_to_fit_height(target_h)
                flame.set_opacity(min(1.0, f_int * 0.95))

            for smoke, meta in self.smokes:
                drift_x = meta["base_x"] + (t * meta["speed_x"]) % 16.0 - 8.0
                drift_y = meta["base_y"] + (t * meta["speed_y"]) % 7.0 - 3.5
                smoke.move_to([drift_x, drift_y, 0.0])
                smoke.set_opacity(min(0.85, s_int * 0.70))

        self.group.add_updater(update_sys)


class CitySmogSystem:
    """Sistem kabut asap masif yang menyelimuti seluruh kawasan kota (Bagian B)."""

    def __init__(self, smoke_svg_path: Path, seed: int = 505) -> None:
        self.rng = random.Random(seed)
        self.smoke_svg_path = smoke_svg_path
        self.clock = ValueTracker(0.0)
        self.density = ValueTracker(0.5)

        self.clouds: list[tuple[SVGMobject, dict]] = []
        self.soot_particles: list[tuple[Dot, dict]] = []
        self.group = VGroup()
        self._init_smog()
        self._bind_updater()

    def _init_smog(self) -> None:
        # Lapisan awan asap tebal bergulung melintasi seluruh kota (atap, gedung, jalan raya)
        for i in range(18):
            cloud = SVGMobject(str(self.smoke_svg_path), use_svg_cache=False)
            cloud.set_height(self.rng.uniform(2.2, 4.5))
            cx = self.rng.uniform(-9.5, 9.5)
            cy = self.rng.uniform(-2.8, 3.2)
            cloud.move_to([cx, cy, 0.0])
            cloud.set_opacity(0.35)
            meta = {
                "base_x": cx,
                "base_y": cy,
                "speed_x": self.rng.uniform(0.35, 0.85),
                "speed_y": self.rng.uniform(-0.08, 0.12),
                "phase": self.rng.uniform(0, math.tau),
            }
            self.clouds.append((cloud, meta))
            self.group.add(cloud)

        # Partikel jelaga abu halus PM2.5 melayang di udara seluruh kota
        for i in range(32):
            dot = Dot(
                point=[self.rng.uniform(-7.5, 7.5), self.rng.uniform(-3.8, 3.8), 0.0],
                radius=self.rng.uniform(0.03, 0.07),
                color="#2B2623",
            ).set_opacity(self.rng.uniform(0.4, 0.8))
            meta = {
                "speed_x": self.rng.uniform(0.5, 1.4),
                "speed_y": self.rng.uniform(-0.3, 0.2),
                "drift_w": self.rng.uniform(2.0, 5.0),
            }
            self.soot_particles.append((dot, meta))
            self.group.add(dot)

    def _bind_updater(self) -> None:
        def update_city_smog(_mob, dt: float) -> None:
            self.clock.increment_value(dt)
            t = self.clock.get_value()
            d = self.density.get_value()

            for cloud, meta in self.clouds:
                cur_x = (meta["base_x"] + t * meta["speed_x"] + 10.0) % 20.0 - 10.0
                cur_y = meta["base_y"] + 0.25 * math.sin(t * 1.5 + meta["phase"])
                cloud.move_to([cur_x, cur_y, 0.0])
                cloud.set_opacity(min(0.85, 0.40 * d))

            for dot, meta in self.soot_particles:
                p = dot.get_center()
                nx = (p[0] + dt * meta["speed_x"] + 8.0) % 16.0 - 8.0
                ny = p[1] + dt * meta["speed_y"] + 0.04 * math.sin(t * meta["drift_w"])
                if ny < -4.0:
                    ny = 4.0
                dot.move_to([nx, ny, 0.0])
                dot.set_opacity(min(0.9, 0.65 * d))

        self.group.add_updater(update_city_smog)


class Scene6KabutAsap(MovingCameraScene):
    """Animasi Utama Scene 6 — Dampak Lanjutan: Kabut Asap Lintas Negara."""

    def construct(self) -> None:
        self.camera.frame.save_state()
        self.asset_paths = ensure_all_assets()
        self._subtitle_mob: VGroup | None = None

        self._play_part_a_ecosystem_damage()
        self._play_part_b_human_impact()
        self._play_part_c_transboundary_haze()

    # ------------------------------------------------------------------
    # Subtitle Helpers
    # ------------------------------------------------------------------
    def _set_subtitle(self, segment_idx: int, run_time: float = 0.45) -> None:
        if not SHOW_SUBTITLES:
            return
        new_sub = build_subtitle_pill(DUBBING_SEGMENTS[segment_idx]["text"])
        if self._subtitle_mob is None:
            self._subtitle_mob = new_sub
            self.play(FadeIn(new_sub, shift=UP * 0.14), run_time=run_time, rate_func=rate_functions.smooth)
        else:
            old_sub = self._subtitle_mob
            self._subtitle_mob = new_sub
            self.play(
                FadeOut(old_sub, shift=DOWN * 0.08),
                FadeIn(new_sub, shift=UP * 0.12),
                run_time=run_time,
                rate_func=rate_functions.smooth,
            )

    def _clear_subtitle(self, run_time: float = 0.45) -> None:
        if self._subtitle_mob is not None:
            self.play(FadeOut(self._subtitle_mob, shift=DOWN * 0.1), run_time=run_time)
            self._subtitle_mob = None

    # ==================================================================
    # BAGIAN A — KERUSAKAN EKOSISTEM (0.0s - 8.5s)
    # ==================================================================
    def _play_part_a_ecosystem_damage(self) -> None:
        self._set_subtitle(0, run_time=0.40)

        # Layer Hutan Terbakar (Kontinuitas Scene 5)
        self.sky = SVGMobject(str(self.asset_paths["sky_burning"]), use_svg_cache=False)
        self.sky.set_height(PANORAMA_SCENE_HEIGHT).move_to(ORIGIN)

        self.forest_far = SVGMobject(str(self.asset_paths["forest_far_burnt"]), use_svg_cache=False)
        self.forest_far.set_height(PANORAMA_SCENE_HEIGHT).move_to(ORIGIN)

        self.forest_mid = SVGMobject(str(self.asset_paths["forest_mid_burnt"]), use_svg_cache=False)
        self.forest_mid.set_height(PANORAMA_SCENE_HEIGHT).move_to(ORIGIN)

        self.forest_fg = SVGMobject(str(self.asset_paths["forest_fg_burnt"]), use_svg_cache=False)
        self.forest_fg.set_height(PANORAMA_SCENE_HEIGHT).move_to(ORIGIN)

        self.forest_group = VGroup(self.sky, self.forest_far, self.forest_mid, self.forest_fg)
        self.add(self.forest_group)

        self.particles = ForestFireParticles(self.asset_paths, seed=123)
        self.add(self.particles.group)

        # Hewan-hewan Mengungsi
        self.orangutan = SVGMobject(str(SVG_DIR / "orangutan.svg"), use_svg_cache=False)
        self.orangutan.set_height(1.65).move_to([-1.5, -1.5, 0.0])

        self.deer = SVGMobject(str(SVG_DIR / "deer.svg"), use_svg_cache=False)
        self.deer.set_height(1.75).move_to([2.2, -1.45, 0.0])

        self.hornbill = SVGMobject(str(SVG_DIR / "hornbill.svg"), use_svg_cache=False)
        self.hornbill.set_height(1.15).move_to([-6.5, 2.2, 0.0])

        self.animals_group = VGroup(self.orangutan, self.deer, self.hornbill)
        self.add(self.animals_group)

        # Lapisan Kabut Asap Pekat (Smog Blanket Hutan)
        self.smog_overlay = Rectangle(
            width=config.frame_width * 1.5,
            height=config.frame_height * 1.5,
            fill_color="#C4A77D",
            fill_opacity=0.0,
            stroke_opacity=0.0,
        ).set_z_index(50)
        self.add(self.smog_overlay)

        pan_tracker = ValueTracker(0.0)

        def walk_update(_mob) -> None:
            p = pan_tracker.get_value()
            self.orangutan.set_x(-1.5 + 2.8 * p)
            self.orangutan.set_y(-1.5 + abs(math.sin(p * math.pi * 5.0)) * 0.08)
            self.deer.set_x(2.2 + 3.2 * p)
            self.deer.set_y(-1.45 + abs(math.sin(p * math.pi * 4.5)) * 0.06)
            self.hornbill.set_x(-6.5 + 14.5 * p)
            self.hornbill.set_y(2.2 + 0.45 * math.sin(p * math.pi * 2.0))

        anim_driver = Dot().set_opacity(0.0)
        anim_driver.add_updater(walk_update)
        self.add(anim_driver)

        self.play(
            pan_tracker.animate.set_value(0.55),
            self.particles.smoke_intensity.animate.set_value(1.2),
            self.smog_overlay.animate.set_fill(opacity=0.45),
            run_time=4.2,
            rate_func=rate_functions.smooth,
        )

        self.play(
            pan_tracker.animate.set_value(1.0),
            self.smog_overlay.animate.set_fill(opacity=0.92),
            self.particles.smoke_intensity.animate.set_value(1.6),
            run_time=3.8,
            rate_func=rate_functions.smooth,
        )

        anim_driver.remove_updater(walk_update)
        self.remove(anim_driver)
        self.remove(self.forest_group, self.particles.group, self.animals_group)
        self.wait(0.5)

    # ==================================================================
    # BAGIAN B — DAMPAK KE MANUSIA & ASAP SELURUH KOTA (8.5s - 21.5s)
    # ==================================================================
    def _play_part_b_human_impact(self) -> None:
        self._set_subtitle(1, run_time=0.40)

        # 1. Permukiman Warga (Atap rumah, gedung perkantoran, tiang listrik)
        self.settlement = SVGMobject(str(SETTLEMENT_LAYER_PATH), use_svg_cache=False)
        self.settlement.set_height(config.frame_height).move_to(ORIGIN).set_z_index(5)
        self.add(self.settlement)

        # 2. SISTEM ASAP MENYEBAR DI SELURUH KOTA (CitySmogSystem)
        self.city_smog = CitySmogSystem(self.asset_paths["smoke_puff"], seed=777)
        self.city_smog.group.set_z_index(30)
        self.add(self.city_smog.group)

        # Haze atmosferik kota (ground smog & sky pollution)
        self.city_haze_blanket = Rectangle(
            width=config.frame_width * 1.5,
            height=config.frame_height * 1.5,
            fill_color="#C9A066",
            fill_opacity=0.38,
            stroke_opacity=0.0,
        ).set_z_index(25)
        self.add(self.city_haze_blanket)

        self.play(
            self.smog_overlay.animate.set_fill(opacity=0.15),
            self.city_smog.density.animate.set_value(1.1),
            self.city_haze_blanket.animate.set_fill(opacity=0.48),
            run_time=1.3,
            rate_func=rate_functions.smooth,
        )

        # 3. Stickman Muncul Berjalan di Jalanan Kota yang Berasap
        self.stickman_normal = SVGMobject(str(STICKMAN_NORMAL_PATH), use_svg_cache=False)
        self.stickman_normal.set_height(3.1).move_to([-3.4, -1.35, 0.0]).set_z_index(60)

        self.play(
            FadeIn(self.stickman_normal, shift=RIGHT * 0.4),
            run_time=1.0,
        )

        # Gulungan asap pekat melintas menyapu stickman dan seluruh jalan
        gust_smoke = SVGMobject(str(self.asset_paths["smoke_puff"]), use_svg_cache=False)
        gust_smoke.set_height(3.5).move_to([-4.8, -1.0, 0.0]).set_opacity(0.0).set_z_index(62)
        self.add(gust_smoke)

        self.play(
            gust_smoke.animate.set_opacity(0.75).shift(RIGHT * 2.8).scale(1.2),
            self.city_haze_blanket.animate.set_fill(opacity=0.55),
            run_time=1.1,
        )

        # 4. Stickman Batuk Sesak Hebat (tremor, onomatopoeia Uhuk! Uhuk!, tutup hidung)
        self.stickman_cough = SVGMobject(str(STICKMAN_COUGH_PATH), use_svg_cache=False)
        self.stickman_cough.set_height(3.1).move_to(self.stickman_normal.get_center()).set_z_index(60)

        self.remove(self.stickman_normal)
        self.add(self.stickman_cough)

        cough_tracker = ValueTracker(0.0)
        orig_cough_pos = self.stickman_cough.get_center().copy()

        def cough_shake(_mob) -> None:
            c = cough_tracker.get_value()
            shake_x = 0.08 * math.sin(c * 42.0)
            shake_y = 0.05 * math.sin(c * 32.0)
            self.stickman_cough.move_to(orig_cough_pos + np.array([shake_x, shake_y, 0.0]))

        cough_driver = Dot().set_opacity(0.0)
        cough_driver.add_updater(cough_shake)
        self.add(cough_driver)

        # Onomatopoeia dramatis gaya 'Kok Bisa!'
        cough_text_1 = Text(
            "*Uhuk! Uhuk!*",
            font="Segoe UI",
            font_size=26,
            weight="BOLD",
            color=PALETTE["accent_crimson"],
        ).next_to(self.stickman_cough, UP + LEFT * 0.2, buff=0.15).set_z_index(70)

        cough_text_2 = Text(
            "*Khuk!*",
            font="Segoe UI",
            font_size=20,
            weight="BOLD",
            color=PALETTE["accent_fire"],
        ).next_to(self.stickman_cough, UP + RIGHT * 0.4, buff=0.25).set_z_index(70)

        shock_ring_1 = Circle(radius=0.3, color=PALETTE["accent_crimson"], stroke_width=3).move_to([-3.4, -0.3, 0]).set_z_index(68)
        shock_ring_2 = Circle(radius=0.5, color=PALETTE["accent_fire"], stroke_width=2).move_to([-3.4, -0.3, 0]).set_z_index(68)

        self.play(
            cough_tracker.animate.set_value(1.0),
            FadeIn(cough_text_1, scale=1.35),
            FadeIn(cough_text_2, scale=1.2),
            shock_ring_1.animate.scale(2.2).set_opacity(0.0),
            shock_ring_2.animate.scale(2.5).set_opacity(0.0),
            run_time=1.8,
        )

        cough_driver.remove_updater(cough_shake)
        self.remove(cough_driver)
        self.stickman_cough.move_to(orig_cough_pos)
        self.remove(shock_ring_1, shock_ring_2)

        # 5. Stickman Memakai Masker N95 Pelindung
        self.stickman_masked = SVGMobject(str(STICKMAN_MASKED_PATH), use_svg_cache=False)
        self.stickman_masked.set_height(3.1).move_to(orig_cough_pos).set_z_index(60)

        self.play(
            FadeOut(cough_text_1, scale=0.8),
            FadeOut(cough_text_2, scale=0.8),
            FadeOut(gust_smoke),
            FadeOut(self.stickman_cough),
            FadeIn(self.stickman_masked),
            run_time=0.9,
        )

        # 6. Cut-in Paru-paru & ISPA di Sisi Kanan Layar
        self.lungs_healthy = SVGMobject(str(LUNGS_HEALTHY_PATH), use_svg_cache=False)
        self.lungs_healthy.set_height(3.2).move_to([2.7, -0.2, 0.0]).set_z_index(65)

        med_card = RoundedRectangle(
            corner_radius=0.2,
            width=5.8,
            height=5.2,
            fill_color=PALETTE["card_bg"],
            fill_opacity=0.90,
            stroke_color="#FFFFFF",
            stroke_opacity=0.25,
            stroke_width=1.5,
        ).move_to([2.7, 0.4, 0.0]).set_z_index(63)

        self.play(
            FadeIn(med_card, shift=UP * 0.2),
            FadeIn(self.lungs_healthy, scale=0.9),
            run_time=1.1,
        )

        soot_dots = VGroup(*[
            Dot(point=[2.7 + random.uniform(-0.15, 0.15), 1.6 + i * 0.35, 0.0], radius=0.06, color="#1B1918")
            for i in range(6)
        ]).set_z_index(67)
        self.add(soot_dots)

        self.play(
            soot_dots.animate.shift(DOWN * 1.5),
            run_time=0.9,
            rate_func=rate_functions.ease_in_quad,
        )
        self.remove(soot_dots)

        self.lungs_damaged = SVGMobject(str(LUNGS_DAMAGED_PATH), use_svg_cache=False)
        self.lungs_damaged.set_height(3.2).move_to(self.lungs_healthy.get_center()).set_z_index(65)

        self.play(
            FadeOut(self.lungs_healthy),
            FadeIn(self.lungs_damaged, scale=1.06),
            run_time=1.0,
        )

        # 7. Kartu Peringatan Dramatis "ISPA" Muncul
        self.badge_ispa = SVGMobject(str(BADGE_ISPA_PATH), use_svg_cache=False)
        self.badge_ispa.set_height(2.0).move_to([2.7, 1.8, 0.0]).set_z_index(80)

        self.play(
            self.lungs_damaged.animate.shift(DOWN * 0.75).scale(0.85),
            FadeIn(self.badge_ispa, shift=DOWN * 0.35, scale=1.1),
            run_time=1.3,
            rate_func=rate_functions.ease_out_back,
        )

        self.wait(1.8)

        self.play(
            FadeOut(self.stickman_masked, shift=LEFT * 0.4),
            FadeOut(med_card, shift=RIGHT * 0.4),
            FadeOut(self.lungs_damaged, shift=RIGHT * 0.4),
            FadeOut(self.badge_ispa, shift=RIGHT * 0.4),
            FadeOut(self.settlement),
            FadeOut(self.city_smog.group),
            FadeOut(self.city_haze_blanket),
            self.smog_overlay.animate.set_fill(opacity=0.0),
            run_time=1.2,
        )
        self.remove(self.smog_overlay)

    # ==================================================================
    # BAGIAN C — PETA ASIA TENGGARA DARI GAMBAR USER (ImageMobject) & ASAP ALAMI
    # ==================================================================
    def _play_part_c_transboundary_haze(self) -> None:
        self._set_subtitle(2, run_time=0.40)

        # 1. PETA ASIA TENGGARA JERNIH & PREFESIONAL DARI GAMBAR PENGGUNA
        # Menggunakan ImageMobject resmi Manim agar laut biru, bendera, dan teks tampil 100% sempurna
        self.sea_map = ImageMobject(str(MAP_SEA_PATH))
        self.sea_map.set_height(config.frame_height)
        self.sea_map.move_to(ORIGIN)
        self.sea_map.set_z_index(10)

        self.play(
            FadeIn(self.sea_map, scale=1.05),
            run_time=1.4,
            rate_func=rate_functions.smooth,
        )

        # Konversi koordinat peta (1024 x 577) ke koordinat Manim
        def sea_px_to_manim(px: float, py: float) -> np.ndarray:
            nw, nh = SEA_MAP_SIZE
            mx = (px / nw - 0.5) * self.sea_map.width
            my = (0.5 - py / nh) * self.sea_map.height
            return np.array([mx, my, 0.0])

        # 2. Titik Api Hotspot Satelit Inframerah di Sumatera & Kalimantan
        hotspot_dots = VGroup()
        for hs in HOTSPOTS_SEA_PX:
            pos = sea_px_to_manim(*hs["px"])
            dot = Dot(point=pos, radius=0.08, color="#FF1100")
            pulse_ring = Circle(radius=0.20, color="#FF7700", stroke_width=2.5).move_to(pos)
            hotspot_dots.add(dot, pulse_ring)
        hotspot_dots.set_z_index(15)

        self.play(
            FadeIn(hotspot_dots),
            run_time=0.8,
        )

        # 3. SIMULASI ASAP LINTAS NEGARA YANG SANGAT NATURAL & REALISTIS
        # - Stream 1: Dari Sumatera (Riau/Jambi) menyeberangi Selat Malaka -> MENYELIMUTI SINGAPURA & KUALA LUMPUR
        # - Stream 2: Dari Kalimantan (Palangka Raya/Ketapang) -> MENYELIMUTI KUCHING (SARAWAK) & BRUNEI DARUSSALAM
        transboundary_smoke = VGroup()

        # Plume Sumatera -> Selat Malaka -> Singapura & Semenanjung Malaysia
        sumatra_plume_steps = [
            (165.0, 425.0, 0.9, 0.72),  # Titik api Riau / Sumatera Tengah
            (195.0, 415.0, 1.3, 0.68),  # Masuk ke Selat Malaka
            (235.0, 400.0, 1.7, 0.70),  # MENYELIMUTI SINGAPURA SECARA PEKAT
            (185.0, 360.0, 2.0, 0.64),  # MENYELIMUTI KUALA LUMPUR / SELANGOR
            (160.0, 330.0, 2.3, 0.55),  # Meluas ke Perak & Penang
        ]
        for px, py, sz, op in sumatra_plume_steps:
            puff = SVGMobject(str(self.asset_paths["smoke_puff"]), use_svg_cache=False)
            puff.set_height(sz).move_to(sea_px_to_manim(px, py)).set_opacity(0.0)
            transboundary_smoke.add(puff)

        # Plume Kalimantan -> Sarawak -> Brunei Darussalam
        kalimantan_plume_steps = [
            (440.0, 440.0, 0.9, 0.72),  # Asal api Palangka Raya (Kalteng)
            (420.0, 405.0, 1.3, 0.68),  # Melintasi perbatasan Kalteng - Sarawak
            (410.0, 375.0, 1.7, 0.66),  # MENYELIMUTI KUCHING / SARAWAK
            (445.0, 360.0, 1.9, 0.62),  # Pesisir barat laut Kalimantan
            (470.0, 350.0, 2.1, 0.65),  # MENYELIMUTI BRUNEI DARUSSALAM
            (485.0, 320.0, 2.4, 0.52),  # Meluas ke Laut Cina Selatan
        ]
        for px, py, sz, op in kalimantan_plume_steps:
            puff = SVGMobject(str(self.asset_paths["smoke_puff"]), use_svg_cache=False)
            puff.set_height(sz).move_to(sea_px_to_manim(px, py)).set_opacity(0.0)
            transboundary_smoke.add(puff)

        transboundary_smoke.set_z_index(22)

        # Garis aliran angin muson melengkung halus (Monsoon Wind Streamlines)
        wind_arrows = VGroup(
            CurvedArrow(
                sea_px_to_manim(175.0, 445.0),
                sea_px_to_manim(235.0, 400.0),
                angle=-math.pi / 5,
                color=PALETTE["warning_yellow"],
                stroke_width=3.2,
            ),
            CurvedArrow(
                sea_px_to_manim(235.0, 400.0),
                sea_px_to_manim(185.0, 360.0),
                angle=math.pi / 4.5,
                color=PALETTE["warning_yellow"],
                stroke_width=3.2,
            ),
            CurvedArrow(
                sea_px_to_manim(440.0, 440.0),
                sea_px_to_manim(410.0, 375.0),
                angle=-math.pi / 6,
                color=PALETTE["warning_yellow"],
                stroke_width=3.2,
            ),
            CurvedArrow(
                sea_px_to_manim(410.0, 375.0),
                sea_px_to_manim(470.0, 350.0),
                angle=-math.pi / 5,
                color=PALETTE["warning_yellow"],
                stroke_width=3.2,
            ),
        ).set_z_index(24)

        # Lapisan haze regional transparan menyelimuti Selat Malaka & Laut Cina Selatan
        regional_haze = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color="#D4C5A9",
            fill_opacity=0.0,
            stroke_opacity=0.0,
        ).set_z_index(20)
        self.add(regional_haze)

        # Animasi aliran asap mengepul meluas secara organik
        self.play(
            LaggedStart(*[arr.animate.set_opacity(0.85) for arr in wind_arrows], lag_ratio=0.2),
            LaggedStart(*[puff.animate.set_opacity(0.68).scale(1.15) for puff in transboundary_smoke], lag_ratio=0.15),
            regional_haze.animate.set_fill(opacity=0.28),
            run_time=2.8,
            rate_func=rate_functions.smooth,
        )

        # 4. Badge Peringatan Bahaya (AQI / IPU) Muncul di Singapura, Malaysia, & Brunei
        alert_badges = VGroup()
        for tgt in TARGET_COUNTRIES_SEA_PX:
            pos = sea_px_to_manim(*tgt["px"])
            card = RoundedRectangle(
                corner_radius=0.12,
                width=2.5,
                height=0.85,
                fill_color=PALETTE["card_bg"],
                fill_opacity=0.94,
                stroke_color=tgt["alert_color"],
                stroke_width=1.8,
            )
            txt_title = Text(
                f"{tgt['country']}",
                font="Segoe UI",
                font_size=12,
                weight="BOLD",
                color=PALETTE["text_light"],
            )
            txt_status = Text(
                f"{tgt['status']} ({tgt['desc']})",
                font="Segoe UI",
                font_size=10,
                color=tgt["alert_color"],
            )
            txt_group = VGroup(txt_title, txt_status).arrange(DOWN, buff=0.08)
            card_group = VGroup(card, txt_group)
            txt_group.move_to(card.get_center())

            offset = UP * 0.80 + (RIGHT * 0.55 if pos[0] > 0 else LEFT * 0.4)
            card_group.move_to(pos + offset)
            alert_badges.add(card_group)

        alert_badges.set_z_index(35)

        self.play(
            LaggedStart(*[FadeIn(b, shift=UP * 0.25) for b in alert_badges], lag_ratio=0.25),
            run_time=2.0,
        )

        self.wait(1.5)

        # 5. Transisi ke Panggung Konferensi Diplomatik / Protes Antarnegara
        self.conference = SVGMobject(str(CONFERENCE_SUMMIT_PATH), use_svg_cache=False)
        self.conference.set_height(6.5).move_to(ORIGIN).set_z_index(50)

        self.play(
            FadeOut(self.sea_map),
            FadeOut(hotspot_dots),
            FadeOut(wind_arrows),
            FadeOut(transboundary_smoke),
            FadeOut(alert_badges),
            FadeOut(regional_haze),
            FadeIn(self.conference, scale=0.92),
            run_time=1.8,
            rate_func=rate_functions.smooth,
        )

        # Kamera subtle zoom-in fokus ke podium diplomat
        self.play(
            self.camera.frame.animate.scale(0.92).shift(DOWN * 0.15),
            run_time=2.5,
            rate_func=rate_functions.smooth,
        )

        self.wait(1.2)
        self._clear_subtitle(run_time=0.5)
        self.wait(0.5)
