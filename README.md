# Asset Converter

**Convertssor** adalah aplikasi desktop berbasis **Python + CustomTkinter** untuk melakukan **convert, kompresi, resize, dan optimasi file gambar serta video secara massal**.

Aplikasi ini dibuat untuk mempermudah proses optimasi asset website, portfolio, landing page, UI design showcase, dokumentasi produk, dan kebutuhan digital lainnya. Cukup pilih satu folder utama, lalu aplikasi akan memproses semua file gambar/video di dalam folder tersebut, termasuk file yang berada di dalam subfolder.

---

## Fitur Utama

### Image Converter

- Convert gambar secara massal.
- Kompres gambar dengan pengaturan quality.
- Support recursive folder processing.
- Bisa memproses gambar di folder utama dan subfolder.
- Bisa mempertahankan struktur folder asli.
- Bisa resize gambar berdasarkan max width.
- Bisa overwrite file output jika diperlukan.
- Bisa skip file yang sudah pernah dikonversi.
- Support transparansi untuk format yang mendukung.
- Support output format:
  - WEBP
  - JPEG / JPG
  - PNG
  - AVIF
  - BMP
  - TIFF

### Video Converter

- Convert video secara massal.
- Kompres video dengan pengaturan CRF.
- Support recursive folder processing.
- Bisa mempertahankan struktur folder asli.
- Bisa overwrite file output jika diperlukan.
- Bisa mute / menghapus audio dari video.
- Bisa mengubah resolusi video.
- Bisa memilih codec video.
- Support output format:
  - MP4
  - WEBM
  - MKV
  - MOV
  - AVI
  - Custom extension

### Video Codec

- Auto
- H.264
- H.265
- VP9
- AV1
- MPEG-4

### Video Scale

- Original
- 2160p
- 1440p
- 1080p
- 720p
- 480p
- 360p

---

## Struktur Folder Project

Struktur project yang direkomendasikan:

```text
Auto-convert/
├─ App.py
├─ install.bat
├─ run.bat
├─ requirements.txt
├─ README.md
└─ .gitignore
```

Keterangan:

| File               | Fungsi                                                                   |
| ------------------ | ------------------------------------------------------------------------ |
| `App.py`           | File utama aplikasi                                                      |
| `install.bat`      | Installer otomatis untuk Python, FFmpeg, dependency, dan menjalankan app |
| `run.bat`          | Menjalankan aplikasi dan menginstall dependency Python jika belum ada    |
| `requirements.txt` | Daftar dependency Python                                                 |

---

## Cara Install Langsung Pakai

Langkah:

1. Download / clone repository ini.
2. Pastikan `install.bat` berada satu folder dengan `App.py`.
3. Double click `install.bat`.
4. Tunggu proses instalasi selesai.
5. Aplikasi akan otomatis terbuka.

`install.bat` akan otomatis:

- Mengecek apakah Python sudah tersedia.
- Menginstall Python jika belum tersedia.
- Mengecek apakah FFmpeg sudah tersedia.
- Menginstall Gyan.FFmpeg jika belum tersedia.
- Membuat virtual environment `.venv`.
- Menginstall dependency Python.
- Menjalankan aplikasi.

---

## Cara Menjalankan Aplikasi

Jika dependensi sudah terinstall bisa langsung menggunakan:

```text
run.bat
```

Langkah:

1. Pastikan `run.bat` berada satu folder dengan `App.py`.
2. Double click `run.bat`.
3. Aplikasi akan berjalan.

`run.bat` akan otomatis:

- Membuat virtual environment jika belum ada.
- Menginstall dependency Python.
- Mengecek FFmpeg.
- Menjalankan aplikasi.

---

## Instalasi Manual

Jika ingin menjalankan secara manual lewat terminal:

### 1. Clone Repository

```bash
git clone https://github.com/Mubax5/Convertssor.git
cd Convertssor
```

### 2. Buat Virtual Environment

```bash
python -m venv .venv
```

### 3. Aktifkan Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependency

```bash
pip install -r requirements.txt
```

Atau install langsung:

```bash
pip install customtkinter pillow pillow-avif-plugin
```

### 5. Jalankan Aplikasi

```bash
python App.py
```

---

## Requirements

### Wajib

- Windows 10 / Windows 11
- Python 3.10 atau lebih baru
- Koneksi internet saat proses install dependency

### Untuk Fitur Video

Fitur video membutuhkan **FFmpeg**.

Jika menggunakan `install.bat`, FFmpeg akan dicoba diinstall otomatis menggunakan:

```bash
winget install Gyan.FFmpeg
```

Cek apakah FFmpeg sudah terinstall:

```bash
ffmpeg -version
```

Jika command tersebut menampilkan versi FFmpeg, berarti FFmpeg sudah siap digunakan.

---

## Dependency Python

Isi file `requirements.txt`:

```txt
customtkinter
pillow
pillow-avif-plugin
```

Penjelasan:

| Dependency           | Fungsi                                       |
| -------------------- | -------------------------------------------- |
| `customtkinter`      | Membuat tampilan GUI modern                  |
| `pillow`             | Membaca, convert, resize, dan kompres gambar |
| `pillow-avif-plugin` | Menambahkan support AVIF pada Pillow         |

---

