"""Scene 5 — Dampak Pertama: Kerusakan Hutan (Kalimantan).

Animasi edukasi 2D bergaya editorial ("Kok Bisa!") murni berbasis vektor SVG
menggunakan Manim + Pycairo (cairo.SVGSurface) tanpa ketergantungan Pillow.
Alur visual disinkronkan dengan naskah dubbing (tanpa audio terlebih dahulu):
  1. Peta Indonesia (SVG vektor) muncul kembali di kanvas editorial.
  2. Kamera zoom halus ke Pulau Kalimantan dengan titik hotspot kebakaran.
  3. Transisi kabut/cahaya mulus masuk ke hutan hujan tropis Kalimantan (peta hilang total);
     api menyala dan melalap pepohonan serta lahan gambut hijau menjadi hangus dan berasap.
  4. Panning parallax ke tepi hutan hangus: satwa liar endemik (Orangutan, Enggang, Rusa)
     berjalan dan terbang maju menjauhi kebakaran.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

# Pastikan impor berfungsi baik saat dijalankan via `python main.py` maupun `manim src/scene5_kerusakan_hutan.py`
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MovingCameraScene,
    Rectangle,
    RoundedRectangle,
    SVGMobject,
    Text,
    UpdateFromAlphaFunc,
    VGroup,
    ValueTracker,
    config,
    rate_functions,
)

from src.cairo_assets import PANORAMA_H, PANORAMA_W, ensure_all_assets
from src.config import (
    DUBBING_SEGMENTS,
    KALIMANTAN_HOTSPOTS_PX,
    KALIMANTAN_PIXEL_CENTER,
    MAP_PIXEL_SIZE,
    MAP_SVG_PATH,
    PALETTE,
    SHOW_SUBTITLES,
    SVG_DIR,
)

PANORAMA_SCENE_HEIGHT = 8.0
PANORAMA_SCENE_WIDTH = PANORAMA_SCENE_HEIGHT * (PANORAMA_W / PANORAMA_H)


def smooth_step(t: float) -> float:
    """Kurva interpolasi kubik halus [0, 1] -> [0, 1]."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def cache_original_opacities(mob: VGroup) -> None:
    """Menyimpan fill_opacity & stroke_opacity asli setiap sub-path SVG."""
    for sub in mob.family_members_with_points():
        if not hasattr(sub, "_orig_fill_op"):
            sub._orig_fill_op = float(sub.fill_opacity)
            sub._orig_stroke_op = float(sub.stroke_opacity)


def set_scaled_opacity(mob: VGroup, factor: float) -> None:
    """Mengatur opasitas relatif terhadap nilai asli tiap sub-path (menjaga transparansi berlapis)."""
    f = max(0.0, min(1.0, float(factor)))
    for sub in mob.family_members_with_points():
        if not hasattr(sub, "_orig_fill_op"):
            sub._orig_fill_op = float(sub.fill_opacity)
            sub._orig_stroke_op = float(sub.stroke_opacity)
        sub.set_fill(opacity=sub._orig_fill_op * f)
        sub.set_stroke(opacity=sub._orig_stroke_op * f)


def map_pixel_to_local(px: float, py: float, map_mobject: SVGMobject) -> np.ndarray:
    """Konversi koordinat viewBox SVG peta (1024x359) ke koordinat lokal Manim."""
    img_w, img_h = MAP_PIXEL_SIZE
    nx = (px / img_w) - 0.5
    ny = 0.5 - (py / img_h)
    center = map_mobject.get_center()
    return np.array(
        [
            center[0] + nx * map_mobject.width,
            center[1] + ny * map_mobject.height,
            0.0,
        ]
    )


def build_subtitle_pill(text: str) -> VGroup:
    """Membuat kartu subtitle editorial bersih di bagian bawah layar."""
    label = Text(
        text,
        font="Segoe UI",
        font_size=21,
        color=PALETTE["text_light"],
        line_spacing=1.25,
    )
    pad_x, pad_y = 0.65, 0.30
    pill = RoundedRectangle(
        corner_radius=0.18,
        width=min(config.frame_width - 1.2, label.width + pad_x),
        height=label.height + pad_y,
        fill_color=PALETTE["card_bg"],
        fill_opacity=0.84,
        stroke_color="#FFFFFF",
        stroke_opacity=0.18,
        stroke_width=1.2,
    )
    if label.width > pill.width - 0.35:
        label.scale_to_fit_width(pill.width - 0.35)
    label.move_to(pill.get_center())
    group = VGroup(pill, label)
    group.to_edge(DOWN, buff=0.28)
    group.set_z_index(100)
    return group


