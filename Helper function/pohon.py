NAMA_POHON = [ "pohon1", "pohon2", "pohon3", "pohon4", "pohon5", "pohon6", "pohon7", "pohon8" ]

def load_trees(path=PATH_POHON):
    svg = SVGMobject(path)
    crowns, trunks, leaves = [], [], []

    for m in svg.submobjects:
        r, g, b = m.get_fill_color().to_rgb()
        if r > 0.9:                    
            continue
        elif r < 0.1 and g > 0.5:      
            crowns.append(m)
        elif r < 0.3 and g < 0.2:      
            trunks.append(m)
        else:                          
            leaves.append(m)

    pohon = {}
    for nama, c in zip(NAMA_POHON, crowns):
        # batang di baris yang sama (atas/bawah), lalu pilih x terdekat
        same_row = [t for t in trunks if (t.get_y() > 0) == (c.get_y() > 0)]
        t = min(same_row, key=lambda t: abs(t.get_x() - c.get_x()))
        pohon[nama] = VGroup(c, t)     # [0] = tajuk, [1] = batang

    return pohon, VGroup(*leaves)

def ambil_pohon(pohon, nama, tinggi):
    """Salinan satu pohon utuh dengan tinggi tertentu."""
    return pohon[nama].copy().scale_to_fit_height(tinggi)