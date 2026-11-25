"""Script pembangun aset SVG Pycairo untuk Scene 5.

Jalankan sekali untuk menghasilkan seluruh layer SVG ke assets/svg/generated/,
atau otomatis dipanggil oleh scene5_kerusakan_hutan.py jika file belum ada.
"""

from src.cairo_assets import ensure_all_assets

if __name__ == "__main__":
    paths = ensure_all_assets(force=True)
    print(f"Berhasil menghasilkan {len(paths)} aset SVG Pycairo di assets/svg/generated/.")
