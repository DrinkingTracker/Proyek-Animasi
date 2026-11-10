import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from utils import load_trees, ambil_pohon, load_sun, load_map, summon_trees

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

        #  transisi: hutan -> peta Indonesia 
        matahari.clear_updaters()
        self.play(
            FadeOut(hutan, shift=DOWN * 0.5),
            FadeOut(matahari, shift=UP * 0.5),
            run_time=1.5,
        )
 
        peta, provinsi = load_map(lebar=12, warna="#E6EDE0")
        self.play(LaggedStart(*[FadeIn(prov, scale=0.9) for prov in peta], lag_ratio=0.04), run_time=2)
        self.wait(0.5)
 
        # pohon muncul di berbagai daerah , kode daerah dari SVG
        sebaran = {
            "IDAC": 2, "IDSU": 3, "IDSB": 2, "IDRI": 3, "IDJA": 2, "IDSS": 3, "IDBE": 1, "IDLA": 1,
            "IDKB": 4, "IDKT": 4, "IDKS": 2, "IDKI": 4, "IDKU": 2,
            "IDJB": 1, "IDJT": 2, "IDJI": 2, "IDNB": 1, "IDNT": 2,
            "IDSN": 2, "IDST": 3, "IDSG": 2, "IDSA": 1,
            "IDMA": 2, "IDMU": 1, "IDPA": 5, "IDPB": 2,
        }
        hutan_peta = summon_trees(pohon, provinsi, sebaran)
        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in hutan_peta], lag_ratio=0.05), run_time=4)
        self.wait(2)



        


