# BPJS Checker - Full Otomatis

Script Python untuk mengecek data BPJS melalui API jaga.id dengan captcha solving otomatis menggunakan OCR.

## Fitur

✅ **Full Otomatis** - Tidak perlu input manual
✅ **Captcha Solving** - Menggunakan OCR (pytesseract) untuk solve captcha otomatis
✅ **Batch Processing** - Proses multiple NIK dari file CSV
✅ **Auto Retry** - Otomatis retry jika captcha salah
✅ **Export Results** - Simpan hasil ke JSON dan CSV
✅ **Progress Tracking** - Tampilan progress real-time

## Cara Kerja

1. **Generate Captcha** - Request ke API untuk mendapatkan captcha image dan UUID
2. **Solve Captcha** - Gunakan OCR untuk membaca captcha otomatis
3. **Check BPJS** - Query data BPJS dengan NIK, tanggal lahir, dan captcha
4. **Auto Retry** - Jika captcha salah, otomatis generate dan solve ulang
5. **Save Results** - Simpan semua hasil ke file

## Instalasi

### 1. Install Dependencies Python

```bash
pip install pillow pytesseract requests
```

### 2. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Amazon Linux 2023:**
```bash
sudo dnf install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer dari: https://github.com/UB-Mannheim/tesseract/wiki

## Penggunaan

### Mode 1: Single/Multiple NIK (Hardcoded)

Edit file `bpjs_checker.py` bagian `data_to_check`:

```python
data_to_check = [
    {'nik': '3317110608050001', 'tgl_lahir': '2005-08-06'},
    {'nik': '1234567890123456', 'tgl_lahir': '1990-01-01'},
    # Tambahkan NIK lain di sini
]
```

Jalankan:
```bash
python bpjs_checker.py
```

### Mode 2: Batch Processing dari CSV

1. **Buat file CSV input** (contoh: `input_nik.csv`):

```csv
nik,tgl_lahir
3317110608050001,2005-08-06
1234567890123456,1990-01-01
9876543210987654,1985-12-25
```

2. **Jalankan batch processor**:

```bash
# Dengan default bearer token
python bpjs_checker_batch.py input_nik.csv

# Dengan custom bearer token
python bpjs_checker_batch.py input_nik.csv YOUR_BEARER_TOKEN
```

3. **Atau buat sample CSV**:

```bash
python bpjs_checker_batch.py --create-sample
```

## Output

### 1. Console Output

```
╔══════════════════════════════════════════════════════════════╗
║           BPJS CHECKER - FULL OTOMATIS                       ║
║           Powered by OCR Captcha Solving                     ║
╚══════════════════════════════════════════════════════════════╝

============================================================
Checking NIK: 3317110608050001 | DOB: 2005-08-06
============================================================

Attempt 1/5
✓ Captcha generated: 6aacde23-7b3a-4270-bae4-dbf905f5661f
✓ Captcha solved: K633v
  Checking BPJS (attempt 1/3)...
✓ BPJS data retrieved successfully

────────────────────────────────────────────────────────────
RESULT:
{
  "nik": "3317110608050001",
  "tgl_lahir": "2005-08-06",
  "status": "SUCCESS",
  "nama_peserta": " AGU* ILH** MAU****",
  "status_peserta": "TIDAK AKTIF",
  "jenis_peserta": "PPU",
  "faskes_terdaftar": "Pancur ",
  "timestamp": "2026-01-02T20:36:17.935Z"
}
────────────────────────────────────────────────────────────
```

### 2. JSON Output (`bpjs_results.json`)

```json
[
  {
    "nik": "3317110608050001",
    "tgl_lahir": "2005-08-06",
    "status": "SUCCESS",
    "nama_peserta": " AGU* ILH** MAU****",
    "status_peserta": "TIDAK AKTIF",
    "jenis_peserta": "PPU",
    "faskes_terdaftar": "Pancur ",
    "timestamp": "2026-01-02T20:36:17.935Z"
  }
]
```

### 3. CSV Output (`bpjs_results.csv`)

```csv
nik,tgl_lahir,status,nama_peserta,status_peserta,jenis_peserta,faskes_terdaftar,timestamp
3317110608050001,2005-08-06,SUCCESS, AGU* ILH** MAU****,TIDAK AKTIF,PPU,Pancur ,2026-01-02T20:36:17.935Z
```

## Konfigurasi

### Bearer Token

Bearer token diperlukan untuk authorization. Ada 3 cara:

1. **Hardcode di script** (default):
```python
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

