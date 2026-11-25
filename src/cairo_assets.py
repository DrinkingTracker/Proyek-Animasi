"""Generator aset vektor SVG menggunakan Pycairo (cairo.SVGSurface).

Seluruh aset (latar peta, layer hutan sehat & terbakar, api, asap, bara, abu)
dihasilkan murni dalam format SVG tanpa membutuhkan Pillow sama sekali.
Efek pijar lembut dan asap dibangun dengan teknik lapisan konsentris transparan
agar terbaca sempurna oleh SVGMobject di Manim.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Callable

import cairo

from .config import GENERATED_SVG_DIR

# Dimensi kanvas panorama vektor (rasio lebih lebar dari 16:9 untuk panning 2.5D parallax)
PANORAMA_W = 3200
PANORAMA_H = 1080
FRAME_W = 1920
FRAME_H = 1080


def _hex_rgba(hex_color: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return (r, g, b, alpha)


def _quad_to(ctx: cairo.Context, x1: float, y1: float, x2: float, y2: float) -> None:
    """Konversi kurva Bezier kuadratik ke kubik untuk Pycairo."""
    x0, y0 = ctx.get_current_point()
    c1x = x0 + (2.0 / 3.0) * (x1 - x0)
    c1y = y0 + (2.0 / 3.0) * (y1 - y0)
    c2x = x2 + (2.0 / 3.0) * (x1 - x2)
    c2y = y2 + (2.0 / 3.0) * (y1 - y2)
    ctx.curve_to(c1x, c1y, c2x, c2y, x2, y2)


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
    """Pijar radial lembut berbasis lingkaran berlapis agar 100% kompatibel dengan SVGMobject."""
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
    """Menjaga bounding-box SVG agar setiap layer panorama sejajar 100% di SVGMobject."""
    # Gunakan alpha sangat kecil (> 0) pada dua sudut agar Cairo menulis path
    # dan SVGMobject mengunci ukuran tepat (w x h) tanpa terlihat mata.
    ctx.set_source_rgba(0, 0, 0, 0.005)
    ctx.rectangle(0, 0, 1.0, 1.0)
    ctx.fill()
    ctx.rectangle(w - 1.0, h - 1.0, 1.0, 1.0)
    ctx.fill()


def _draw_cloud(
    ctx: cairo.Context,
    cx: float,
    cy: float,
    scale: float,
    color_hex: str,
    alpha: float,
) -> None:
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    blobs = [
        (-85, 12, 48),
        (-30, -10, 62),
        (38, -4, 56),
        (92, 16, 40),
        (5, 18, 52),
    ]
    ctx.set_source_rgba(*_hex_rgba(color_hex, alpha))
    for bx, by, br in blobs:
        ctx.arc(bx, by, br, 0, math.tau)
        ctx.fill()
    ctx.restore()


def generate_map_backdrop_svg(out_path: Path) -> None:
    """Latar belakang peta bergaya infografis Kok Bisa dalam SVG murni."""
    surface = cairo.SVGSurface(str(out_path), FRAME_W, FRAME_H)
    ctx = cairo.Context(surface)

    # Dasar laut editorial
    ctx.set_source_rgba(*_hex_rgba("#DCE8E2", 1.0))
    ctx.rectangle(0, 0, FRAME_W, FRAME_H)
    ctx.fill()

    # Cahaya fokus lembut di tengah peta (radius dijaga di dalam batas tinggi 1080px)
    _draw_soft_glow(
        ctx,
        FRAME_W * 0.5,
        FRAME_H * 0.5,
        FRAME_H * 0.48,
        outer_hex="#E5EFE9",
        inner_hex="#F7F4EC",
        peak_alpha=0.85,
        rings=6,
    )

    # Garis lintang & bujur kartografi halus
    ctx.set_source_rgba(*_hex_rgba("#7D988C", 0.16))
    ctx.set_line_width(1.2)
    step = 120
    for x in range(0, FRAME_W + 1, step):
        ctx.move_to(x, 0)
        ctx.line_to(x, FRAME_H)
        ctx.stroke()
    for y in range(0, FRAME_H + 1, step):
        ctx.move_to(0, y)
        ctx.line_to(FRAME_W, y)
        ctx.stroke()

    # Garis khatulistiwa aksen tipis
    ctx.save()
    ctx.set_dash([12, 10])
    ctx.set_source_rgba(*_hex_rgba("#52796F", 0.28))
    ctx.set_line_width(2.0)
    ctx.move_to(0, FRAME_H * 0.50)
    ctx.line_to(FRAME_W, FRAME_H * 0.50)
    ctx.stroke()
    ctx.restore()

    surface.finish()


def generate_sky_details_svg(out_path: Path, burning: bool) -> None:
    """Detail atmosfer langit (sinar matahari & awan atau pijar panas & gumpalan asap atas)."""
    surface = cairo.SVGSurface(str(out_path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    if not burning:
        # Pijar matahari tropis (tetap berada di dalam kanvas 3200x1080)
        _draw_soft_glow(
            ctx,
            520,
            245,
            235,
            outer_hex="#FDE68A",
            inner_hex="#FFFBEB",
            peak_alpha=0.72,
            rings=6,
        )
        # Berkas sinar matahari diagonal halus
        for sx, width in [(260, 150), (540, 210), (860, 170)]:
            ctx.set_source_rgba(*_hex_rgba("#FFF9DB", 0.15))
            ctx.move_to(sx, 0)
            ctx.line_to(sx + width, 0)
            ctx.line_to(sx + width + 480, PANORAMA_H)
            ctx.line_to(sx + 320, PANORAMA_H)
            ctx.close_path()
            ctx.fill()

        # Awan tropis lembut
        for cx, cy, sc in [
            (480, 210, 1.1),
            (1180, 170, 1.35),
            (1880, 240, 1.0),
            (2650, 185, 1.25),
        ]:
            _draw_cloud(ctx, cx, cy, sc, "#FFFFFF", 0.58)
    else:
        # Pijar panas kebakaran di cakrawala (tetap di dalam tinggi 1080px)
        _draw_soft_glow(
            ctx,
            1050,
            690,
            370,
            outer_hex="#9A3412",
            inner_hex="#FDBA74",
            peak_alpha=0.58,
            rings=6,
        )
        # Gumpalan awan asap gelap di langit atas
        for cx, cy, sc in [
            (620, 220, 1.6),
            (1420, 180, 1.9),
            (2200, 250, 1.7),
            (2850, 210, 1.5),
        ]:
            _draw_cloud(ctx, cx, cy, sc, "#332C30", 0.45)

    surface.finish()


def generate_far_forest_svg(out_path: Path, burning: bool) -> None:
    """Siluet perbukitan & kanopi hutan tropis jauh dalam format SVG."""
    surface = cairo.SVGSurface(str(out_path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    rng = random.Random(101)
    layers = [
        (560, "#5A8F80" if not burning else "#3B2B2C", 18, 0.94),
        (655, "#366959" if not burning else "#261C1E", 26, 0.98),
    ]

    for base_y, col, bump_h, alpha in layers:
        ctx.set_source_rgba(*_hex_rgba(col, alpha))
        ctx.move_to(0, PANORAMA_H)
        ctx.line_to(0, base_y)
        x = 0.0
        while x < PANORAMA_W:
            step = rng.uniform(75, 130)
            nx = min(PANORAMA_W, x + step)
            wave = math.sin(x * 0.0032) * 55 + math.cos(x * 0.008) * 24
            cy = base_y + wave - rng.uniform(bump_h * 0.5, bump_h * 1.9)
            nwave = math.sin(nx * 0.0032) * 55 + math.cos(nx * 0.008) * 24
            ctx.curve_to(x + step * 0.35, cy, x + step * 0.65, cy, nx, base_y + nwave)
            x = nx
        ctx.line_to(PANORAMA_W, PANORAMA_H)
        ctx.close_path()
        ctx.fill()

    # Lapisan kabut lembah / kabut asap tipis
    mist_col = "#D8EFE2" if not burning else "#B45309"
    ctx.set_source_rgba(*_hex_rgba(mist_col, 0.22 if not burning else 0.18))
    ctx.rectangle(0, 720, PANORAMA_W, 210)
    ctx.fill()

    surface.finish()


def _draw_canopy_cluster(
    ctx: cairo.Context,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    rng: random.Random,
    base_col: str,
    hi_col: str,
    shadow_col: str,
) -> None:
    blobs = []
    count = 5
    for i in range(count):
        ang = (i / count) * math.tau + rng.uniform(-0.2, 0.2)
        dist = rng.uniform(0.24, 0.58)
        bx = cx + math.cos(ang) * rx * dist
        by = cy + math.sin(ang) * ry * dist
        br = rng.uniform(0.45, 0.65) * min(rx, ry)
        blobs.append((bx, by, br))
    blobs.append((cx, cy - ry * 0.12, min(rx, ry) * 0.64))

    ctx.set_source_rgba(*_hex_rgba(shadow_col, 1.0))
    for bx, by, br in blobs:
        ctx.arc(bx + 6, by + 10, br, 0, math.tau)
        ctx.fill()

    ctx.set_source_rgba(*_hex_rgba(base_col, 1.0))
    for bx, by, br in blobs:
        ctx.arc(bx, by, br, 0, math.tau)
        ctx.fill()

    ctx.set_source_rgba(*_hex_rgba(hi_col, 0.72))
    for bx, by, br in blobs[::2]:
        ctx.arc(bx - br * 0.18, by - br * 0.22, br * 0.66, 0, math.tau)
        ctx.fill()


def _draw_tree(
    ctx: cairo.Context,
    x: float,
    ground_y: float,
    height: float,
    width: float,
    seed: int,
    burning: bool,
    is_foreground: bool = False,
) -> None:
    rng = random.Random(seed)
    lean = rng.uniform(-18, 18)
    top_x = x + lean
    top_y = ground_y - height

    trunk_dark = "#3D2B1F" if not burning else "#181314"
    trunk_hi = "#7A5846" if not burning else "#FF5A1F"

    # Batang & akar banir
    ctx.set_source_rgba(*_hex_rgba(trunk_dark, 1.0))
    ctx.move_to(x - width * 1.15, ground_y + 10)
    ctx.curve_to(
        x - width * 0.55,
        ground_y - height * 0.22,
        top_x - width * 0.42,
        ground_y - height * 0.65,
        top_x - width * 0.24,
        top_y + height * 0.14,
    )
    ctx.line_to(top_x + width * 0.24, top_y + height * 0.14)
    ctx.curve_to(
        top_x + width * 0.42,
        ground_y - height * 0.65,
        x + width * 0.55,
        ground_y - height * 0.22,
        x + width * 1.15,
        ground_y + 10,
    )
    ctx.close_path()
    ctx.fill()

    # Tekstur kulit kayu / retakan bara menyala saat terbakar
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for b_idx in range(3):
        frac = 0.22 + b_idx * 0.20
        bx = x + lean * frac + rng.uniform(-width * 0.16, width * 0.16)
        by = ground_y - height * frac
        ctx.set_source_rgba(*_hex_rgba(trunk_hi, 0.35 if not burning else 0.80))
        ctx.set_line_width(2.0 if not is_foreground else 3.2)
        ctx.move_to(bx, by)
        ctx.line_to(bx + rng.uniform(-3, 3), by - height * 0.12)
        ctx.stroke()

    # Cabang-cabang utama
    branches = [
        (-1, 0.54, rng.uniform(0.24, 0.34)),
        (1, 0.58, rng.uniform(0.24, 0.34)),
        (-1, 0.68, rng.uniform(0.18, 0.28)),
        (1, 0.72, rng.uniform(0.18, 0.26)),
    ]
    for side, h_frac, len_frac in branches:
        bx0 = x + lean * h_frac
        by0 = ground_y - height * h_frac
        bx1 = bx0 + side * height * len_frac
        by1 = by0 - height * rng.uniform(0.14, 0.20)
        ctrl_x = (bx0 + bx1) * 0.5
        ctrl_y = by0 - 8

        ctx.set_source_rgba(*_hex_rgba(trunk_dark, 1.0))
        ctx.set_line_width(max(3.5, width * 0.24))
        ctx.move_to(bx0, by0)
        _quad_to(ctx, ctrl_x, ctrl_y, bx1, by1)
        ctx.stroke()

        if burning:
            ctx.set_source_rgba(*_hex_rgba("#FF6B1A", 0.82))
            ctx.set_line_width(2.0)
            ctx.move_to(bx0, by0)
            _quad_to(ctx, ctrl_x, ctrl_y - 1.5, bx1, by1)
            ctx.stroke()

            fx0 = bx0 * 0.35 + bx1 * 0.65
            fy0 = by0 * 0.35 + by1 * 0.65
            ctx.set_source_rgba(*_hex_rgba("#181314", 1.0))
            ctx.set_line_width(max(2.2, width * 0.12))
            ctx.move_to(fx0, fy0)
            ctx.line_to(fx0 + side * 18, fy0 - 28)
            ctx.stroke()

    if not burning:
        leaf_palettes = [
            ("#2D6A4F", "#52B788", "#1B4332"),
            ("#3A7D44", "#6AB04C", "#1E4620"),
            ("#2A6F4E", "#48B57C", "#183D2B"),
        ]
        base_c, hi_c, sh_c = leaf_palettes[seed % len(leaf_palettes)]
        crown_r = height * (0.28 if is_foreground else 0.25)
        _draw_canopy_cluster(
            ctx,
            top_x - crown_r * 0.55,
            top_y + height * 0.24,
            crown_r * 0.88,
            crown_r * 0.72,
            rng,
            base_c,
            hi_c,
            sh_c,
        )
        _draw_canopy_cluster(
            ctx,
            top_x + crown_r * 0.55,
            top_y + height * 0.22,
            crown_r * 0.85,
            crown_r * 0.70,
            rng,
            base_c,
            hi_c,
            sh_c,
        )
        _draw_canopy_cluster(
            ctx,
            top_x,
            top_y + height * 0.08,
            crown_r * 1.05,
            crown_r * 0.84,
            rng,
            base_c,
            hi_c,
            sh_c,
        )
    else:
        ctx.set_source_rgba(*_hex_rgba("#181314", 1.0))
        ctx.set_line_width(max(3.5, width * 0.22))
        ctx.move_to(top_x, top_y + height * 0.16)
        ctx.line_to(top_x - 12, top_y + height * 0.02)
        ctx.move_to(top_x, top_y + height * 0.16)
        ctx.line_to(top_x + 18, top_y + height * 0.05)
        ctx.stroke()

        _draw_soft_glow(
            ctx,
            top_x,
            top_y + height * 0.28,
            width * 1.8,
            outer_hex="#EA580C",
            inner_hex="#FF9E00",
            peak_alpha=0.52,
            rings=5,
        )


def _draw_fern(
    ctx: cairo.Context,
    x: float,
    y: float,
    scale: float,
    burning: bool,
    seed: int,
) -> None:
    rng = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    fronds = 5 if not burning else 3
    for i in range(fronds):
        ang = -math.pi * 0.85 + (i / max(1, fronds - 1)) * math.pi * 0.7
        length = rng.uniform(46, 72) * (0.72 if burning else 1.0)
        ex = math.cos(ang) * length
        ey = math.sin(ang) * length
        col = "#2D6A4F" if (i % 2 == 0) else "#40916C"
        if burning:
            col = "#241C1B" if i % 2 == 0 else "#3D251E"
        ctx.set_source_rgba(*_hex_rgba(col, 0.96))
        ctx.set_line_width(7.0 if not burning else 4.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(0, 0)
        _quad_to(ctx, ex * 0.45, ey * 1.15, ex, ey)
        ctx.stroke()
    ctx.restore()


def generate_mid_forest_svg(out_path: Path, burning: bool) -> None:
    """Lapisan hutan tengah dengan pohon-pohon dipterokarpa Kalimantan dalam format SVG."""
    surface = cairo.SVGSurface(str(out_path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    ground_y = 895.0
    tree_specs = [
        (110, 440, 26, 201),
        (250, 520, 30, 202),
        (410, 470, 28, 203),
        (560, 560, 32, 204),
        (720, 460, 27, 205),
        (870, 540, 31, 206),
        (1030, 490, 29, 207),
        (1190, 580, 33, 208),
        (1350, 465, 26, 209),
        (1510, 535, 30, 210),
        (1680, 480, 28, 211),
        (1840, 555, 31, 212),
        (2010, 445, 25, 213),
        (2180, 490, 27, 214),
        (2390, 410, 23, 215),
        (2740, 390, 22, 216),
        (3040, 430, 24, 217),
    ]
    for tx, th, tw, seed in tree_specs:
        _draw_tree(ctx, tx, ground_y, th, tw, seed=seed, burning=burning, is_foreground=False)

    rng = random.Random(305)
    for fx in range(60, PANORAMA_W - 60, 125):
        if fx > 2350 and rng.random() < 0.45:
            continue
        _draw_fern(
            ctx,
            fx + rng.uniform(-18, 18),
            ground_y + 12,
            rng.uniform(0.80, 1.25),
            burning=burning,
            seed=fx,
        )

    surface.finish()


def generate_fg_forest_svg(out_path: Path, burning: bool) -> None:
    """Lapisan depan: tanah gambut, rumput/bara api, pohon hero & tunggul dalam SVG."""
    surface = cairo.SVGSurface(str(out_path), PANORAMA_W, PANORAMA_H)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, PANORAMA_W, PANORAMA_H)

    ground_top = 875.0

    # Pohon hero & tunggul
    for tx, th, tw, seed in [(150, 680, 42, 401), (940, 640, 38, 402), (1620, 660, 40, 403)]:
        _draw_tree(ctx, tx, ground_top + 25, th, tw, seed=seed, burning=burning, is_foreground=True)

    for sx, sh, sw in [(2260, 175, 34), (2940, 150, 30)]:
        ctx.set_source_rgba(*_hex_rgba("#4A3528" if not burning else "#171213", 1.0))
        ctx.move_to(sx - sw * 1.1, ground_top + 35)
        ctx.line_to(sx - sw * 0.55, ground_top - sh)
        ctx.line_to(sx - sw * 0.1, ground_top - sh + 22)
        ctx.line_to(sx + sw * 0.45, ground_top - sh - 12)
        ctx.line_to(sx + sw * 1.05, ground_top + 35)
        ctx.close_path()
        ctx.fill()
        if burning:
            ctx.set_source_rgba(*_hex_rgba("#FF5E14", 0.85))
            ctx.set_line_width(3.0)
            ctx.move_to(sx - sw * 0.3, ground_top - sh + 15)
            ctx.line_to(sx + sw * 0.3, ground_top - sh + 3)
            ctx.stroke()

    # Kontur tanah gambut utama
    def trace_ground_top() -> None:
        ctx.move_to(0, PANORAMA_H)
        ctx.line_to(0, ground_top)
        x = 0.0
        while x < PANORAMA_W:
            nx = min(PANORAMA_W, x + 220)
            y0 = ground_top + math.sin(x * 0.004) * 14
            y1 = ground_top + math.sin(nx * 0.004) * 14
            ctx.curve_to(x + 80, y0 - 10, nx - 80, y1 + 10, nx, y1)
            x = nx
        ctx.line_to(PANORAMA_W, PANORAMA_H)
        ctx.close_path()

    # Lapisan rumput atas (sehat) atau kerak abu (terbakar)
    ctx.set_source_rgba(*_hex_rgba("#3A7D44" if not burning else "#231D1D", 1.0))
    trace_ground_top()
    ctx.fill()

    # Lapisan tanah gambut dalam di bawah permukaan (tetap di dalam batas 1080px)
    ctx.set_source_rgba(*_hex_rgba("#2E1F16" if not burning else "#120D0D", 1.0))
    ctx.rectangle(0, ground_top + 48, PANORAMA_W, max(1.0, PANORAMA_H - (ground_top + 48)))
    ctx.fill()

    rng = random.Random(505)
    if not burning:
        for gx in range(20, PANORAMA_W, 44):
            gy = ground_top + math.sin(gx * 0.004) * 14 + 4
            col = "#52B788" if gx % 88 == 0 else "#40916C"
            ctx.set_source_rgba(*_hex_rgba(col, 0.95))
            ctx.set_line_width(3.2)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for blade in (-1, 0, 1):
                ctx.move_to(gx + blade * 5, gy + 4)
                _quad_to(
                    ctx,
                    gx + blade * 10,
                    gy - 16,
                    gx + blade * 14 + rng.uniform(-3, 3),
                    gy - rng.uniform(18, 30),
                )
                ctx.stroke()
    else:
        cx = 75.0
        while cx < PANORAMA_W - 75:
            cy = ground_top + math.sin(cx * 0.004) * 14 + rng.uniform(22, 85)
            _draw_soft_glow(
                ctx,
                cx,
                cy,
                rng.uniform(34, 58),
                outer_hex="#9D0208",
                inner_hex="#FF6D00",
                peak_alpha=0.45,
                rings=4,
            )
            ctx.set_source_rgba(*_hex_rgba("#FF9E00", 0.86))
            ctx.set_line_width(rng.uniform(1.8, 2.8))
            ctx.move_to(cx - rng.uniform(18, 34), cy + rng.uniform(-6, 6))
            ctx.line_to(cx - 2, cy + rng.uniform(-5, 5))
            ctx.line_to(cx + rng.uniform(16, 32), cy + rng.uniform(-7, 7))
            ctx.stroke()
            cx += rng.uniform(110, 210)

    surface.finish()


def generate_flame_svg(out_path: Path, variant: int) -> None:
    """Sprite lidah api vektor berlapis dengan pijar lembut."""
    w, h = 256, 384
    surface = cairo.SVGSurface(str(out_path), w, h)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, w, h)

    lean = (variant - 1) * 18.0
    _draw_soft_glow(
        ctx,
        w * 0.5,
        h * 0.66,
        w * 0.44,
        outer_hex="#D00000",
        inner_hex="#FF6B00",
        peak_alpha=0.42,
        rings=5,
    )

    def draw_teardrop(scale_x: float, scale_y: float, top_shift: float, col: str, alpha: float) -> None:
        ctx.save()
        ctx.translate(w * 0.5, h * 0.86)
        ctx.scale(scale_x, scale_y)
        ctx.set_source_rgba(*_hex_rgba(col, alpha))
        ctx.move_to(0, 12)
        ctx.curve_to(-92, 8, -96, -110, top_shift, -255)
        ctx.curve_to(96, -110, 92, 8, 0, 12)
        ctx.close_path()
        ctx.fill()
        ctx.restore()

    draw_teardrop(1.0, 1.0, lean, "#E85D04", 0.94)
    draw_teardrop(0.68, 0.76, lean * 0.7, "#FAA307", 0.95)
    draw_teardrop(0.38, 0.46, lean * 0.35, "#FFF3B0", 0.96)
    surface.finish()


def generate_smoke_puff_svg(out_path: Path) -> None:
    """Sprite gumpalan asap vektor berlapis lembut dengan bias pantulan cahaya api."""
    size = 320
    surface = cairo.SVGSurface(str(out_path), size, size)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, size, size)

    lobes = [
        (160, 150, 118, "#6E6764", "#9E9591", 0.42),
        (112, 165, 92, "#5E5755", "#877F7B", 0.36),
        (208, 162, 95, "#615A57", "#8A827E", 0.36),
        (158, 114, 96, "#7A7370", "#ADA4A0", 0.38),
        (160, 198, 84, "#7C523D", "#B87E59", 0.30),
    ]
    for lx, ly, lr, outer_c, inner_c, peak in lobes:
        _draw_soft_glow(ctx, lx, ly, lr, outer_hex=outer_c, inner_hex=inner_c, peak_alpha=peak, rings=8)

    surface.finish()


def generate_glow_dot_svg(out_path: Path, inner_col: str, outer_col: str, size: int = 128) -> None:
    """Sprite partikel pijar bulat SVG (bara api atau hotspot peta)."""
    surface = cairo.SVGSurface(str(out_path), size, size)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, size, size)
    c = size * 0.5
    _draw_soft_glow(ctx, c, c, c * 0.92, outer_hex=outer_col, inner_hex=inner_col, peak_alpha=0.88, rings=6)
    surface.finish()


def generate_ash_flake_svg(out_path: Path) -> None:
    """Sprite serpihan abu halus dalam SVG."""
    size = 48
    surface = cairo.SVGSurface(str(out_path), size, size)
    ctx = cairo.Context(surface)
    _draw_bounds_anchor(ctx, size, size)
    ctx.set_source_rgba(*_hex_rgba("#2B2628", 0.85))
    ctx.move_to(14, 18)
    ctx.line_to(28, 12)
    ctx.line_to(35, 25)
    ctx.line_to(22, 34)
    ctx.line_to(11, 27)
    ctx.close_path()
    ctx.fill()
    surface.finish()


def ensure_all_assets(force: bool = False) -> dict[str, Path]:
    """Pastikan seluruh aset vektor SVG Pycairo tersedia di assets/svg/generated/."""
    GENERATED_SVG_DIR.mkdir(parents=True, exist_ok=True)

    targets: dict[str, tuple[Path, Callable[[Path], None]]] = {
        "map_backdrop": (GENERATED_SVG_DIR / "map_backdrop.svg", generate_map_backdrop_svg),
        "hotspot_glow": (
            GENERATED_SVG_DIR / "hotspot_glow.svg",
            lambda p: generate_glow_dot_svg(p, "#FFE066", "#FF4D00", size=256),
        ),
        "sky_healthy": (
            GENERATED_SVG_DIR / "sky_healthy.svg",
            lambda p: generate_sky_details_svg(p, False),
        ),
        "sky_burning": (
            GENERATED_SVG_DIR / "sky_burning.svg",
            lambda p: generate_sky_details_svg(p, True),
        ),
        "forest_far_healthy": (
            GENERATED_SVG_DIR / "forest_far_healthy.svg",
            lambda p: generate_far_forest_svg(p, False),
        ),
        "forest_far_burnt": (
            GENERATED_SVG_DIR / "forest_far_burnt.svg",
            lambda p: generate_far_forest_svg(p, True),
        ),
        "forest_mid_healthy": (
            GENERATED_SVG_DIR / "forest_mid_healthy.svg",
            lambda p: generate_mid_forest_svg(p, False),
        ),
        "forest_mid_burnt": (
            GENERATED_SVG_DIR / "forest_mid_burnt.svg",
            lambda p: generate_mid_forest_svg(p, True),
        ),
        "forest_fg_healthy": (
            GENERATED_SVG_DIR / "forest_fg_healthy.svg",
            lambda p: generate_fg_forest_svg(p, False),
        ),
        "forest_fg_burnt": (
            GENERATED_SVG_DIR / "forest_fg_burnt.svg",
            lambda p: generate_fg_forest_svg(p, True),
        ),
        "flame_0": (GENERATED_SVG_DIR / "flame_0.svg", lambda p: generate_flame_svg(p, 0)),
        "flame_1": (GENERATED_SVG_DIR / "flame_1.svg", lambda p: generate_flame_svg(p, 1)),
        "flame_2": (GENERATED_SVG_DIR / "flame_2.svg", lambda p: generate_flame_svg(p, 2)),
        "smoke_puff": (GENERATED_SVG_DIR / "smoke_puff.svg", generate_smoke_puff_svg),
        "ember_spark": (
            GENERATED_SVG_DIR / "ember_spark.svg",
            lambda p: generate_glow_dot_svg(p, "#FFF3B0", "#FF7B00", size=64),
        ),
        "ash_flake": (GENERATED_SVG_DIR / "ash_flake.svg", generate_ash_flake_svg),
    }

    paths: dict[str, Path] = {}
    for key, (path, builder) in targets.items():
        if force or not path.exists():
            builder(path)
        paths[key] = path
    return paths
