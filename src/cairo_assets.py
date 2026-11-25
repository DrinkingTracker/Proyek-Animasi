"""Generator aset vektor SVG menggunakan Pycairo dan SVG murni untuk Scene 6."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Callable

import cairo
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .config import (
    ASSETS_DIR,
    BADGE_ISPA_PATH,
    CONFERENCE_SUMMIT_PATH,
    GENERATED_SVG_DIR,
    HOTSPOTS_SEA_PX,
    LUNGS_DAMAGED_PATH,
    LUNGS_HEALTHY_PATH,
    MAP_SEA_PATH,
    PALETTE,
    SETTLEMENT_LAYER_PATH,
    STICKMAN_COUGH_PATH,
    STICKMAN_MASKED_PATH,
    STICKMAN_NORMAL_PATH,
    SVG_DIR,
    TARGET_COUNTRIES_SEA_PX,
)

PANORAMA_W = 3200
PANORAMA_H = 1080
FRAME_W = 1920
FRAME_H = 1080
USER_MAP_IMG_PATH = Path("C:/Users/ACER/.gemini/antigravity/brain/75dc61ab-15de-4d9b-950f-28a89448b5b7/.user_uploaded/media_1795616678665_92d4a547.jpg")


def _hex_rgba(hex_color: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return (r, g, b, alpha)


def _draw_soft_glow(
    ctx: cairo.Context,
    cx: float,
    cy: float,
    radius: float,
    outer_hex: str,
    inner_hex: str,
    peak_alpha: float = 0.45,
    rings: int = 9,
) -> None:
    for i in range(rings, 0, -1):
        frac = i / rings
        r = radius * frac
        ro, go, bo, _ = _hex_rgba(outer_hex, 1.0)
        ri, gi, bi, _ = _hex_rgba(inner_hex, 1.0)
        mix = 1.0 - frac
        col_r = ro + (ri - ro) * mix
        col_g = go + (gi - go) * mix
        col_b = bo + (bi - bo) * mix
        alpha = peak_alpha * ((1.0 - frac * 0.85) ** 1.55) / (rings * 0.34)
        ctx.set_source_rgba(col_r, col_g, col_b, min(0.95, alpha))
        ctx.arc(cx, cy, r, 0, math.tau)
        ctx.fill()


def _draw_bounds_anchor(ctx: cairo.Context, w: int, h: int) -> None:
    ctx.set_source_rgba(0, 0, 0, 0.005)
    ctx.rectangle(0, 0, 1.0, 1.0)
    ctx.fill()
    ctx.rectangle(w - 1.0, h - 1.0, 1.0, 1.0)
    ctx.fill()


# =========================================================================
# BAGIAN A — ASET HUTAN TERBAKAR & PARTIKEL
# =========================================================================

def generate_sky_burning_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    pat = cairo.LinearGradient(0, 0, 0, PANORAMA_H)
    pat.add_color_stop_rgba(0.0, *_hex_rgba("#2B1810", 1.0))
    pat.add_color_stop_rgba(0.4, *_hex_rgba("#7A2E12", 0.95))
    pat.add_color_stop_rgba(0.7, *_hex_rgba("#C85A17", 0.90))
    pat.add_color_stop_rgba(1.0, *_hex_rgba("#E87C24", 0.85))
    ctx.set_source(pat)
    ctx.rectangle(0, 0, PANORAMA_W, PANORAMA_H)
    ctx.fill()

    rng = random.Random(88)
    for _ in range(45):
        cx = rng.uniform(0, PANORAMA_W)
        cy = rng.uniform(150, 750)
        rad = rng.uniform(80, 220)
        shade = rng.choice(["#3D352E", "#59493B", "#735B47", "#8C6A43"])
        _draw_soft_glow(ctx, cx, cy, rad, shade, "#261D17", peak_alpha=0.35, rings=6)

    surface.finish()
    return path


def generate_far_forest_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    ctx.set_source_rgba(*_hex_rgba("#3B2318", 0.92))
    ctx.move_to(0, PANORAMA_H)
    ctx.line_to(0, 520)

    x = 0
    rng = random.Random(101)
    while x < PANORAMA_W:
        dx = rng.uniform(35, 75)
        dy = rng.uniform(-40, 40)
        top_y = 500 + dy
        ctx.line_to(x + dx * 0.5, top_y)
        x += dx
        ctx.line_to(x, 530 + rng.uniform(-15, 15))

    ctx.line_to(PANORAMA_W, PANORAMA_H)
    ctx.close_path()
    ctx.fill()

    surface.finish()
    return path


def generate_mid_forest_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    rng = random.Random(202)
    ctx.set_source_rgba(*_hex_rgba("#22150F", 0.98))
    for x in range(50, PANORAMA_W - 50, 85):
        jitter_x = x + rng.uniform(-25, 25)
        trunk_h = rng.uniform(320, 500)
        w = rng.uniform(14, 28)
        ctx.rectangle(jitter_x, PANORAMA_H - trunk_h - 100, w, trunk_h + 100)
        ctx.fill()
        ctx.save()
        ctx.set_line_width(rng.uniform(5, 10))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(jitter_x + w * 0.5, PANORAMA_H - trunk_h - 40)
        ctx.line_to(jitter_x - rng.uniform(30, 80), PANORAMA_H - trunk_h - rng.uniform(80, 140))
        ctx.stroke()
        ctx.restore()

    ctx.set_source_rgba(*_hex_rgba("#2A1A12", 1.0))
    ctx.move_to(0, PANORAMA_H)
    ctx.line_to(0, 680)
    for x in range(0, PANORAMA_W, 100):
        ctx.line_to(x + 50, 670 + rng.uniform(-15, 15))
    ctx.line_to(PANORAMA_W, PANORAMA_H)
    ctx.close_path()
    ctx.fill()

    surface.finish()
    return path


def generate_fg_forest_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    rng = random.Random(303)
    ctx.set_source_rgba(*_hex_rgba("#140C08", 1.0))

    for x in [120, 480, 950, 1500, 2100, 2750]:
        bx = x + rng.uniform(-30, 30)
        w = rng.uniform(55, 90)
        h = rng.uniform(600, 800)
        ctx.rectangle(bx, PANORAMA_H - h, w, h)
        ctx.fill()

    ctx.move_to(0, PANORAMA_H)
    ctx.line_to(0, 820)
    for x in range(0, PANORAMA_W, 120):
        ctx.line_to(x + 60, 810 + rng.uniform(-18, 18))
    ctx.line_to(PANORAMA_W, PANORAMA_H)
    ctx.close_path()
    ctx.fill()

    for x in range(80, PANORAMA_W, 160):
        gx = x + rng.uniform(-40, 40)
        gy = 840 + rng.uniform(0, 80)
        _draw_soft_glow(ctx, gx, gy, rng.uniform(35, 60), "#D00000", "#FFBA08", peak_alpha=0.55, rings=5)

    surface.finish()
    return path


def generate_flame_svg(path: Path, variant: int = 0) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 200, 280)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 200, 280)

    ctx.set_source_rgba(*_hex_rgba("#D00000", 0.92))
    ctx.move_to(100, 20)
    ctx.curve_to(160, 80, 180, 180, 100, 260)
    ctx.curve_to(20, 180, 40, 80, 100, 20)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#F48C06", 0.95))
    ctx.move_to(100, 60)
    ctx.curve_to(145, 110, 160, 195, 100, 255)
    ctx.curve_to(40, 195, 55, 110, 100, 60)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#FFF3B0", 0.98))
    ctx.move_to(100, 120)
    ctx.curve_to(130, 160, 140, 215, 100, 250)
    ctx.curve_to(60, 215, 70, 160, 100, 120)
    ctx.fill()

    surface.finish()
    return path


def generate_smoke_puff_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 240, 240)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 240, 240)

    blobs = [
        (120, 120, 75, "#3D352E", 0.45),
        (95, 135, 55, "#59493B", 0.40),
        (145, 110, 60, "#4F4439", 0.42),
        (110, 95, 50, "#6E5A47", 0.38),
        (135, 140, 50, "#3D352E", 0.40),
    ]
    for cx, cy, r, col, a in blobs:
        ctx.set_source_rgba(*_hex_rgba(col, a))
        ctx.arc(cx, cy, r, 0, math.tau)
        ctx.fill()

    surface.finish()
    return path


def generate_ember_spark_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 40, 40)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 40, 40)
    _draw_soft_glow(ctx, 20, 20, 18, "#E85D04", "#FFEE88", peak_alpha=0.9, rings=5)
    surface.finish()
    return path


def generate_ash_flake_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 32, 32)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 32, 32)
    ctx.set_source_rgba(*_hex_rgba("#887C74", 0.75))
    ctx.arc(16, 16, 7, 0, math.tau)
    ctx.fill()
    surface.finish()
    return path


# =========================================================================
# BAGIAN B — PERMUKIMAN, STICKMAN, PARU-PARU & ISPA
# =========================================================================

def generate_settlement_layer_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    pat = cairo.LinearGradient(0, 0, 0, PANORAMA_H)
    pat.add_color_stop_rgba(0.0, *_hex_rgba("#7A6855", 0.95))
    pat.add_color_stop_rgba(0.5, *_hex_rgba("#C4A77D", 0.90))
    pat.add_color_stop_rgba(1.0, *_hex_rgba("#E8D5B5", 0.88))
    ctx.set_source(pat)
    ctx.rectangle(0, 0, PANORAMA_W, PANORAMA_H)
    ctx.fill()

    # Gedung kota siluet
    ctx.set_source_rgba(*_hex_rgba("#615344", 0.40))
    for x in range(100, PANORAMA_W, 140):
        gw = random.Random(x).uniform(60, 110)
        gh = random.Random(x).uniform(180, 360)
        ctx.rectangle(x, 700 - gh, gw, gh)
        ctx.fill()

    # Rumah-rumah warga
    rng = random.Random(555)
    for x in range(50, PANORAMA_W - 80, 160):
        hx = x + rng.uniform(-20, 20)
        hw = rng.uniform(110, 150)
        hh = rng.uniform(90, 130)
        base_y = 740

        ctx.set_source_rgba(*_hex_rgba("#473E35", 0.85))
        ctx.rectangle(hx, base_y - hh, hw, hh)
        ctx.fill()

        roof_h = rng.uniform(45, 65)
        ctx.set_source_rgba(*_hex_rgba("#2E2721", 0.95))
        ctx.move_to(hx - 15, base_y - hh)
        ctx.line_to(hx + hw * 0.5, base_y - hh - roof_h)
        ctx.line_to(hx + hw + 15, base_y - hh)
        ctx.close_path()
        ctx.fill()

        ctx.set_source_rgba(*_hex_rgba("#E9C46A", 0.35))
        ctx.rectangle(hx + 18, base_y - hh + 25, 24, 28)
        ctx.rectangle(hx + hw - 42, base_y - hh + 25, 24, 28)
        ctx.fill()

    # Tiang listrik & kabel
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 0.90))
    ctx.set_line_width(4)
    poles = [320, 980, 1650, 2300, 2950]
    for px in poles:
        ctx.move_to(px, 780)
        ctx.line_to(px, 440)
        ctx.stroke()
        ctx.move_to(px - 35, 470)
        ctx.line_to(px + 35, 470)
        ctx.stroke()

    ctx.set_line_width(2.0)
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 0.65))
    for i in range(len(poles) - 1):
        p1, p2 = poles[i], poles[i + 1]
        ctx.move_to(p1, 470)
        ctx.curve_to((p1 + p2) * 0.5, 520, (p1 + p2) * 0.5, 520, p2, 470)
        ctx.stroke()

    # Jalan raya
    ctx.set_source_rgba(*_hex_rgba("#38332E", 1.0))
    ctx.rectangle(0, 750, PANORAMA_W, PANORAMA_H - 750)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#F4F0E8", 0.55))
    ctx.set_line_width(8)
    for rx in range(40, PANORAMA_W, 140):
        ctx.move_to(rx, 860)
        ctx.line_to(rx + 70, 860)
        ctx.stroke()

    surface.finish()
    return path


def generate_stickman_normal_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 240, 320)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 240, 320)

    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(120, 80, 42, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.set_line_width(4)
    ctx.arc(120, 80, 42, 0, math.tau)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.move_to(80, 70)
    ctx.curve_to(95, 38, 145, 38, 160, 68)
    ctx.curve_to(140, 52, 100, 52, 80, 70)
    ctx.fill()

    ctx.arc(110, 82, 4.5, 0, math.tau)
    ctx.arc(135, 82, 4.5, 0, math.tau)
    ctx.fill()

    ctx.set_line_width(2.5)
    ctx.move_to(103, 72)
    ctx.line_to(116, 73)
    ctx.move_to(129, 73)
    ctx.line_to(142, 72)
    ctx.stroke()
    ctx.move_to(118, 102)
    ctx.line_to(128, 102)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.rectangle(98, 126, 44, 76)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.set_line_width(4)
    ctx.rectangle(98, 126, 44, 76)
    ctx.stroke()

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(6)
    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.move_to(98, 136)
    ctx.line_to(76, 185)
    ctx.move_to(142, 136)
    ctx.line_to(164, 185)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#264653", 1.0))
    ctx.set_line_width(8)
    ctx.move_to(110, 202)
    ctx.line_to(106, 275)
    ctx.move_to(130, 202)
    ctx.line_to(134, 275)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#E76F51", 1.0))
    ctx.set_line_width(10)
    ctx.move_to(100, 280)
    ctx.line_to(112, 280)
    ctx.move_to(128, 280)
    ctx.line_to(140, 280)
    ctx.stroke()

    surface.finish()
    return path


def generate_stickman_cough_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 240, 320)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 240, 320)

    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(120, 84, 42, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.set_line_width(4)
    ctx.arc(120, 84, 42, 0, math.tau)
    ctx.stroke()

    ctx.move_to(80, 74)
    ctx.curve_to(95, 42, 145, 42, 160, 72)
    ctx.curve_to(140, 56, 100, 56, 80, 74)
    ctx.fill()

    ctx.set_line_width(3.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(105, 80)
    ctx.line_to(114, 85)
    ctx.line_to(105, 90)
    ctx.move_to(135, 80)
    ctx.line_to(126, 85)
    ctx.line_to(135, 90)
    ctx.stroke()

    ctx.move_to(104, 73)
    ctx.line_to(115, 78)
    ctx.move_to(136, 73)
    ctx.line_to(125, 78)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.rectangle(98, 130, 44, 76)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.set_line_width(4)
    ctx.rectangle(98, 130, 44, 76)
    ctx.stroke()

    # Lengan naik menutup hidung & mulut
    ctx.set_line_width(7)
    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.move_to(140, 140)
    ctx.line_to(148, 118)
    ctx.line_to(120, 102)
    ctx.stroke()
    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(120, 102, 9, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.set_line_width(2.5)
    ctx.arc(120, 102, 9, 0, math.tau)
    ctx.stroke()

    # Lengan kiri memegangi dada sesak
    ctx.set_line_width(7)
    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.move_to(98, 140)
    ctx.line_to(88, 162)
    ctx.line_to(112, 160)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#264653", 1.0))
    ctx.set_line_width(8)
    ctx.move_to(110, 206)
    ctx.line_to(106, 275)
    ctx.move_to(130, 206)
    ctx.line_to(136, 275)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#E76F51", 1.0))
    ctx.set_line_width(10)
    ctx.move_to(100, 280)
    ctx.line_to(112, 280)
    ctx.move_to(130, 280)
    ctx.line_to(142, 280)
    ctx.stroke()

    # Gelombang batuk getar
    ctx.set_source_rgba(*_hex_rgba("#E76F51", 0.85))
    ctx.set_line_width(2.6)
    for rad, start_deg, end_deg in [(24, -40, 30), (34, -45, 35)]:
        ctx.arc(88, 100, rad, math.radians(start_deg), math.radians(end_deg))
        ctx.stroke()

    surface.finish()
    return path


def generate_stickman_masked_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 240, 320)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 240, 320)

    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(120, 80, 42, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.set_line_width(4)
    ctx.arc(120, 80, 42, 0, math.tau)
    ctx.stroke()

    ctx.move_to(80, 70)
    ctx.curve_to(95, 38, 145, 38, 160, 68)
    ctx.curve_to(140, 52, 100, 52, 80, 70)
    ctx.fill()

    ctx.arc(110, 80, 4.5, 0, math.tau)
    ctx.arc(135, 80, 4.5, 0, math.tau)
    ctx.fill()
    ctx.set_line_width(2.8)
    ctx.move_to(102, 70)
    ctx.line_to(116, 73)
    ctx.move_to(138, 70)
    ctx.line_to(124, 73)
    ctx.stroke()

    # Masker N95
    ctx.set_source_rgba(*_hex_rgba("#E8F4F8", 1.0))
    ctx.move_to(94, 94)
    ctx.line_to(146, 94)
    ctx.curve_to(146, 124, 94, 124, 94, 94)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#457B9D", 1.0))
    ctx.set_line_width(3.2)
    ctx.move_to(94, 94)
    ctx.line_to(146, 94)
    ctx.curve_to(146, 124, 94, 124, 94, 94)
    ctx.stroke()

    ctx.set_line_width(1.8)
    ctx.move_to(94, 98)
    ctx.line_to(80, 88)
    ctx.move_to(146, 98)
    ctx.line_to(160, 88)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.rectangle(98, 126, 44, 76)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.set_line_width(4)
    ctx.rectangle(98, 126, 44, 76)
    ctx.stroke()

    ctx.set_line_width(6.5)
    ctx.set_source_rgba(*_hex_rgba("#2A9D8F", 1.0))
    ctx.move_to(98, 136)
    ctx.line_to(76, 185)
    ctx.move_to(142, 136)
    ctx.line_to(164, 185)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#264653", 1.0))
    ctx.set_line_width(8)
    ctx.move_to(110, 202)
    ctx.line_to(106, 275)
    ctx.move_to(130, 202)
    ctx.line_to(134, 275)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#E76F51", 1.0))
    ctx.set_line_width(10)
    ctx.move_to(100, 280)
    ctx.line_to(112, 280)
    ctx.move_to(128, 280)
    ctx.line_to(140, 280)
    ctx.stroke()

    surface.finish()
    return path


def generate_lungs_healthy_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 360, 380)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 360, 380)

    ctx.set_source_rgba(*_hex_rgba("#F4A261", 1.0))
    ctx.rectangle(166, 25, 28, 90)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.set_line_width(3.0)
    ctx.rectangle(166, 25, 28, 90)
    ctx.stroke()

    for ty in range(35, 110, 14):
        ctx.move_to(166, ty)
        ctx.line_to(194, ty)
        ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#F28482", 0.95))
    ctx.move_to(165, 115)
    ctx.curve_to(130, 95, 75, 120, 60, 180)
    ctx.curve_to(45, 240, 65, 310, 110, 340)
    ctx.curve_to(145, 360, 165, 320, 165, 230)
    ctx.close_path()
    ctx.fill()

    ctx.move_to(195, 115)
    ctx.curve_to(230, 95, 285, 120, 300, 180)
    ctx.curve_to(315, 240, 295, 310, 250, 340)
    ctx.curve_to(215, 360, 195, 320, 195, 230)
    ctx.close_path()
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#9E2A2B", 0.85))
    ctx.set_line_width(3.2)
    ctx.move_to(165, 115)
    ctx.curve_to(130, 95, 75, 120, 60, 180)
    ctx.curve_to(45, 240, 65, 310, 110, 340)
    ctx.curve_to(145, 360, 165, 320, 165, 230)
    ctx.close_path()
    ctx.stroke()

    ctx.move_to(195, 115)
    ctx.curve_to(230, 95, 285, 120, 300, 180)
    ctx.curve_to(315, 240, 295, 310, 250, 340)
    ctx.curve_to(215, 360, 195, 320, 195, 230)
    ctx.close_path()
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 0.85))
    ctx.set_line_width(3.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(180, 115)
    ctx.line_to(135, 170)
    ctx.line_to(105, 210)
    ctx.move_to(135, 170)
    ctx.line_to(145, 235)
    ctx.move_to(105, 210)
    ctx.line_to(80, 260)
    ctx.move_to(180, 115)
    ctx.line_to(225, 170)
    ctx.line_to(255, 210)
    ctx.move_to(225, 170)
    ctx.line_to(215, 235)
    ctx.move_to(255, 210)
    ctx.line_to(280, 260)
    ctx.stroke()

    surface.finish()
    return path


def generate_lungs_damaged_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 360, 380)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 360, 380)

    ctx.set_source_rgba(*_hex_rgba("#6B4D3C", 1.0))
    ctx.rectangle(166, 25, 28, 90)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F1915", 1.0))
    ctx.set_line_width(3.0)
    ctx.rectangle(166, 25, 28, 90)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#D00000", 0.90))
    for ty in range(35, 110, 14):
        ctx.move_to(166, ty)
        ctx.line_to(194, ty)
        ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#383236", 0.96))
    ctx.move_to(165, 115)
    ctx.curve_to(130, 95, 75, 120, 60, 180)
    ctx.curve_to(45, 240, 65, 310, 110, 340)
    ctx.curve_to(145, 360, 165, 320, 165, 230)
    ctx.close_path()
    ctx.fill()

    ctx.move_to(195, 115)
    ctx.curve_to(230, 95, 285, 120, 300, 180)
    ctx.curve_to(315, 240, 295, 310, 250, 340)
    ctx.curve_to(215, 360, 195, 320, 195, 230)
    ctx.close_path()
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#D00000", 0.95))
    ctx.set_line_width(3.5)
    ctx.move_to(165, 115)
    ctx.curve_to(130, 95, 75, 120, 60, 180)
    ctx.curve_to(45, 240, 65, 310, 110, 340)
    ctx.curve_to(145, 360, 165, 320, 165, 230)
    ctx.close_path()
    ctx.stroke()

    ctx.move_to(195, 115)
    ctx.curve_to(230, 95, 285, 120, 300, 180)
    ctx.curve_to(315, 240, 295, 310, 250, 340)
    ctx.curve_to(215, 360, 195, 320, 195, 230)
    ctx.close_path()
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#E85D04", 0.95))
    ctx.set_line_width(4.0)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(180, 115)
    ctx.line_to(135, 170)
    ctx.line_to(105, 210)
    ctx.move_to(135, 170)
    ctx.line_to(145, 235)
    ctx.move_to(105, 210)
    ctx.line_to(80, 260)
    ctx.move_to(180, 115)
    ctx.line_to(225, 170)
    ctx.line_to(255, 210)
    ctx.move_to(225, 170)
    ctx.line_to(215, 235)
    ctx.move_to(255, 210)
    ctx.line_to(280, 260)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#141113", 0.90))
    rng = random.Random(404)
    for _ in range(35):
        ctx.arc(rng.uniform(80, 150), rng.uniform(150, 310), rng.uniform(3, 6), 0, math.tau)
        ctx.fill()
        ctx.arc(rng.uniform(210, 280), rng.uniform(150, 310), rng.uniform(3, 6), 0, math.tau)
        ctx.fill()

    surface.finish()
    return path


def generate_badge_ispa_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 460, 220)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 460, 220)

    ctx.set_source_rgba(*_hex_rgba("#1B232A", 0.94))
    ctx.rectangle(10, 10, 440, 200)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#D00000", 0.90))
    ctx.set_line_width(3.0)
    ctx.rectangle(10, 10, 440, 200)
    ctx.stroke()

    ctx.save()
    ctx.translate(45, 65)
    ctx.set_source_rgba(*_hex_rgba("#FFB703", 1.0))
    ctx.move_to(0, 30)
    ctx.line_to(25, -20)
    ctx.line_to(50, 30)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1B232A", 1.0))
    ctx.set_line_width(3.5)
    ctx.move_to(25, -5)
    ctx.line_to(25, 14)
    ctx.stroke()
    ctx.arc(25, 22, 2.4, 0, math.tau)
    ctx.fill()
    ctx.restore()

    def draw_tp(text, x, y, sz, col, bold=True):
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(sz)
        ctx.move_to(x, y)
        ctx.text_path(text)
        ctx.set_source_rgba(*_hex_rgba(col, 1.0))
        ctx.fill()

    draw_tp("DARURAT KESEHATAN MASYARAKAT", 115, 45, 14, "#F48C06")
    draw_tp("ISPA", 115, 95, 46, "#D00000")
    draw_tp("Infeksi Saluran Pernapasan Akut", 115, 126, 17, "#F8F9FA", bold=False)

    ctx.set_source_rgba(*_hex_rgba("#9E2A2B", 0.85))
    ctx.rectangle(35, 150, 390, 38)
    ctx.fill()
    draw_tp("KONSENTRASI PM2.5 > 350 ug/m3  (LEVEL BERBAHAYA)", 55, 174, 14, "#FFD166")

    surface.finish()
    return path


def generate_conference_summit_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    surface = cairo.SVGSurface(str(path), 640, 420)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, 640, 420)

    ctx.set_source_rgba(*_hex_rgba("#1B232A", 0.96))
    ctx.rectangle(10, 10, 620, 400)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2D6A4F", 0.90))
    ctx.set_line_width(3.0)
    ctx.rectangle(10, 10, 620, 400)
    ctx.stroke()

    def draw_tp(text, x, y, sz, col, bold=True):
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(sz)
        ctx.move_to(x, y)
        ctx.text_path(text)
        ctx.set_source_rgba(*_hex_rgba(col, 1.0))
        ctx.fill()

    draw_tp("ASEAN MINISTERIAL MEETING ON HAZE", 170, 45, 14, "#F48C06")
    draw_tp("KTT DARURAT KABUT ASAP LINTAS BATAS", 110, 75, 20, "#F8F9FA")

    flags = [
        {"x": 100, "country": "ID"},
        {"x": 230, "country": "MY"},
        {"x": 360, "country": "SG"},
        {"x": 490, "country": "BN"},
    ]
    for fl in flags:
        fx = fl["x"]
        ctx.set_source_rgba(*_hex_rgba("#A0AEC0", 1.0))
        ctx.set_line_width(3.0)
        ctx.move_to(fx, 100)
        ctx.line_to(fx, 210)
        ctx.stroke()

        if fl["country"] == "ID":
            ctx.set_source_rgba(*_hex_rgba("#D00000", 1.0))
            ctx.rectangle(fx, 105, 65, 20)
            ctx.fill()
            ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 1.0))
            ctx.rectangle(fx, 125, 65, 20)
            ctx.fill()
        elif fl["country"] == "MY":
            for s in range(6):
                ctx.set_source_rgba(*_hex_rgba("#D00000" if s % 2 == 0 else "#FFFFFF", 1.0))
                ctx.rectangle(fx, 105 + s * 6.6, 65, 6.6)
                ctx.fill()
            ctx.set_source_rgba(*_hex_rgba("#002B7F", 1.0))
            ctx.rectangle(fx, 105, 32, 22)
            ctx.fill()
            ctx.set_source_rgba(*_hex_rgba("#FCD116", 1.0))
            ctx.arc(fx + 16, 116, 6, 0, math.tau)
            ctx.fill()
        elif fl["country"] == "SG":
            ctx.set_source_rgba(*_hex_rgba("#ED2939", 1.0))
            ctx.rectangle(fx, 105, 65, 20)
            ctx.fill()
            ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 1.0))
            ctx.rectangle(fx, 125, 65, 20)
            ctx.fill()
            ctx.arc(fx + 14, 115, 6, 0, math.tau)
            ctx.fill()
        elif fl["country"] == "BN":
            ctx.set_source_rgba(*_hex_rgba("#F7E017", 1.0))
            ctx.rectangle(fx, 105, 65, 40)
            ctx.fill()
            ctx.set_source_rgba(*_hex_rgba("#000000", 1.0))
            ctx.move_to(fx, 105)
            ctx.line_to(fx + 65, 138)
            ctx.line_to(fx + 65, 145)
            ctx.line_to(fx, 112)
            ctx.fill()

    # Podium Konferensi
    ctx.set_source_rgba(*_hex_rgba("#2C3E50", 1.0))
    ctx.rectangle(250, 240, 140, 120)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#F4A261", 1.0))
    ctx.rectangle(240, 230, 160, 15)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#E76F51", 1.0))
    ctx.arc(320, 290, 22, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#FFEAA7", 1.0))
    ctx.set_line_width(2.5)
    ctx.arc(320, 290, 15, 0, math.tau)
    ctx.stroke()

    ctx.set_source_rgba(*_hex_rgba("#A0AEC0", 1.0))
    ctx.set_line_width(2.5)
    ctx.move_to(290, 230)
    ctx.line_to(305, 205)
    ctx.move_to(350, 230)
    ctx.line_to(335, 205)
    ctx.stroke()
    ctx.set_source_rgba(*_hex_rgba("#111111", 1.0))
    ctx.arc(305, 205, 4.5, 0, math.tau)
    ctx.arc(335, 205, 4.5, 0, math.tau)
    ctx.fill()

    # Karakter Diplomat Stickman
    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(320, 165, 24, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#2B2520", 1.0))
    ctx.set_line_width(3.0)
    ctx.arc(320, 165, 24, 0, math.tau)
    ctx.stroke()
    ctx.arc(313, 163, 3.0, 0, math.tau)
    ctx.arc(327, 163, 3.0, 0, math.tau)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.rectangle(295, 192, 50, 40)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 1.0))
    ctx.move_to(314, 192)
    ctx.line_to(320, 205)
    ctx.line_to(326, 192)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#D00000", 1.0))
    ctx.move_to(318, 200)
    ctx.line_to(322, 200)
    ctx.line_to(320, 220)
    ctx.fill()

    # Delegasi Kiri & Kanan
    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(190, 180, 20, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.rectangle(175, 202, 35, 60)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 0.95))
    ctx.rectangle(160, 220, 24, 32)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#FEE4CB", 1.0))
    ctx.arc(450, 180, 20, 0, math.tau)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#1F2933", 1.0))
    ctx.rectangle(430, 202, 35, 60)
    ctx.fill()
    ctx.set_source_rgba(*_hex_rgba("#FFFFFF", 0.95))
    ctx.rectangle(455, 220, 24, 32)
    ctx.fill()

    ctx.set_source_rgba(*_hex_rgba("#D00000", 0.90))
    ctx.rectangle(40, 368, 560, 34)
    ctx.fill()
    draw_tp("DESAKAN REGIONAL: PENEGAKAN HUKUM & AKSI TANGGAP ASAP LINTAS BATAS", 70, 390, 14, "#FFFFFF")

    surface.finish()
    return path


def ensure_sea_map_svg(path: Path) -> Path:
    """Memastikan peta Asia Tenggara vektor dari gambar pengguna tersedia."""
    if path.exists() and path.stat().st_size > 100000:
        return path

    from scratch.tools_build_user_map import build_svg_from_user_image
    build_svg_from_user_image()
    return path


def ensure_all_assets(force: bool = False) -> dict[str, Path]:
    GENERATED_SVG_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)

    assets: dict[str, tuple[Path, Callable[[Path], Path]]] = {
        "sky_burning": (GENERATED_SVG_DIR / "sky_burning.svg", generate_sky_burning_svg),
        "forest_far_burnt": (GENERATED_SVG_DIR / "forest_far_burnt.svg", generate_far_forest_svg),
        "forest_mid_burnt": (GENERATED_SVG_DIR / "forest_mid_burnt.svg", generate_mid_forest_svg),
        "forest_fg_burnt": (GENERATED_SVG_DIR / "forest_fg_burnt.svg", generate_fg_forest_svg),
        "flame_0": (GENERATED_SVG_DIR / "flame_0.svg", lambda p: generate_flame_svg(p, 0)),
        "flame_1": (GENERATED_SVG_DIR / "flame_1.svg", lambda p: generate_flame_svg(p, 1)),
        "flame_2": (GENERATED_SVG_DIR / "flame_2.svg", lambda p: generate_flame_svg(p, 2)),
        "smoke_puff": (GENERATED_SVG_DIR / "smoke_puff.svg", generate_smoke_puff_svg),
        "ember_spark": (GENERATED_SVG_DIR / "ember_spark.svg", generate_ember_spark_svg),
        "ash_flake": (GENERATED_SVG_DIR / "ash_flake.svg", generate_ash_flake_svg),
        "settlement_layer": (SETTLEMENT_LAYER_PATH, generate_settlement_layer_svg),
        "stickman_normal": (STICKMAN_NORMAL_PATH, generate_stickman_normal_svg),
        "stickman_cough": (STICKMAN_COUGH_PATH, generate_stickman_cough_svg),
        "stickman_masked": (STICKMAN_MASKED_PATH, generate_stickman_masked_svg),
        "lungs_healthy": (LUNGS_HEALTHY_PATH, generate_lungs_healthy_svg),
        "lungs_damaged": (LUNGS_DAMAGED_PATH, generate_lungs_damaged_svg),
        "badge_ispa": (BADGE_ISPA_PATH, generate_badge_ispa_svg),
        "peta_asia_tenggara": (MAP_SEA_PATH, ensure_sea_map_svg),
        "conference_summit": (CONFERENCE_SUMMIT_PATH, generate_conference_summit_svg),
    }

    result: dict[str, Path] = {}
    for key, (path, gen_func) in assets.items():
        if force or not path.exists():
            gen_func(path)
        result[key] = path

    return result