2. **Pass sebagai argument**:
```bash
python bpjs_checker_batch.py input.csv YOUR_TOKEN_HERE
```

3. **Dari environment variable**:
```bash
export BPJS_BEARER_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
python bpjs_checker.py
```

### Captcha Solving Settings

Edit di `bpjs_checker.py`:

```python
# Maksimal percobaan solve captcha
max_captcha_attempts = 5

# Maksimal retry jika captcha salah
max_retries = 3

# Delay antar request (seconds)
time.sleep(3)
```

### OCR Configuration

Untuk meningkatkan akurasi OCR, edit di method `solve_captcha()`:

```python
# Whitelist karakter yang diperbolehkan
custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# Contrast enhancement
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(2.0)  # Adjust value (1.0 - 3.0)
```

## Troubleshooting

### 1. Tesseract Not Found

**Error:** `pytesseract.pytesseract.TesseractNotFoundError`

**Solusi:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Amazon Linux
sudo dnf install tesseract

# macOS
brew install tesseract
```

### 2. Captcha Solving Gagal

**Gejala:** Captcha selalu salah atau empty result

**Solusi:**
- Tingkatkan contrast enhancement
- Adjust OCR config
- Tambah preprocessing (threshold, denoise)
- Coba manual solve beberapa captcha untuk lihat pattern

### 3. Bearer Token Expired

**Error:** 401 Unauthorized atau token expired

**Solusi:**
- Login ulang ke jaga.id
- Capture bearer token baru dari browser DevTools
- Update token di script

### 4. Rate Limiting

**Error:** Too many requests atau 429 status

**Solusi:**
- Tambah delay antar request
- Kurangi max_captcha_attempts
- Gunakan proxy rotation (advanced)

## Advanced Usage

### Custom Preprocessing untuk OCR

```python
def solve_captcha_advanced(self, inline_image):
    # ... decode image ...
    
    # Grayscale
    image = image.convert('L')
    
    # Threshold
    import numpy as np
    img_array = np.array(image)
    threshold = 128
    img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
    image = Image.fromarray(img_array)
    
    # Denoise
    from PIL import ImageFilter
    image = image.filter(ImageFilter.MedianFilter(size=3))
    
    # OCR
    captcha_text = pytesseract.image_to_string(image, config=custom_config)
    return captcha_text.strip()
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_parallel(data_list, max_workers=3):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(checker.check_bpjs_auto, d['nik'], d['tgl_lahir'])
            for d in data_list
        ]
        results = [f.result() for f in futures]
    return results
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bpjs_checker.log'),
        logging.StreamHandler()
    ]
)
```

## Struktur File

```
.
├── bpjs_checker.py           # Main script (single/multiple NIK)
├── bpjs_checker_batch.py     # Batch processor (dari CSV)
├── input_nik.csv             # Input file (user created)
├── bpjs_results.json         # Output JSON
├── bpjs_results.csv          # Output CSV
└── README_USAGE.md           # Dokumentasi ini
```

## API Endpoints

Script ini menggunakan 2 endpoint dari jaga.id:

1. **Generate Captcha**
   - URL: `https://jaga.id/api/v5/captchas/generate`
   - Method: POST
   - Body: `{}`
   - Response: `{uuid, inline_image}`

2. **Check BPJS**
   - URL: `https://jaga.id/api/v5/bpjs/detail`
   - Method: GET
   - Params: `nik, tgl_lahir, captcha_uuid, captcha_answer`
   - Response: `{namapeserta, nmstatuspeserta, nmjenispeserta, faskesterdaftar}`

## Disclaimer

⚠️ **PENTING:**
- Script ini hanya untuk tujuan edukasi dan testing
- Pastikan Anda memiliki izin untuk mengakses data
- Jangan abuse API dengan request berlebihan
- Hormati rate limiting dan terms of service
- Data BPJS adalah data sensitif, jaga kerahasiaannya

## License

MIT License - Free to use and modify

## Support

Jika ada pertanyaan atau issue:
1. Check troubleshooting section
2. Review code comments
3. Test dengan single NIK dulu sebelum batch
4. Pastikan dependencies terinstall dengan benar

---

**Happy Checking! 🚀**
