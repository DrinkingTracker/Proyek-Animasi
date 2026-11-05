import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from utils import load_trees, ambil_pohon, load_sun

class opening1(Scene):
     def construct(self):
        pohon, daun = load_trees()
        matahari = load_sun(2, 0.5)

        susunan = [
            ("pohon1", 3.0, -5, -3), # (nama, tinggi, posisi x, posisi y dasar pohon)
            ("pohon2", 2.2, -4, -3),
            ("pohon3", 2.6, -3, -3),
            ("pohon4", 3.4, -2, -3),
            ("pohon5", 2.8, -1, -3),
            ("pohon6", 2.4,  1, -3),
            ("pohon7", 2.5,  2, -3),
            ("pohon8", 3.0,  4, -3),
        ]

        hutan = VGroup()
        for nama, tinggi, x, y in susunan:
            p = ambil_pohon(pohon, nama, tinggi)
            p.move_to([x, y, 0], aligned_edge=DOWN)   # dasar pohon di y
            hutan.add(p)

        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in hutan], lag_ratio=0.2))
        self.wait(1)

        self.play(FadeIn(matahari, shift=DOWN * 0.5))
        matahari.add_updater(lambda m, dt: m.rotate(0.5 * dt))   
        self.wait(5) # berputar pelan
         



        


