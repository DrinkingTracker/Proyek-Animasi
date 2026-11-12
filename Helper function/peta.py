def load_map(lebar=12, warna=None, path=PATH_PETA):
    teks = open(path, encoding="utf-8").read()
    ids = re.findall(r'<path\b[^>]*?\bid="([^"]+)"', teks)   # urutan id = urutan bentuk
 
    svg = SVGMobject(path)
    bagian = list(svg.submobjects)[:len(ids)]   # sisanya lingkaran penanda, dibuang
 
    peta = VGroup(*bagian)
    peta.scale_to_fit_width(lebar).move_to(ORIGIN)
    if warna is not None:
        peta.set_fill(warna)
    return peta, dict(zip(ids, bagian))
 
 
def _di_dalam(titik, poligon_list):
    """Uji titik di dalam bentuk (ray casting, aturan even-odd)."""
    x, y = titik
    di_dalam = False
    for poly in poligon_list:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                di_dalam = not di_dalam
    return di_dalam
 
 
def random_point(provinsi, jumlah, jarak_min=0.3, seed=0):
    """Titik-titik acak (x, y) yang berada di dalam satu provinsi."""
    rng = random.Random(seed)
    poligon = [sp[::4, :2] for sp in provinsi.get_subpaths()]   # titik jangkar tiap kurva
    semua = np.vstack(poligon)
    x_min, y_min = semua.min(axis=0)
    x_max, y_max = semua.max(axis=0)
 
    hasil = []
    for _ in range(2000):
        if len(hasil) >= jumlah:
            break
        t = (rng.uniform(x_min, x_max), rng.uniform(y_min, y_max))
        if not _di_dalam(t, poligon):
            continue
        if all((t[0] - h[0]) ** 2 + (t[1] - h[1]) ** 2 > jarak_min ** 2 for h in hasil):
            hasil.append(t)
    return hasil
 
 
def summon_trees(pohon, provinsi, sebaran, tinggi=(0.35, 0.6), seed=1):
    rng = random.Random(seed)
    nama_pohon = list(pohon.keys())
    hutan = VGroup()
    for k, (id_prov, jumlah) in enumerate(sebaran.items()):
        for (x, y) in random_point(provinsi[id_prov], jumlah, seed=seed + k):
            p = ambil_pohon(pohon, rng.choice(nama_pohon), rng.uniform(*tinggi))
            p.move_to([x, y, 0], aligned_edge=DOWN)   # dasar pohon di titik itu
            hutan.add(p)
    hutan.submobjects.sort(key=lambda p: -p.get_bottom()[1])
    return hutan