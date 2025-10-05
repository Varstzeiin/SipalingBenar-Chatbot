"""
Script untuk generate semua aset statis yang dibutuhkan
untuk Sistem Identifikasi dan Mitigasi Disinformasi
"""
import os
import csv

def create_directory_structure():
    """Membuat struktur folder yang dibutuhkan"""
    directories = [
        'static_assets',
        'static_assets/lexicons',
        'static_assets/samples'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Folder '{directory}' dibuat/sudah ada")

def create_hoax_keywords():
    """Generate kamus kata kunci hoaks bahasa Indonesia"""
    hoax_keywords = [
        # Kata-kata sensasional
        "HEBOH", "VIRAL", "MENGEJUTKAN", "BREAKING NEWS", "MENGERIKAN",
        "WASPADA", "AWAS", "BAHAYA", "HATI-HATI", "JANGAN SAMPAI",
        
        # Kata yang memaksa share
        "SEBARKAN", "SHARE SEGERA", "FORWARD", "BAGIKAN SEBELUM DIHAPUS",
        "JANGAN DISIMPAN SENDIRI", "INFO PENTING", "BROADCAST",
        
        # Kata tanpa sumber jelas
        "KABAR BURUNG", "KATANYA", "MENURUT ORANG DALAM", "SUMBER TERPERCAYA",
        "BEREDAR", "VIRAL DI MEDSOS", "GRUP SEBELAH", "INFO DARI DALAM",
        
        # Klaim berlebihan
        "100% AMPUH", "DIJAMIN", "PASTI", "TERBUKTI", "MANJUR",
        "TANPA EFEK SAMPING", "OBAT AJAIB", "SEMBUH TOTAL",
        
        # Konspirasi & teori
        "KONSPIRASI", "DIREKAYASA", "SENGAJA DISEMBUNYIKAN", "RAHASIA",
        "MEREKA TIDAK INGIN ANDA TAHU", "KEBOHONGAN PUBLIK", "PROPAGANDA",
        
        # Ancaman & ketakutan
        "AKAN MATI", "SANGAT BERBAHAYA", "MEMATIKAN", "SEGERA ATAU",
        "BATAS WAKTU", "DEADLINE", "TERAKHIR",
        
        # Hadiah & penipuan
        "GRATIS", "HADIAH", "MENANG", "UNTUNG", "BONUS", 
        "TRANSFER", "PULSA", "SALDO", "TERPILIH",
        
        # Kata emosional ekstrim
        "MENGKHIANATI", "MENJIJIKKAN", "MEMALUKAN", "MEMPERMALUKAN",
        "BIADAB", "KAFIR", "LAKNAT"
    ]
    
    filepath = 'static_assets/lexicons/hoax_keywords.txt'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# KAMUS KATA KUNCI HOAKS BAHASA INDONESIA\n")
        f.write("# Sumber: Analisis berita hoaks yang sering beredar\n")
        f.write("# Format: Satu kata/frasa per baris\n\n")
        for keyword in hoax_keywords:
            f.write(f"{keyword}\n")
    
    print(f"✓ File '{filepath}' berhasil dibuat ({len(hoax_keywords)} keywords)")

def create_phishing_keywords():
    """Generate kamus kata kunci phishing"""
    phishing_keywords = [
        # Hadiah palsu
        "SELAMAT ANDA MENDAPAT", "ANDA TERPILIH", "PEMENANG",
        "HADIAH Rp", "DANA HIBAH", "BANTUAN LANGSUNG TUNAI",
        
        # Urgency & ancaman
        "SEGERA VERIFIKASI", "AKUN AKAN DIBLOKIR", "REKENING TERBLOKIR",
        "KARTU ATM TIDAK AKTIF", "SEGERA KONFIRMASI", "BATAS WAKTU",
        "EXPIRED", "KADALUARSA", "SUSPEND",
        
        # Permintaan data sensitif
        "MASUKKAN PIN", "BERIKAN OTP", "KODE OTP", "CVV", 
        "VERIFIKASI NIK", "NOMOR KARTU", "PASSWORD", "KATA SANDI",
        "KODE VERIFIKASI", "TOKEN",
        
        # Link & tindakan mencurigakan
        "KLIK LINK", "KLIK DISINI", "KLIK TAUTAN", "BUKA LINK",
        "DOWNLOAD APLIKASI", "INSTAL APKPURE", "UPDATE APLIKASI",
        "BIT.LY", "TINY.URL", "SHORT.LINK",
        
        # Mengaku institusi resmi
        "BANK INDONESIA", "BI CHECKING", "OJK", "KEMENKEU",
        "KEMENSOS", "BPJS", "PLN", "MARKETPLACE OFFICIAL",
        
        # Nominal uang mencurigakan
        "TRANSFER Rp", "KIRIM DANA", "BIAYA ADMIN Rp",
        "BAYAR RP", "SALDO Rp", "PENCAIRAN DANA",
        
        # Teknik social engineering
        "KELUARGA ANDA", "ANAK ANDA", "KECELAKAAN",
        "BUTUH DANA MENDESAK", "NOMOR BARU", "HP HILANG"
    ]
    
    filepath = 'static_assets/lexicons/phishing_keywords.txt'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# KAMUS KATA KUNCI PHISHING BAHASA INDONESIA\n")
        f.write("# Untuk deteksi pesan penipuan, scam, dan phishing\n\n")
        for keyword in phishing_keywords:
            f.write(f"{keyword}\n")
    
    print(f"✓ File '{filepath}' berhasil dibuat ({len(phishing_keywords)} keywords)")

def create_trusted_sources():
    """Generate daftar sumber terpercaya"""
    trusted_sources = {
        "Pemerintah & Lembaga Resmi": [
            "kominfo.go.id",
            "covid19.go.id",
            "setkab.go.id",
            "indonesia.go.id",
            "bpom.go.id",
            "kemkes.go.id",
            "bnpb.go.id",
            "polri.go.id",
            "bi.go.id"
        ],
        "Fact-Checking": [
            "turnbackhoax.id",
            "cekfakta.com",
            "medcom.id/cek-fakta",
            "liputan6.com/cek-fakta",
            "tempo.co/indeks/cek-fakta",
            "kompas.com/cekfakta"
        ],
        "Media Mainstream Terpercaya": [
            "kompas.com",
            "detik.com",
            "tempo.co",
            "antaranews.com",
            "cnnindonesia.com",
            "bbc.com/indonesia",
            "liputan6.com",
            "tirto.id",
            "katadata.co.id"
        ],
        "Kesehatan": [
            "who.int",
            "alodokter.com",
            "halodoc.com",
            "klikdokter.com",
            "sehatq.com"
        ],
        "Teknologi & Keamanan Siber": [
            "bssn.go.id",
            "csirt.go.id",
            "cert.or.id"
        ]
    }
    
    filepath = 'static_assets/lexicons/trusted_sources.txt'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# DAFTAR SUMBER TERPERCAYA\n")
        f.write("# Format: Kategori -> Domain\n\n")
        
        for category, sources in trusted_sources.items():
            f.write(f"## {category}\n")
            for source in sources:
                f.write(f"{source}\n")
            f.write("\n")
    
    total = sum(len(sources) for sources in trusted_sources.values())
    print(f"✓ File '{filepath}' berhasil dibuat ({total} sources)")

def create_example_texts():
    """Generate contoh teks untuk testing"""
    examples = [
        {
            "id": 1,
            "text": "HEBOH!!! Dokter mengungkap rahasia pemerintah sembunyikan obat corona yang 100% ampuh! SHARE SEBELUM DIHAPUS!!!",
            "label": "hoax",
            "category": "kesehatan",
            "reasoning": "Menggunakan kata sensasional, klaim berlebihan tanpa bukti"
        },
        {
            "id": 2,
            "text": "Kementerian Kesehatan RI mengumumkan update vaksinasi COVID-19 untuk booster kedua. Informasi lengkap dapat diakses di covid19.go.id",
            "label": "valid",
            "category": "kesehatan",
            "reasoning": "Merujuk ke sumber resmi pemerintah"
        },
        {
            "id": 3,
            "text": "Selamat! Anda terpilih mendapat hadiah Rp 10.000.000 dari program BRI. Segera klik link ini dan masukkan PIN ATM Anda untuk klaim: bit.ly/xxxxx",
            "label": "phishing",
            "category": "penipuan",
            "reasoning": "Meminta data sensitif, link mencurigakan, hadiah tidak realistis"
        },
        {
            "id": 4,
            "text": "Menurut analisis Katadata, inflasi Indonesia di bulan Maret tercatat 2,8% year-on-year berdasarkan data BPS.",
            "label": "valid",
            "category": "ekonomi",
            "reasoning": "Merujuk sumber data kredibel dan media terpercaya"
        },
        {
            "id": 5,
            "text": "WASPADA! Menurut orang dalam, akan ada gempa besar besok jam 3 sore. Sebarkan ke semua grup!",
            "label": "hoax",
            "category": "bencana",
            "reasoning": "Tidak ada sumber jelas, memprediksi bencana tanpa basis ilmiah"
        },
        {
            "id": 6,
            "text": "Akun BCA Anda terblokir karena aktivitas mencurigakan. Segera verifikasi dengan mengirim OTP ke nomor ini: 0812xxxx. Batas waktu 1 jam.",
            "label": "phishing",
            "category": "penipuan",
            "reasoning": "Social engineering, urgency palsu, meminta OTP"
        },
        {
            "id": 7,
            "text": "BMKG melaporkan potensi cuaca ekstrim di wilayah Jabodetabek pada 15-17 Januari 2025. Masyarakat diimbau waspada. Sumber: bmkg.go.id",
            "label": "valid",
            "category": "cuaca",
            "reasoning": "Informasi dari lembaga berwenang dengan sumber jelas"
        },
        {
            "id": 8,
            "text": "Katanya dari grup sebelah, pemerintah akan lockdown total minggu depan. Info dari orang dalam Istana.",
            "label": "disinformasi",
            "category": "kebijakan",
            "reasoning": "Rumor tanpa konfirmasi resmi, sumber tidak jelas"
        }
    ]
    
    filepath = 'static_assets/samples/example_texts.csv'
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['id', 'text', 'label', 'category', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(examples)
    
    print(f"✓ File '{filepath}' berhasil dibuat ({len(examples)} examples)")

def create_sample_links():
    """Generate daftar link contoh untuk testing scraper"""
    sample_links = [
        "# DAFTAR LINK UNTUK TESTING URL SCRAPER",
        "# Format: URL (satu per baris)",
        "",
        "# Sumber Terpercaya",
        "https://www.kompas.com/",
        "https://www.detik.com/",
        "https://turnbackhoax.id/",
        "https://www.antaranews.com/",
        "",
        "# Fact-Checking Sites",
        "https://cekfakta.com/",
        "https://www.tempo.co/indeks/cek-fakta",
        "",
        "# Government Sites",
        "https://www.kominfo.go.id/",
        "https://covid19.go.id/",
        "",
        "# Contoh untuk diuji (gunakan link aktual untuk testing)",
        "# https://example-news-site.com/article-1",
        "# https://example-blog.com/post-2"
    ]
    
    filepath = 'static_assets/samples/sample_links.txt'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_links))
    
    print(f"✓ File '{filepath}' berhasil dibuat")