## Cara Menggunakan Aplikasi

### Convert dan Kompres Gambar

1. Buka aplikasi.
2. Masuk ke tab **Images**.
3. Pilih **Input Folder**.
4. Pilih **Output Folder**.
5. Pilih output format, misalnya `WEBP`.
6. Atur quality.
7. Aktifkan opsi tambahan jika perlu:
   - Pertahankan struktur folder
   - Overwrite jika file sudah ada
   - Resize max width
   - Lossless jika format mendukung
8. Klik **Start Image Convert**.
9. Tunggu sampai proses selesai.

### Convert dan Kompres Video

1. Buka aplikasi.
2. Masuk ke tab **Videos**.
3. Pilih **Input Folder**.
4. Pilih **Output Folder**.
5. Pilih output format, misalnya `mp4`.
6. Pilih codec, misalnya `Auto` atau `H.264`.
7. Atur CRF.
8. Pilih preset dan scale jika diperlukan.
9. Atur audio bitrate atau aktifkan mute.
10. Klik **Start Video Convert**.
11. Tunggu sampai proses selesai.

---

## Penjelasan Quality dan CRF

### Image Quality

Quality digunakan untuk mengatur keseimbangan antara ukuran file dan kualitas visual.

```text
Quality tinggi = kualitas lebih bagus, ukuran file lebih besar
Quality rendah = ukuran file lebih kecil, kualitas bisa turun
```

Rekomendasi:

| Kebutuhan             | Quality  |
| --------------------- | -------- |
| Portfolio / website   | 85 - 92  |
| Preview ringan        | 70 - 85  |
| Arsip kualitas tinggi | 92 - 100 |

### Video CRF

CRF digunakan untuk mengatur kompresi video.

```text
CRF kecil = kualitas lebih tinggi, file lebih besar
CRF besar = file lebih kecil, kualitas lebih rendah
```

Rekomendasi:

| Kebutuhan       | CRF     |
| --------------- | ------- |
| Kualitas tinggi | 18 - 23 |
| Web portfolio   | 23 - 28 |
| File kecil      | 28 - 34 |
| Sangat kecil    | 34 - 40 |

---

## Format yang Didukung

### Input Gambar

Aplikasi akan mendeteksi file dengan extension:

```text
.jpg
.jpeg
.png
.webp
.bmp
.tiff
.tif
.gif
.avif
.ico
.ppm
.pgm
.pbm
```

Catatan:

- Untuk GIF animasi, aplikasi mengambil frame pertama.
- Untuk AVIF, install `pillow-avif-plugin`.
- Untuk JPEG/BMP yang tidak mendukung transparansi, background transparan akan dibuat putih.

### Output Gambar

```text
.webp
.jpg
.png
.avif
.bmp
.tiff
```

### Input Video

Aplikasi akan mendeteksi file dengan extension:

```text
.mp4
.mov
.mkv
.avi
.webm
.flv
.wmv
.m4v
.mpeg
.mpg
.3gp
.ts
.mts
.m2ts
```

### Output Video

```text
.mp4
.webm
.mkv
.mov
.avi
custom extension
```

---

## Troubleshooting

### Python Tidak Ditemukan

Jika muncul pesan:

```text
Python tidak ditemukan
```

Solusi:

1. Install Python dari website resmi.
2. Saat install, centang opsi:

```text
Add python.exe to PATH
```

3. Tutup terminal.
4. Jalankan ulang `install.bat`.

Jika menggunakan Windows 10/11, kamu juga bisa menjalankan `install.bat` agar Python dicoba diinstall otomatis via winget.

---

### Winget Tidak Ditemukan

Jika muncul pesan:

```text
Winget tidak ditemukan
```

Solusi:

1. Buka Microsoft Store.
2. Cari **App Installer**.
3. Install atau update **App Installer**.
4. Jalankan ulang `install.bat`.

---

### FFmpeg Tidak Ditemukan

Jika muncul pesan:

```text
FFmpeg belum ditemukan
```

Fitur gambar tetap bisa digunakan, tetapi fitur video membutuhkan FFmpeg.

Install manual dengan command:

```bash
winget install Gyan.FFmpeg
```

Setelah install:

1. Tutup terminal.
2. Restart PC jika perlu.
3. Jalankan ulang aplikasi.

Cek FFmpeg:

```bash
ffmpeg -version
```

---

### Dependency Gagal Install

Jika muncul error saat install dependency:

```text
Gagal install dependency
```

Solusi:

1. Pastikan koneksi internet aktif.
2. Jalankan ulang `install.bat`.
3. Jika masih gagal, coba manual:

```bash
python -m pip install --upgrade pip
pip install customtkinter pillow pillow-avif-plugin
```

---

### AVIF Tidak Bisa Dibuka

Pastikan plugin AVIF sudah terinstall:

```bash
pip install pillow-avif-plugin
```

Jika menggunakan `run.bat` atau `install.bat`, dependency ini akan diinstall otomatis.

---

## Kontribusi

Kontribusi terbuka untuk siapa pun.

Cara kontribusi:

1. Fork repository.
2. Buat branch baru.
3. Lakukan perubahan.
4. Commit perubahan.
5. Push ke branch.
6. Buat pull request.

Contoh:

```bash
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

---
