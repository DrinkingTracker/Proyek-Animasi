from manim import *
from .utils import PATH_MATAHARI

def load_sun(tinggi, buff, buang_latar=True, path=PATH_MATAHARI):
    svg = SVGMobject(path)
    bagian = list(svg.submobjects)

    if buang_latar and len(bagian) > 1:
        w, h = svg.width, svg.height
        bagian = [m for m in bagian if not (m.width > 0.98 * w and m.height > 0.98 * h)]

    matahari = VGroup(*bagian)
    matahari.scale_to_fit_height(tinggi)
    matahari.to_corner(UR, buff=buff)
    return matahari