def create_readme():
    """Generate README untuk dokumentasi"""
    readme_content = """# Static Assets - Sistem Identifikasi Disinformasi

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
"""
    
    filepath = 'static_assets/README.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ File '{filepath}' berhasil dibuat")

def main():
    """Jalankan semua fungsi setup"""
    print("=" * 60)
    print("SISTEM IDENTIFIKASI DAN MITIGASI DISINFORMASI")
    print("Setup Static Assets Generator")
    print("=" * 60)
    print()
    
    create_directory_structure()
    print()
    
    print("Membuat file lexicons...")
    create_hoax_keywords()
    create_phishing_keywords()
    create_trusted_sources()
    print()
    
    print("Membuat file samples...")
    create_example_texts()
    create_sample_links()
    print()
    
    print("Membuat dokumentasi...")
    create_readme()
    print()
    
    print("=" * 60)
    print("✓ SETUP SELESAI!")
    print("=" * 60)
    print()
    print("Struktur folder dan file telah dibuat di: ./static_assets/")
    print()
    print("Next steps:")
    print("1. Review dan sesuaikan konten file sesuai kebutuhan")
    print("2. Tambahkan lebih banyak keywords dan examples")
    print("3. Integrate dengan sistem rule-based detection Anda")

if __name__ == "__main__":
    main()