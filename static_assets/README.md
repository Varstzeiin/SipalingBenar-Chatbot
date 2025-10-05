# Static Assets - Sistem Identifikasi Disinformasi

## Struktur Folder

```
static_assets/
├── lexicons/              # Kamus kata kunci
│   ├── hoax_keywords.txt
│   ├── phishing_keywords.txt
│   └── trusted_sources.txt
└── samples/               # Contoh data untuk testing
    ├── example_texts.csv
    └── sample_links.txt
```

## Deskripsi File

### Lexicons

1. **hoax_keywords.txt**
   - Kumpulan kata kunci yang sering muncul di konten hoaks
   - Digunakan untuk rule-based detection
   - Kategori: sensasional, memaksa share, tanpa sumber, dll

2. **phishing_keywords.txt**
   - Kata kunci umum dalam pesan phishing/penipuan
   - Deteksi social engineering attempts
   - Kategori: hadiah palsu, urgency, permintaan data sensitif

3. **trusted_sources.txt**
   - Daftar domain/sumber terpercaya
   - Dikelompokkan berdasarkan kategori
   - Untuk validasi kredibilitas sumber

### Samples

1. **example_texts.csv**
   - Contoh teks dengan label (hoax/valid/phishing/disinformasi)
   - Untuk testing dan training model
   - Kolom: id, text, label, category, reasoning

2. **sample_links.txt**
   - Daftar URL untuk testing scraper
   - Kombinasi sumber terpercaya dan contoh kasus

## Cara Penggunaan

```python
# Contoh load hoax keywords
with open('static_assets/lexicons/hoax_keywords.txt', 'r') as f:
    keywords = [line.strip() for line in f if not line.startswith('#')]

# Contoh load example texts
import pandas as pd
df = pd.read_csv('static_assets/samples/example_texts.csv')
```

## Update & Maintenance

- Perbarui keywords secara berkala berdasarkan tren hoaks terbaru
- Tambahkan sumber terpercaya baru yang muncul
- Perluas dataset contoh untuk meningkatkan akurasi

## Kontribusi

Untuk menambahkan data baru:
1. Ikuti format yang sudah ada
2. Pastikan menggunakan encoding UTF-8
3. Tambahkan komentar jika perlu
