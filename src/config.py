"""Konfigurasi global Scene 6 — Dampak Lanjutan: Kabut Asap Lintas Negara."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SVG_DIR = ASSETS_DIR / "svg"
GENERATED_SVG_DIR = SVG_DIR / "generated"
IMAGES_DIR = ASSETS_DIR / "images"

# File path untuk aset utama
MAP_SEA_PATH = IMAGES_DIR / "peta_asia_tenggara.jpg"
STICKMAN_NORMAL_PATH = SVG_DIR / "stickman_normal.svg"
STICKMAN_COUGH_PATH = SVG_DIR / "stickman_cough.svg"
STICKMAN_MASKED_PATH = SVG_DIR / "stickman_masked.svg"
LUNGS_HEALTHY_PATH = SVG_DIR / "lungs_healthy.svg"
LUNGS_DAMAGED_PATH = SVG_DIR / "lungs_damaged.svg"
BADGE_ISPA_PATH = SVG_DIR / "badge_ispa.svg"
CONFERENCE_SUMMIT_PATH = SVG_DIR / "conference_summit.svg"
SETTLEMENT_LAYER_PATH = SVG_DIR / "settlement_layer.svg"

# Toggle subtitle panduan dubbing di bagian bawah layar.
SHOW_SUBTITLES = True

# Palet warna editorial bergaya "Kok Bisa!"
PALETTE = {
    "bg_cream": "#F4F0E8",
    "bg_ocean": "#065FA8",
    "bg_smog": "#E5D9C5",
    "ink_dark": "#1F2933",
    "ink_muted": "#4A5568",
    "accent_emerald": "#2D6A4F",
    "accent_amber": "#F48C06",
    "accent_fire": "#E85D04",
    "accent_crimson": "#D00000",
    "smoke_haze": "#D4C5A9",
    "smoke_dark": "#4A4643",
    "text_light": "#F8F9FA",
    "card_bg": "#1B232A",
    "lungs_pink": "#F28482",
    "lungs_soot": "#353238",
    "lungs_bronchi": "#9E2A2B",
    "warning_yellow": "#FFB703",
    "warning_red": "#E63946",
}

# Naskah dubbing per segmen untuk sinkronisasi animasi & subtitle
DUBBING_SEGMENTS = [
    {
        "id": "beat_1_forest_haze",
        "start": 0.0,
        "end": 8.5,
        "text": (
            "Dampak kebakaran tidak berhenti di tengah hutan lebat.\n"
            "Asap pekat terus membubung tinggi, menelan vegetasi yang tersisa,\n"
            "dan memaksa satwa liar mengungsi lebih jauh."
        ),
    },
    {
        "id": "beat_2_human_impact_ispa",
        "start": 8.5,
        "end": 21.5,
        "text": (
            "Gumpalan asap beracun ini kemudian menyelimuti seluruh permukiman warga.\n"
            "Partikel berbahaya dan karbon monoksida masuk ke saluran pernapasan,\n"
            "memicu lonjakan kasus ISPA, terutama pada kelompok rentan."
        ),
    },
    {
        "id": "beat_3_transboundary_conference",
        "start": 21.5,
        "end": 35.0,
        "text": (
            "Ditiup angin muson, kabut asap melintasi batas negara menuju Malaysia,\n"
            "Singapura, hingga Brunei Darussalam. Kualitas udara anjlok ke level berbahaya,\n"
            "memicu protes diplomatik dan desakan nyata aksi bersama."
        ),
    },
]

# Ukuran gambar peta Asia Tenggara pengguna
SEA_MAP_SIZE = (1024, 577)

# Titik-titik hotspot kebakaran hutan aktif (thermal satellite hotspots)
HOTSPOTS_SEA_PX = [
    {"name": "Kalteng (Palangka Raya)", "px": (440.0, 440.0), "color": "#FF2200"},
    {"name": "Kalbar (Ketapang)", "px": (395.0, 435.0), "color": "#FF4400"},
    {"name": "Kalsel (Banjarmasin)", "px": (465.0, 465.0), "color": "#FF5500"},
    {"name": "Riau (Sumatera)", "px": (155.0, 415.0), "color": "#FF1100"},
    {"name": "Jambi (Sumatera)", "px": (175.0, 445.0), "color": "#FF3300"},
    {"name": "Sumsel (Palembang)", "px": (195.0, 470.0), "color": "#FF4400"},
]

# Target negara terdampak kabut asap lintas batas (viewBox 1024 x 577)
TARGET_COUNTRIES_SEA_PX = [
    {
        "country": "Singapura",
        "code": "SG",
        "px": (235.0, 400.0),
        "status": "AQI 220+",
        "desc": "Sangat Tidak Sehat",
        "alert_color": "#D00000",
    },
    {
        "country": "Malaysia (Kuala Lumpur)",
        "code": "MY",
        "px": (185.0, 360.0),
        "status": "IPU 210+",
        "desc": "Darurat Asap",
        "alert_color": "#E85D04",
    },
    {
        "country": "Malaysia (Sarawak)",
        "code": "MY-SWK",
        "px": (410.0, 375.0),
        "status": "IPU 205+",
        "desc": "Sekolah Diliburkan",
        "alert_color": "#E85D04",
    },
    {
        "country": "Brunei Darussalam",
        "code": "BN",
        "px": (470.0, 350.0),
        "status": "Waspada",
        "desc": "Kabut Asap Lintas Batas",
        "alert_color": "#F48C06",
    },
]
