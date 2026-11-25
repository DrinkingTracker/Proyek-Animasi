# Scene 6 — Dampak Lanjutan: Kabut Asap Lintas Negara (Manim + Pycairo SVG)

Proyek animasi 2D edukatif bergaya **"Kok Bisa!"** murni berbasis vektor **SVG** menggunakan **Manim Community** dan **Pycairo** (`cairo.SVGSurface`), tanpa ketergantungan library Pillow.

Proyek ini merupakan kelanjutan langsung (sambungan cerita) dari **Scene 5: Kerusakan Hutan**.

---

## 🎬 Alur Cerita 3 Bagian (Scene 6)

1. **🌿 Bagian A — Kerusakan Ekosistem (Lanjutan langsung dari Scene 5)**
   - Hutan masih membara, dipenuhi kepulan asap tebal yang membubung tinggi.
   - Satwa liar endemik (Orangutan, Rusa Sambar, Burung Rangkong) tampak panik dan mengungsi lebih jauh menjauhi kebakaran.
   - Lapisan kabut asap pekat (*smog blanket*) semakin tebal menutupi seluruh vegetasi dan pepohonan.

2. **👨 Bagian B — Dampak ke Manusia**
   - Asap beracun bergerak perlahan menyelimuti kawasan permukiman warga (atap rumah, gedung perkantoran, tiang listrik).
   - Karakter **Stickman** bergaya *Kok Bisa!* berjalan di permukiman, tiba-tiba terbatuk sesak (*Uhuk! Uhuk!*), menutup hidung dan mulut dengan tangan, lalu memakai masker pelindung medis/N95.
   - Cut-in diagram anatomis paru-paru: partikel jelaga PM2.5 masuk ke saluran pernapasan, paru-paru mengalami spasme sesak dan berubah menghitam pekat dengan bronkus meradang merah.
   - Ikon & kartu peringatan dramatis **"ISPA"** (*Infeksi Saluran Pernapasan Akut*) muncul dengan data bahaya PM2.5 > 350 µg/m³.

3. **🗺️ Bagian C — Kabut Asap Lintas Negara & KTT Diplomatik**
   - Kamera zoom-out secara dramatis menampilkan **Peta Vektor Asia Tenggara** (Indonesia, Malaysia, Singapura, Brunei Darussalam).
   - Animasi aliran kabut asap lintas batas (*transboundary haze plume*) ditiup angin muson dari titik api di Kalimantan & Sumatera melintasi Selat Malaka dan Laut Cina Selatan menuju Malaysia, Singapura, hingga Brunei.
   - Ikon peringatan bahaya polusi udara (AQI / IPU darurat) muncul di tiap negara tetangga terdampak.
   - Transisi ke panggung **Konferensi Tingkat Tinggi (KTT) Diplomatik**: podium internasional dengan 4 bendera negara (🇮🇩, 🇲🇾, 🇸🇬, 🇧🇳) dan karakter diplomat stickman berjas formal yang menyampaikan nota protes dan menuntut penegakan hukum serta aksi bersama.

---

## 📂 Struktur Proyek

```text
scene6_kabut_asap/
├── .vscode/
│   ├── launch.json                 # Konfigurasi Run/Debug di VS Code (F5)
│   └── settings.json               # Pengaturan workspace Python
├── assets/
│   └── svg/
│       ├── deer.svg                # Rusa Sambar mengungsi (vektor)
│       ├── hornbill.svg            # Burung Rangkong terbang (vektor)
│       ├── orangutan.svg           # Orangutan Kalimantan berjalan mengungsi (vektor)
│       ├── stickman_normal.svg     # Stickman Kok Bisa berjalan santai (vektor)
│       ├── stickman_cough.svg      # Stickman batuk sesak menutup hidung (vektor)
│       ├── stickman_masked.svg     # Stickman memakai masker pelindung N95 (vektor)
│       ├── lungs_healthy.svg       # Ilustrasi anatomis paru-paru sehat (vektor)
│       ├── lungs_damaged.svg       # Ilustrasi anatomis paru-paru rusak jelaga (vektor)
│       ├── badge_ispa.svg          # Kartu peringatan dramatis ISPA & PM2.5 (vektor)
│       ├── peta_asia_tenggara.svg  # Peta Vektor Asia Tenggara resolusi tinggi
│       ├── conference_summit.svg   # Panggung KTT Diplomatik & bendera negara
│       ├── settlement_layer.svg    # Panorama permukiman warga berselimut kabut
│       └── generated/              # Layer hutan, langit, api, asap, bara & abu
├── src/
│   ├── __init__.py
│   ├── config.py                   # Palet warna, naskah dubbing, koordinat negara
│   ├── cairo_assets.py             # Generator vektor SVG Pycairo murni
│   └── scene6_kabut_asap.py        # Logika animasi utama Manim Scene 6
├── build_assets.py                 # Script pembangun aset SVG Pycairo
├── main.py                         # Entry point cepat (Run / F5 di VS Code)
└── requirements.txt
```

---

## 🚀 Cara Menjalankan di Visual Studio Code

1. **Ekstrak** `scene6_kabut_asap.zip` lalu buka foldernya di VS Code (**File > Open Folder...**).
2. Pastikan dependensi telah terpasang:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Opsional)** Bangun ulang aset SVG:
   ```bash
   python build_assets.py
   ```
   *(Aset juga otomatis dibangun jika belum ada saat scene dijalankan).*
4. **Render Animasi**:
   - Tekan **F5** di VS Code, **atau**
   - Jalankan lewat terminal:
     - Preview cepat (480p): `manim -pql src/scene6_kabut_asap.py Scene6KabutAsap`
     - Kualitas HD (1080p 60fps): `manim -pqh src/scene6_kabut_asap.py Scene6KabutAsap`

---

## 🎙️ Sinkronisasi Dubbing (Tanpa Audio)

Di `src/config.py`, opsi `SHOW_SUBTITLES = True` menampilkan kartu panduan narasi di bawah video untuk mempermudah sinkronisasi waktu saat perekaman suara (dubbing). Jika ingin merender tanpa subtitle:
```python
SHOW_SUBTITLES = False
```

### Naskah Dubbing Scene 6:
> **Segmen 1 (0.0s – 8.5s):**
> *"Dampak kebakaran tidak berhenti di tengah hutan lebat. Asap pekat terus membubung tinggi, menelan vegetasi yang tersisa, dan memaksa satwa liar mengungsi lebih jauh."*
>
> **Segmen 2 (8.5s – 21.5s):**
> *"Gumpalan asap beracun ini kemudian menyelimuti permukiman warga. Partikel berbahaya dan karbon monoksida masuk ke saluran pernapasan, memicu lonjakan kasus ISPA, terutama pada kelompok rentan."*
>
> **Segmen 3 (21.5s – 35.0s):**
> *"Ditiup angin kencang, kabut asap melintasi batas negara menuju Malaysia, Singapura, hingga Brunei Darussalam. Kualitas udara anjlok ke level berbahaya, memicu protes diplomatik dan desakan nyata aksi bersama."*