class FireSmokeParticleSystem:
    """Sistem partikel api, asap tebal, bara api, dan serpihan abu berbasis vektor SVG."""

    def __init__(self, asset_paths: dict[str, Path], seed: int = 77) -> None:
        self.rng = random.Random(seed)
        self.asset_paths = asset_paths

        self.fire_intensity = ValueTracker(0.0)
        self.smoke_intensity = ValueTracker(0.0)
        self.ash_intensity = ValueTracker(0.0)
        self.pan_offset = ValueTracker(0.0)
        self.clock = ValueTracker(0.0)

        self.flames: list[tuple[SVGMobject, dict]] = []
        self.smokes: list[tuple[SVGMobject, dict]] = []
        self.embers: list[tuple[SVGMobject, dict]] = []
        self.ashes: list[tuple[SVGMobject, dict]] = []

        self.group = VGroup()
        self._init_particles()
        self._bind_updater()

    def _init_particles(self) -> None:
        # Muat template SVG sekali saja lalu .copy() agar inisialisasi cepat
        flame_tpls = [
            SVGMobject(str(self.asset_paths[f"flame_{i}"]), use_svg_cache=False) for i in range(3)
        ]
        smoke_tpl = SVGMobject(str(self.asset_paths["smoke_puff"]), use_svg_cache=False)
        ember_tpl = SVGMobject(str(self.asset_paths["ember_spark"]), use_svg_cache=False)
        ash_tpl = SVGMobject(str(self.asset_paths["ash_flake"]), use_svg_cache=False)

        for tpl in [*flame_tpls, smoke_tpl, ember_tpl, ash_tpl]:
            cache_original_opacities(tpl)

        # 1. Lidah api di lantai gambut & pangkal pohon
        flame_anchors = [
            (-9.2, -2.55, 1.45),
            (-8.1, -2.50, 1.95),
            (-7.0, -2.58, 1.55),
            (-5.8, -2.45, 2.20),
            (-4.7, -2.55, 1.75),
            (-3.6, -2.42, 2.25),
            (-2.4, -2.55, 1.65),
            (-1.3, -2.48, 2.05),
            (-0.2, -2.56, 1.55),
            (0.9, -2.52, 1.85),
            (2.0, -2.55, 1.65),
            (3.0, -2.56, 1.45),
            (4.0, -2.58, 1.15),
            (-5.5, -1.75, 1.15),
            (-1.3, -1.65, 1.10),
        ]
        for idx, (bx, by, base_h) in enumerate(flame_anchors):
            spr = flame_tpls[idx % 3].copy()
            spr.set_height(base_h)
            base_w = spr.width
            spr.move_to([bx, by + base_h * 0.35, 0])
            set_scaled_opacity(spr, 0.0)
            spr.set_z_index(18)
            meta = {
                "base_x": bx,
                "base_y": by,
                "base_h": base_h,
                "base_w": base_w,
                "phase": self.rng.uniform(0, math.tau),
                "speed": self.rng.uniform(4.8, 7.5),
                "delay": idx * 0.04,
            }
            self.flames.append((spr, meta))
            self.group.add(spr)

        # 2. Gumpalan asap tebal naik & tertiup angin ke kanan
        for i in range(20):
            spr = smoke_tpl.copy()
            spr.set_height(2.4)
            set_scaled_opacity(spr, 0.0)
            spr.set_z_index(24)
            meta = {
                "origin_x": self.rng.uniform(-8.5, 4.2),
                "origin_y": self.rng.uniform(-2.1, -0.4),
                "cycle": self.rng.uniform(3.4, 5.2),
                "offset": i / 20.0,
                "drift_x": self.rng.uniform(2.8, 5.2),
                "rise_y": self.rng.uniform(4.2, 6.2),
                "max_scale": self.rng.uniform(2.4, 3.9),
                "max_alpha": self.rng.uniform(0.45, 0.72),
            }
            self.smokes.append((spr, meta))
            self.group.add(spr)

        # 3. Bara api (ember sparks) melayang naik diagonal
        for i in range(22):
            spr = ember_tpl.copy()
            spr.set_height(self.rng.uniform(0.14, 0.28))
            set_scaled_opacity(spr, 0.0)
            spr.set_z_index(22)
            meta = {
                "origin_x": self.rng.uniform(-8.0, 5.0),
                "origin_y": self.rng.uniform(-2.8, -0.8),
                "cycle": self.rng.uniform(2.0, 3.6),
                "offset": i / 22.0,
                "drift_x": self.rng.uniform(2.2, 4.6),
                "rise_y": self.rng.uniform(3.8, 6.0),
                "wobble": self.rng.uniform(2.0, 4.5),
                "base_h": spr.height,
            }
            self.embers.append((spr, meta))
            self.group.add(spr)

        # 4. Serpihan abu melayang di fase hilangnya habitat
        for i in range(18):
            spr = ash_tpl.copy()
            spr.set_height(self.rng.uniform(0.10, 0.18))
            set_scaled_opacity(spr, 0.0)
            spr.set_z_index(26)
            meta = {
                "origin_x": self.rng.uniform(-4.5, 11.0),
                "origin_y": self.rng.uniform(1.8, 4.2),
                "cycle": self.rng.uniform(4.0, 6.5),
                "offset": i / 18.0,
                "drift_x": self.rng.uniform(1.2, 2.8),
                "fall_y": self.rng.uniform(4.5, 6.8),
                "wobble": self.rng.uniform(1.5, 3.0),
            }
            self.ashes.append((spr, meta))
            self.group.add(spr)

    def _bind_updater(self) -> None:
        def update_particles(_mob, dt: float) -> None:
            self.clock.increment_value(dt)
            t = self.clock.get_value()
            fire_lvl = self.fire_intensity.get_value()
            smoke_lvl = self.smoke_intensity.get_value()
            ash_lvl = self.ash_intensity.get_value()
            px_shift = self.pan_offset.get_value()

            for spr, meta in self.flames:
                local_lvl = smooth_step((fire_lvl - meta["delay"]) / max(0.2, 1.0 - meta["delay"]))
                if local_lvl <= 0.01:
                    set_scaled_opacity(spr, 0.0)
                    continue
                flicker = 0.86 + 0.16 * math.sin(t * meta["speed"] + meta["phase"])
                flicker_x = 0.92 + 0.10 * math.cos(t * meta["speed"] * 1.3 + meta["phase"])
                h = max(0.05, meta["base_h"] * local_lvl * flicker)
                w = max(0.04, meta["base_w"] * local_lvl * flicker_x)
                spr.stretch_to_fit_height(h)
                spr.stretch_to_fit_width(w)
                sway_x = 0.06 * math.sin(t * 4.2 + meta["phase"])
                spr.move_to([meta["base_x"] - px_shift + sway_x, meta["base_y"] + h * 0.40, 0.0])
                set_scaled_opacity(spr, min(0.96, 0.90 * local_lvl))

            for spr, meta in self.smokes:
                if smoke_lvl <= 0.01:
                    set_scaled_opacity(spr, 0.0)
                    continue
                life = ((t / meta["cycle"]) + meta["offset"]) % 1.0
                fade_envelope = math.sin(life * math.pi)
                scale_h = 0.9 + meta["max_scale"] * (life**0.75)
                spr.set_height(scale_h)
                x = meta["origin_x"] - px_shift * 0.88 + meta["drift_x"] * life
                y = meta["origin_y"] + meta["rise_y"] * (life**0.85)
                spr.move_to([x, y, 0.0])
                set_scaled_opacity(spr, meta["max_alpha"] * fade_envelope * smoke_lvl)

            for spr, meta in self.embers:
                if fire_lvl <= 0.02 and smoke_lvl <= 0.02:
                    set_scaled_opacity(spr, 0.0)
                    continue
                lvl = max(fire_lvl, smoke_lvl * 0.6)
                life = ((t / meta["cycle"]) + meta["offset"]) % 1.0
                envelope = math.sin(life * math.pi)
                wobble_x = 0.25 * math.sin(t * meta["wobble"] + meta["offset"] * 12.0)
                spr.set_height(meta["base_h"] * (0.7 + 0.5 * (1.0 - life)))
                x = meta["origin_x"] - px_shift * 0.95 + meta["drift_x"] * life + wobble_x
                y = meta["origin_y"] + meta["rise_y"] * life
                spr.move_to([x, y, 0.0])
                set_scaled_opacity(spr, 0.95 * envelope * lvl)

            for spr, meta in self.ashes:
                if ash_lvl <= 0.01:
                    set_scaled_opacity(spr, 0.0)
                    continue
                life = ((t / meta["cycle"]) + meta["offset"]) % 1.0
                envelope = math.sin(life * math.pi)
                wobble_x = 0.22 * math.sin(t * meta["wobble"] + meta["offset"] * 9.0)
                x = meta["origin_x"] - px_shift + meta["drift_x"] * life + wobble_x
                y = meta["origin_y"] - meta["fall_y"] * life
                spr.move_to([x, y, 0.0])
                set_scaled_opacity(spr, 0.82 * envelope * ash_lvl)

        self.group.add_updater(update_particles)


