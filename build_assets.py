"""Script pembangun seluruh aset SVG Pycairo untuk Scene 6.

Jalankan sekali untuk menghasilkan seluruh file SVG ke assets/svg/ dan assets/svg/generated/,
atau otomatis dipanggil oleh scene6_kabut_asap.py jika file belum ada.
"""

from src.cairo_assets import ensure_all_assets

if __name__ == "__main__":
    paths = ensure_all_assets(force=True)
    print(f"Berhasil menghasilkan {len(paths)} aset SVG Pycairo untuk Scene 6.")
    for name, p in paths.items():
        print(f" - [{name}] -> {p.name} ({p.stat().st_size} bytes)")
