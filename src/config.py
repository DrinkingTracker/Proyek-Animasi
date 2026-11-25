"""Konfigurasi global warna, path aset SVG, durasi segmen dubbing, dan opsi render."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SVG_DIR = ASSETS_DIR / "svg"
GENERATED_SVG_DIR = SVG_DIR / "generated"

MAP_SVG_PATH = SVG_DIR / "peta_indonesia.svg"

# Toggle subtitle panduan dubbing di bagian bawah layar.
# Ubah menjadi False saat Anda siap menggabungkan audio dubbing asli.
SHOW_SUBTITLES = True

# Koordinat Pulau Kalimantan pada peta_indonesia.svg (viewBox 1024 x 359)
MAP_PIXEL_SIZE = (1024, 359)
KALIMANTAN_PIXEL_CENTER = (423.0, 128.0)

# Titik-titik hotspot kebakaran di Kalimantan dalam koordinat viewBox peta (1024 x 359)
KALIMANTAN_HOTSPOTS_PX = [
    (405.0, 165.0),  # Kalimantan Tengah (lahan gambut)
    (360.0, 148.0),  # Kalimantan Barat
    (438.0, 182.0),  # Kalimantan Selatan
    (478.0, 138.0),  # Kalimantan Timur
    (462.0, 96.0),   # Kalimantan Utara
]

# Palet warna bergaya editorial ("Kok Bisa!" meets atmospheric 2D vector realism)
PALETTE = {
    "bg_cream": "#F4F0E8",
    "bg_ocean": "#E3ECE8",
    "ink_dark": "#1F2933",
    "ink_muted": "#4A5568",
    "map_green": "#6E9877",
    "accent_emerald": "#2D6A4F",
    "accent_amber": "#F48C06",
    "accent_fire": "#E85D04",
    "accent_crimson": "#D00000",
    "text_light": "#F8F9FA",
    "card_bg": "#1B232A",
}

# Naskah dubbing per segmen (untuk sinkronisasi animasi & opsional subtitle panduan)
DUBBING_SEGMENTS = [
    {
        "id": "beat_1_map_appear",
        "start": 0.0,
        "end": 5.8,
        "text": "Ketika api mulai menyebar, kawasan hutan menjadi korban utama.",
    },
    {
        "id": "beat_2_zoom_kalimantan",
        "start": 5.8,
        "end": 14.0,
        "text": (
            "Salah satu wilayah yang rentan terhadap ancaman ini adalah Kalimantan,\n"
            "yang memiliki kawasan hutan tropis dan lahan gambut yang luas."
        ),
    },
    {
        "id": "beat_3_forest_fire",
        "start": 14.0,
        "end": 23.5,
        "text": (
            "Kebakaran menyebabkan pepohonan hangus, vegetasi rusak,\n"
            "dan habitat satwa liar kehilangan tempat tinggalnya."
        ),
    },
    {
        "id": "beat_4_wildlife_loss",
        "start": 23.5,
        "end": 33.5,
        "text": (
            "Tidak hanya menghilangkan tutupan hutan, kebakaran juga mengganggu\n"
            "keseimbangan ekosistem dan mengancam kelangsungan hidup berbagai spesies."
        ),
    },
]