class Scene5KerusakanHutan(MovingCameraScene):
    """Scene 5 — Dampak Pertama: Kerusakan Hutan (Kalimantan)."""

    def construct(self) -> None:
        self.asset_paths = ensure_all_assets(force=False)
        self.camera.background_color = PALETTE["bg_cream"]

        self._subtitle_mob: VGroup | None = None
        self._play_beat_1_map_appear()
        self._play_beat_2_zoom_kalimantan()
        self._play_beat_3_forest_and_fire()
        self._play_beat_4_wildlife_habitat_loss()

    # ------------------------------------------------------------------
    # Utilitas Subtitle Panduan Dubbing
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

    # ------------------------------------------------------------------
    # BEAT 1: Peta Indonesia Muncul Kembali (~5.8 detik)
    # ------------------------------------------------------------------
    def _play_beat_1_map_appear(self) -> None:
        # Latar peta editorial Pycairo SVG
        self.map_backdrop = SVGMobject(str(self.asset_paths["map_backdrop"]), use_svg_cache=False)
        self.map_backdrop.set_height(config.frame_height)
        self.map_backdrop.set_z_index(0)
        cache_original_opacities(self.map_backdrop)

        # Peta Indonesia versi vektor SVG murni (tanpa Pillow)
        self.indonesia_map = SVGMobject(str(MAP_SVG_PATH), use_svg_cache=False)
        self.indonesia_map.set_width(12.4)
        self.indonesia_map.move_to(UP * 0.18)
        self.indonesia_map.set_z_index(2)
        cache_original_opacities(self.indonesia_map)

        # Lencana judul bab bergaya "Kok Bisa!"
        chapter_tag = Text(
            "DAMPAK PERTAMA  •  KERUSAKAN HUTAN",
            font="Segoe UI",
            weight="BOLD",
            font_size=20,
            color=PALETTE["text_light"],
        )
        chapter_bg = RoundedRectangle(
            corner_radius=0.18,
            width=chapter_tag.width + 0.7,
            height=chapter_tag.height + 0.34,
            fill_color=PALETTE["accent_emerald"],
            fill_opacity=0.95,
            stroke_width=0,
        )
        chapter_tag.move_to(chapter_bg.get_center())
        self.chapter_badge = VGroup(chapter_bg, chapter_tag).to_edge(UP, buff=0.35)
        self.chapter_badge.set_z_index(40)

        # Animasi masuk halus (satu animasi per mobject agar opacity & scale tidak bentrok)
        set_scaled_opacity(self.map_backdrop, 0.0)
        self.add(self.map_backdrop)
        self.play(
            UpdateFromAlphaFunc(self.map_backdrop, lambda m, a: set_scaled_opacity(m, a)),
            FadeIn(self.indonesia_map, scale=0.92),
            FadeIn(self.chapter_badge, shift=DOWN * 0.18),
            run_time=1.4,
            rate_func=rate_functions.smooth,
        )

        # Subtitle segmen 1
        self._set_subtitle(0, run_time=0.45)

        # Titik-titik hotspot SVG mulai menyala halus di Kalimantan
        hotspot_tpl = SVGMobject(str(self.asset_paths["hotspot_glow"]), use_svg_cache=False)
        cache_original_opacities(hotspot_tpl)

        self.map_hotspots = VGroup()
        for px, py in KALIMANTAN_HOTSPOTS_PX:
            pos = map_pixel_to_local(px, py, self.indonesia_map)
            glow = hotspot_tpl.copy()
            glow.set_height(0.46)
            glow.move_to(pos)
            set_scaled_opacity(glow, 0.0)
            glow.set_z_index(5)
            self.map_hotspots.add(glow)

        self.add(self.map_hotspots)
        self.play(
            LaggedStart(
                *[
                    UpdateFromAlphaFunc(g, lambda m, a: set_scaled_opacity(m, 0.92 * a))
                    for g in self.map_hotspots
                ],
                lag_ratio=0.18,
            ),
            run_time=2.0,
            rate_func=rate_functions.smooth,
        )

        self.play(
            *[g.animate.scale(1.25) for g in self.map_hotspots],
            run_time=1.35,
            rate_func=rate_functions.there_and_back,
        )

    # ------------------------------------------------------------------
    # BEAT 2: Kamera Zoom Halus ke Pulau Kalimantan (~8.2 detik)
    # ------------------------------------------------------------------
    def _play_beat_2_zoom_kalimantan(self) -> None:
        self._set_subtitle(1, run_time=0.45)

        kalimantan_center = map_pixel_to_local(
            KALIMANTAN_PIXEL_CENTER[0],
            KALIMANTAN_PIXEL_CENTER[1],
            self.indonesia_map,
        )
        self.map_stage = VGroup(self.map_backdrop, self.indonesia_map, self.map_hotspots)

        # Lingkaran penanda & label callout Kalimantan
        ring_outer = Circle(
            radius=1.85,
            color=PALETTE["accent_fire"],
            stroke_width=3.2,
            stroke_opacity=0.85,
        ).move_to(UP * 0.20)
        ring_inner = Circle(
            radius=1.55,
            color=PALETTE["accent_amber"],
            stroke_width=1.8,
            stroke_opacity=0.55,
        ).move_to(UP * 0.20)
        ring_group = VGroup(ring_outer, ring_inner).set_z_index(12)

        anchor_dot = Dot(point=np.array([0.85, 0.95, 0.0]), radius=0.07, color=PALETTE["accent_fire"])
        pointer_line = Line(
            anchor_dot.get_center(),
            np.array([2.25, 1.55, 0.0]),
            color=PALETTE["ink_dark"],
            stroke_width=2.4,
        )
        title_txt = Text("KALIMANTAN", font="Segoe UI", weight="BOLD", font_size=28, color=PALETTE["ink_dark"])
        sub_txt = Text(
            "Hutan Tropis & Lahan Gambut",
            font="Segoe UI",
            font_size=18,
            color=PALETTE["accent_emerald"],
        )
        text_stack = VGroup(title_txt, sub_txt).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        card = RoundedRectangle(
            corner_radius=0.16,
            width=text_stack.width + 0.55,
            height=text_stack.height + 0.36,
            fill_color="#FFFFFF",
            fill_opacity=0.95,
            stroke_color=PALETTE["accent_emerald"],
            stroke_width=2.0,
        )
        card.next_to(pointer_line.get_end(), RIGHT, buff=0.0).shift(UP * 0.05)
        text_stack.move_to(card.get_center())
        callout = VGroup(anchor_dot, pointer_line, card, text_stack).set_z_index(20)

        # Zoom smooth ke Pulau Kalimantan
        zoom_factor = 3.15
        self.play(
            self.map_stage.animate.scale(zoom_factor, about_point=kalimantan_center).shift(
                (UP * 0.22) - kalimantan_center
            ),
            FadeOut(self.chapter_badge, shift=UP * 0.25),
            run_time=2.6,
            rate_func=rate_functions.smooth,
        )

        self.play(
            FadeIn(ring_group, scale=0.88),
            FadeIn(callout, shift=LEFT * 0.2),
            run_time=0.95,
            rate_func=rate_functions.smooth,
        )

        self.play(
            *[g.animate.scale(1.38) for g in self.map_hotspots],
            ring_outer.animate.scale(1.07).set_stroke(opacity=0.55),
            run_time=1.5,
            rate_func=rate_functions.there_and_back,
        )
        self.wait(0.45)

        self.kalimantan_overlay = VGroup(ring_group, callout)

    # ------------------------------------------------------------------
    # BEAT 3: Transisi Kabut Halus ke Hutan -> Terbakar & Berasap (~9.5 detik)
    # ------------------------------------------------------------------
    def _build_forest_stage(self) -> None:
        """Menyiapkan seluruh layer vektor hutan sehat & terbakar sejajar piksel."""
        initial_world_offset = 4.4

        def make_svg_layer(key: str, z: int) -> SVGMobject:
            mob = SVGMobject(str(self.asset_paths[key]), use_svg_cache=False)
            mob.set_height(PANORAMA_SCENE_HEIGHT)
            mob.move_to(RIGHT * initial_world_offset)
            mob.set_z_index(z)
            cache_original_opacities(mob)
            return mob

        # Latar gradien langit halus native Manim (mulus tanpa banding)
        self.sky_bg_healthy = Rectangle(
            width=PANORAMA_SCENE_WIDTH,
            height=PANORAMA_SCENE_HEIGHT,
            stroke_width=0,
        )
        self.sky_bg_healthy.set_fill(color=["#6EB6D9", "#F7E9CA"], opacity=1.0)
        self.sky_bg_healthy.move_to(RIGHT * initial_world_offset).set_z_index(0)

        self.sky_bg_burning = Rectangle(
            width=PANORAMA_SCENE_WIDTH,
            height=PANORAMA_SCENE_HEIGHT,
            stroke_width=0,
        )
        self.sky_bg_burning.set_fill(color=["#1E1B22", "#8A2E12", "#D95D1E"], opacity=1.0)
        self.sky_bg_burning.move_to(RIGHT * initial_world_offset).set_z_index(1)

        self.sky_healthy = make_svg_layer("sky_healthy", z=2)
        self.sky_burning = make_svg_layer("sky_burning", z=3)

        self.far_healthy = make_svg_layer("forest_far_healthy", z=4)
        self.far_burning = make_svg_layer("forest_far_burnt", z=5)

        self.mid_healthy = make_svg_layer("forest_mid_healthy", z=8)
        self.mid_burning = make_svg_layer("forest_mid_burnt", z=9)

        self.fg_healthy = make_svg_layer("forest_fg_healthy", z=14)
        self.fg_burning = make_svg_layer("forest_fg_burnt", z=15)

        # Setel seluruh layer terbakar ke opasitas 0 saat awal masuk hutan sehat
        self.sky_bg_burning.set_fill(opacity=0.0)
        for burning_mob in (self.sky_burning, self.far_burning, self.mid_burning, self.fg_burning):
            set_scaled_opacity(burning_mob, 0.0)

    def _play_beat_3_forest_and_fire(self) -> None:
        # Tabir kabut atmosfer lembut penuh layar (tanpa tepi oval tajam)
        mist_bg = Rectangle(
            width=config.frame_width + 1.0,
            height=config.frame_height + 1.0,
            stroke_width=0,
        )
        mist_bg.set_fill(color=["#DCECE2", "#F7F3E6"], opacity=1.0)
        mist_bg.set_z_index(45)

        self.play(
            FadeOut(self.map_stage, scale=1.75),
            FadeOut(self.kalimantan_overlay, scale=1.18),
            FadeIn(mist_bg),
            run_time=0.95,
            rate_func=rate_functions.smooth,
        )

        # Hapus seluruh objek peta SECARA TOTAL sebelum memunculkan hutan!
        self.remove(self.map_stage, self.kalimantan_overlay)

        # Siapkan panggung hutan di balik tabir kabut
        self._build_forest_stage()
        healthy_group = VGroup(
            self.sky_bg_healthy,
            self.sky_healthy,
            self.far_healthy,
            self.mid_healthy,
            self.fg_healthy,
        )
        healthy_group.scale(1.06)

        self.add(
            self.sky_bg_healthy,
            self.sky_bg_burning,
            self.sky_healthy,
            self.sky_burning,
            self.far_healthy,
            self.far_burning,
            self.mid_healthy,
            self.mid_burning,
            self.fg_healthy,
            self.fg_burning,
        )
        self.bring_to_front(mist_bg)
        if self._subtitle_mob is not None:
            self.bring_to_front(self._subtitle_mob)

        # Kabut menyibak halus memperlihatkan hutan tropis Kalimantan yang cerah
        self.play(
            FadeOut(mist_bg),
            healthy_group.animate.scale(1.0 / 1.06),
            run_time=1.15,
            rate_func=rate_functions.smooth,
        )
        self.remove(mist_bg)

        # Subtitle segmen 3
        self._set_subtitle(2, run_time=0.45)

        # Panning ringan hutan hijau yang asri sebelum api menyala
        self.play(
            self.far_healthy.animate.shift(LEFT * 0.25),
            self.far_burning.animate.shift(LEFT * 0.25),
            self.mid_healthy.animate.shift(LEFT * 0.50),
            self.mid_burning.animate.shift(LEFT * 0.50),
            self.fg_healthy.animate.shift(LEFT * 0.75),
            self.fg_burning.animate.shift(LEFT * 0.75),
            run_time=1.6,
            rate_func=rate_functions.smooth,
        )

        # Aktifkan sistem partikel api & asap SVG
        self.particles = FireSmokeParticleSystem(self.asset_paths)
        self.add(self.particles.group)

        # Fase 1 Kebakaran: percikan bara & api mulai menyala dari lahan gambut
        self.play(
            self.particles.fire_intensity.animate.set_value(0.55),
            self.particles.smoke_intensity.animate.set_value(0.35),
            self.sky_bg_burning.animate.set_fill(opacity=0.45),
            UpdateFromAlphaFunc(self.sky_burning, lambda m, a: set_scaled_opacity(m, 0.45 * a)),
            UpdateFromAlphaFunc(self.fg_burning, lambda m, a: set_scaled_opacity(m, 0.55 * a)),
            run_time=1.7,
            rate_func=rate_functions.smooth,
        )

        # Fase 2 Kebakaran: seluruh hutan hangus terbakar & berasap tebal
        self.play(
            self.particles.fire_intensity.animate.set_value(1.0),
            self.particles.smoke_intensity.animate.set_value(1.0),
            self.sky_bg_burning.animate.set_fill(opacity=1.0),
            self.sky_bg_healthy.animate.set_fill(opacity=0.0),
            UpdateFromAlphaFunc(self.sky_burning, lambda m, a: set_scaled_opacity(m, 0.45 + 0.55 * a)),
            UpdateFromAlphaFunc(self.sky_healthy, lambda m, a: set_scaled_opacity(m, 1.0 - a)),
            UpdateFromAlphaFunc(self.far_burning, lambda m, a: set_scaled_opacity(m, a)),
            UpdateFromAlphaFunc(self.far_healthy, lambda m, a: set_scaled_opacity(m, 1.0 - a)),
            UpdateFromAlphaFunc(self.mid_burning, lambda m, a: set_scaled_opacity(m, a)),
            UpdateFromAlphaFunc(self.mid_healthy, lambda m, a: set_scaled_opacity(m, max(0.0, 1.0 - a * 1.35))),
            UpdateFromAlphaFunc(self.fg_burning, lambda m, a: set_scaled_opacity(m, 0.55 + 0.45 * a)),
            UpdateFromAlphaFunc(self.fg_healthy, lambda m, a: set_scaled_opacity(m, 1.0 - a)),
            run_time=2.5,
            rate_func=rate_functions.smooth,
        )

        self.wait(1.1)

    # ------------------------------------------------------------------
    # BEAT 4: Transisi Halus ke Ilustrasi Satwa Kehilangan Habitatnya (~10 detik)
    # ------------------------------------------------------------------
    def _play_beat_4_wildlife_habitat_loss(self) -> None:
        self._set_subtitle(3, run_time=0.45)

        # Hapus layer sehat agar komposisi ringan & bersih
        self.remove(
            self.sky_bg_healthy,
            self.sky_healthy,
            self.far_healthy,
            self.mid_healthy,
            self.fg_healthy,
        )

        # Muat aset satwa liar 2D SVG (semua menghadap MAJU ke kanan menjauhi api)
        orangutan = SVGMobject(str(SVG_DIR / "orangutan.svg"), use_svg_cache=False)
        orangutan.set_height(2.35)   # lebih besar agar terlihat jelas
        orangutan.set_z_index(17)

        deer = SVGMobject(str(SVG_DIR / "deer.svg"), use_svg_cache=False)
        deer.set_height(2.05)        # lebih besar
        deer.set_z_index(16)

        hornbill = SVGMobject(str(SVG_DIR / "hornbill.svg"), use_svg_cache=False)
        hornbill.set_height(1.65)    # lebih besar, terlihat lebih dramatis
        hornbill.set_z_index(21)

        # Hornbill: pisahkan sayap belakang, depan, dan badan
        # (gunakan range aman agar tidak IndexError jika SVG punya lebih/kurang submobject)
        n_subs = len(hornbill)
        if n_subs >= 13:
            hb_back_wing = VGroup(hornbill[0], hornbill[1])
            hb_front_wing = VGroup(hornbill[11], hornbill[12])
            hb_body = VGroup(*[hornbill[i] for i in range(2, 11)])
        else:
            # fallback: treat whole hornbill as body, no wing flap
            hb_back_wing = VGroup()
            hb_front_wing = VGroup()
            hb_body = hornbill

        # Posisi awal: orangutan & rusa di depan (kanan) layer foreground; hornbill masuk dari KANAN atas
        # (menjauhi api ke kiri → terbang ke kiri, karena api ada di kiri bawah dan langit di kanan lebih cerah)
        # Revisi: hornbill terbang dari kiri ke kanan (menjauhi api yang ada di latar belakang kiri)
        orangutan.move_to(np.array([5.5, -1.42, 0.0]))
        deer.move_to(np.array([9.2, -1.46, 0.0]))
        hornbill.move_to(np.array([-9.5, 2.15, 0.0]))  # mulai dari luar layar kiri atas, terbang ke kanan

        self.add(orangutan, deer, hornbill)

        pan_progress = ValueTracker(0.0)
        sky_bg_start_x = self.sky_bg_burning.get_x()
        sky_start_x = self.sky_burning.get_x()
        far_start_x = self.far_burning.get_x()
        mid_start_x = self.mid_burning.get_x()
        fg_start_x = self.fg_burning.get_x()

        orang_start = orangutan.get_center().copy()
        deer_start = deer.get_center().copy()
        total_fg_pan = 8.1

        def apply_parallax_and_walk(_mob) -> None:
            p = pan_progress.get_value()
            dx_fg = total_fg_pan * p
            dx_mid = dx_fg * 0.68
            dx_far = dx_fg * 0.36
            dx_sky = dx_fg * 0.14

            self.sky_bg_burning.set_x(sky_bg_start_x - dx_sky)
            self.sky_burning.set_x(sky_start_x - dx_sky)
            self.far_burning.set_x(far_start_x - dx_far)
            self.mid_burning.set_x(mid_start_x - dx_mid)
            self.fg_burning.set_x(fg_start_x - dx_fg)
            self.particles.pan_offset.set_value(dx_fg)

            # Orangutan melangkah MAJU ke kanan menjauhi api di kiri
            walk_bob = abs(math.sin(p * math.pi * 6.0)) * 0.08
            walk_advance = 1.45 * smooth_step(p)
            orangutan.move_to(
                [
                    orang_start[0] - dx_fg + walk_advance,
                    orang_start[1] + walk_bob,
                    0.0,
                ]
            )

            # Rusa melangkah maju ke kanan menjauhi asap
            deer_bob = abs(math.sin(p * math.pi * 5.0 + 0.8)) * 0.06
            deer_advance = 1.65 * smooth_step(max(0.0, (p - 0.12) / 0.88))
            deer.move_to(
                [
                    deer_start[0] - dx_fg + deer_advance,
                    deer_start[1] + deer_bob,
                    0.0,
                ]
            )

        pan_driver = Dot().set_opacity(0.0)
        pan_driver.add_updater(apply_parallax_and_walk)
        self.add(pan_driver)

        hb_clock = ValueTracker(0.0)
        hb_base_pos = ValueTracker(0.0)
        orig_front_h = hb_front_wing.height if hb_front_wing.submobjects else 0.4
        orig_back_h = hb_back_wing.height if hb_back_wing.submobjects else 0.4

        def update_hornbill(_mob, dt: float) -> None:
            hb_clock.increment_value(dt)
            t = hb_clock.get_value()
            prog = hb_base_pos.get_value()

            # Hornbill terbang dari kiri (-9.5) ke kanan (+9.5)
            x = -9.5 + 19.0 * prog
            y = 2.15 + 0.65 * math.sin(prog * math.pi * 1.6) + 0.09 * math.sin(t * 7.5)
            hornbill.move_to([x, y, 0.0])

            # Kepak sayap — hanya jika ada submobject sayap
            if hb_front_wing.submobjects and hb_back_wing.submobjects:
                flap = math.sin(t * 8.8)
                body_center = hb_body.get_center()
                hb_front_wing.stretch_to_fit_height(max(0.18, orig_front_h * (0.46 + 0.54 * abs(flap))))
                hb_back_wing.stretch_to_fit_height(max(0.16, orig_back_h * (0.48 + 0.52 * abs(flap))))
                wing_offset = flap * 0.16
                hb_front_wing.move_to([body_center[0] - 0.16, body_center[1] + 0.36 + wing_offset, 0.0])
                hb_back_wing.move_to([body_center[0] - 0.28, body_center[1] + 0.44 - wing_offset * 0.7, 0.0])

        hornbill.add_updater(update_hornbill)

        self.play(
            pan_progress.animate.set_value(1.0),
            hb_base_pos.animate.set_value(0.62),
            self.particles.ash_intensity.animate.set_value(0.95),
            self.particles.fire_intensity.animate.set_value(0.65),
            run_time=4.8,
            rate_func=rate_functions.smooth,
        )

        pan_driver.remove_updater(apply_parallax_and_walk)
        self.remove(pan_driver)

        # Langkah lanjutan Orangutan & Rusa maju ke kanan dengan bobbing langkah alami
        walk_tail = ValueTracker(0.0)
        orang_tail_start = orangutan.get_center().copy()
        deer_tail_start = deer.get_center().copy()

        def update_tail_walk(_mob) -> None:
            w = walk_tail.get_value()
            orangutan.move_to(
                [
                    orang_tail_start[0] + 0.85 * smooth_step(w),
                    orang_tail_start[1] + abs(math.sin(w * math.pi * 3.0)) * 0.07,
                    0.0,
                ]
            )
            deer.move_to(
                [
                    deer_tail_start[0] + 0.95 * smooth_step(w),
                    deer_tail_start[1] + abs(math.sin(w * math.pi * 3.0 + 0.5)) * 0.05,
                    0.0,
                ]
            )

        tail_driver = Dot().set_opacity(0.0)
        tail_driver.add_updater(update_tail_walk)
        self.add(tail_driver)

        self.play(
            hb_base_pos.animate.set_value(1.05),
            walk_tail.animate.set_value(1.0),
            self.particles.smoke_intensity.animate.set_value(0.75),
            run_time=3.2,
            rate_func=rate_functions.smooth,
        )

        tail_driver.remove_updater(update_tail_walk)
        self.remove(tail_driver)
        hornbill.remove_updater(update_hornbill)

        self.wait(1.0)
        self._clear_subtitle(run_time=0.55)
        self.wait(0.4)
