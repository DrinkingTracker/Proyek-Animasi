# Scene 5 — Dampak Pertama: Kerusakan Hutan (Manim + Pycairo SVG)

Proyek animasi 2D edukatif bergaya **"Kok Bisa!"** murni berbasis vektor **SVG** menggunakan **Manim Community** dan **Pycairo** (`cairo.SVGSurface`), tanpa ketergantungan library Pillow.

## Struktur Proyek

```text
scene5_kerusakan_hutan/
├── .vscode/
│   ├── launch.json                 # Konfigurasi Run/Debug di VS Code
│   └── settings.json               # Pengaturan workspace Python
├── assets/
│   └── svg/
│       ├── peta_indonesia.svg      # Peta Indonesia vektor SVG (di-trace dari PNG)
│       ├── orangutan.svg           # Ilustrasi 2D Orangutan Kalimantan (menghadap kanan)
│       ├── hornbill.svg            # Ilustrasi 2D Burung Enggang / Rangkong
│       ├── deer.svg                # Ilustrasi 2D Rusa Sambar (menghadap kanan)
│       └── generated/              # Layer hutan, langit, api, asap & bara (SVG Pycairo)
├── src/
│   ├── config.py                   # Palet warna, koordinat Kalimantan, naskah dubbing
│   ├── cairo_assets.py             # Generator aset vektor SVG beresolusi tinggi (Pycairo)
│   └── scene5_kerusakan_hutan.py   # Animasi utama Scene 5 (Manim)
├── build_assets.py                 # Script terpisah untuk membangun ulang aset SVG Pycairo
├── main.py                         # Entry point cepat (Run Python File / F5)
└── requirements.txt
```

## Cara Menjalankan di Visual Studio Code

1. **Ekstrak** file ZIP ini lalu buka folder `scene5_kerusakan_hutan` di VS Code (**File > Open Folder...**).
2. Pastikan dependensi terpasang di environment Python Anda:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Opsional)** Bangun ulang aset SVG Pycairo secara manual:
   ```bash
   python build_assets.py
   ```
   *(Catatan: `scene5_kerusakan_hutan.py` juga otomatis membangun aset jika folder `assets/svg/generated/` belum terisi).*
4. **Render Animasi**:
   - Tekan **F5** di VS Code, **atau**
   - Jalankan via terminal terintegrasi VS Code:
     - Preview cepat (480p): `manim -pql src/scene5_kerusakan_hutan.py Scene5KerusakanHutan`
     - Kualitas HD (1080p 60fps): `manim -pqh src/scene5_kerusakan_hutan.py Scene5KerusakanHutan`

## Sinkronisasi Dubbing (Tanpa Audio)

Di `src/config.py`, `SHOW_SUBTITLES = True` menampilkan teks panduan narasi di bagian bawah video agar Anda mudah mencocokkan tempo saat mengisi suara (dubbing). Setelah siap untuk render final dengan audio eksternal, cukup ubah:

```python
SHOW_SUBTITLES = False
```

Naskah dubbing yang disinkronkan:
> *"Ketika api mulai menyebar, kawasan hutan menjadi korban utama. Salah satu wilayah yang rentan terhadap ancaman ini adalah Kalimantan, yang memiliki kawasan hutan tropis dan lahan gambut yang luas. Kebakaran menyebabkan pepohonan hangus, vegetasi rusak, dan habitat satwa liar kehilangan tempat tinggalnya. Tidak hanya menghilangkan tutupan hutan, kebakaran juga mengganggu keseimbangan ekosistem dan mengancam kelangsungan hidup berbagai spesies."*
