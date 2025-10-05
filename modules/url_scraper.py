"""
URL Scraper - Ekstraksi Teks dari Link Berita (Defensive Analysis Version)
Sistem Identifikasi dan Mitigasi Disinformasi

Prinsip Kerja:
1. Coba scraping terlebih dahulu
2. Jika berhasil → gunakan scraped content untuk analisis
3. Jika gagal → tetap analisis berdasarkan URL text itu sendiri
4. Selalu return data untuk analisis (never block the pipeline)

Fitur:
- Ekstraksi konten artikel dari URL (dengan fallback safety)
- Validasi domain terpercaya (file-based + hardcoded)
- Ekstraksi metadata (title, author, date, description)
- URL text analysis sebagai fallback
- Error handling yang aman (tidak stop eksekusi)
- Support untuk berbagai format berita Indonesia
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from datetime import datetime
from typing import Dict, Optional, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class URLScraper:
    """Class untuk scraping konten berita dengan defensive analysis approach"""
    
    def __init__(self, trusted_sources_file: str = 'static_assets/lexicons/trusted_sources.txt'):
        """
        Inisialisasi URL Scraper
        
        Args:
            trusted_sources_file: Path ke file daftar sumber terpercaya
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = 6  # Timeout cepat untuk responsiveness
        self.max_content_length = 6000  # Batasi panjang konten
        
        # Load trusted sources dari file
        self.trusted_domains = self._load_trusted_sources(trusted_sources_file)
        
        # Hardcoded trusted sources sebagai fallback
        self.hardcoded_trusted = [
            'kompas.com', 'detik.com', 'tempo.co', 'kominfo.go.id', 
            'turnbackhoax.id', 'liputan6.com', 'tribunnews.com',
            'cnnindonesia.com', 'antaranews.com', 'bbc.com',
            'suara.com', 'mediaindonesia.com', 'republika.co.id'
        ]
        
    def _load_trusted_sources(self, filepath: str) -> List[str]:
        """Load daftar domain terpercaya dari file"""
        domains = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('##'):
                        domains.append(line)
            logger.info(f"Loaded {len(domains)} trusted domains from file")
        except FileNotFoundError:
            logger.warning(f"Trusted sources file not found: {filepath}. Using hardcoded sources only.")
        return domains
    
    def is_trusted_source(self, url: str) -> bool:
        """
        Cek apakah URL berasal dari sumber terpercaya
        
        Args:
            url: URL yang akan dicek
            
        Returns:
            bool: True jika dari sumber terpercaya
        """
        try:
            domain = urlparse(url).netloc
            domain = domain.replace('www.', '')
            
            # Check file-based trusted sources
            for trusted in self.trusted_domains:
                if domain == trusted or domain.endswith('.' + trusted):
                    return True
            
            # Check hardcoded trusted sources
            for trusted in self.hardcoded_trusted:
                if trusted in domain:
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Error checking trusted source: {e}")
            return False
        
    def is_suspicious_domain(self, url: str) -> bool:
        """Deteksi domain mencurigakan (umum pada situs phishing)"""
        suspicious_tlds = (
            '.xyz', '.site', '.buzz', '.top', '.icu', '.click',
            '.gift', '.app', '.link', '.live', '.shop', '.monster',
            '.fit', '.rest', '.cf', '.ml', '.gq'
        )
        try:
            domain = urlparse(url).netloc.lower()
            return any(domain.endswith(tld) for tld in suspicious_tlds)
        except Exception:
            return False

    
    def scrape_url(self, url: str, retry: int = 2) -> Dict:
        """
        Scrape konten dari URL dengan defensive analysis approach
        
        PRINSIP KERJA:
        1. Coba scraping dulu
        2. Kalau berhasil → return scraped content
        3. Kalau gagal → return URL text untuk analisis fallback
        4. ALWAYS return analyzable data (never fully fail)
        
        Args:
            url: URL artikel yang akan di-scrape
            retry: Jumlah percobaan ulang jika gagal (default: 2 untuk lebih cepat)
            
        Returns:
            Dict dengan struktur:
            {
                'success': bool,              # True jika scraping berhasil
                'scraped': bool,              # True jika content dari scraping
                'url': str,                   # URL original
                'domain': str,                # Domain extracted
                'is_trusted': bool,           # Apakah dari trusted source
                'title': str,                 # Title artikel (jika ada)
                'content': str,               # ALWAYS ada (scraped atau URL fallback)
                'author': str,                # Author (jika ada)
                'publish_date': str,          # Tanggal publish (jika ada)
                'description': str,           # Description (jika ada)
                'error': str,                 # Error message (jika gagal)
                'analysis_note': str,         # Note untuk sistem analisis
                'scraped_at': str             # Timestamp
            }
        """
        # Validasi input dasar
        if not url or not isinstance(url, str):
            return self._create_fallback_result(
                url or '', 
                error='URL kosong atau tidak valid',
                note='⚠️ Input tidak valid, tidak bisa dianalisis'
            )
        
        # Strip whitespace
        url = url.strip()
        
        # Initialize result structure
        result = {
            'success': False,
            'scraped': False,
            'url': url,
            'domain': '',
            'is_trusted': False,
            'title': '',
            'content': '',
            'author': '',
            'publish_date': '',
            'description': '',
            'analysis_note': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Validasi URL format dengan regex fleksibel
        if not re.match(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}", url):
            logger.warning(f"Suspicious URL format: {url}")
            return self._create_fallback_result(
                url,
                error='Format URL mencurigakan',
                note='⚠️ Link tidak bisa dibuka, tapi tetap dianalisis dari teks URL-nya'
            )
        
        # Extract domain info
        try:
            parsed_url = urlparse(url)
            result['domain'] = parsed_url.netloc.replace('www.', '')
            result['is_trusted'] = self.is_trusted_source(url)
        except Exception as e:
            # Fallback domain extraction
            domain_match = re.findall(r"https?://([^/]+)/?", url)
            result['domain'] = domain_match[0] if domain_match else url
            result['error'] = f'Domain extraction warning: {str(e)}'
            logger.warning(f"Domain extraction issue: {e}")
        
        # === FASE 1: COBA SCRAPING ===
        scraping_success = False
        
        for attempt in range(retry):
            try:
                logger.info(f"🔍 Scraping URL (attempt {attempt + 1}/{retry}): {url}")
                response = self.session.get(url, timeout=self.timeout)
                
                # Check HTTP status
                if response.status_code != 200:
                    result['error'] = f'HTTP {response.status_code}'
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all metadata
                extracted_title = self._extract_title(soup)
                extracted_content = self._extract_content(soup)
                extracted_author = self._extract_author(soup)
                extracted_date = self._extract_date(soup)
                extracted_description = self._extract_description(soup)
                
                # Validasi minimal konten tersedia
                if extracted_content and len(extracted_content) > 100:
                    # === SCRAPING BERHASIL ===
                    result['success'] = True
                    result['scraped'] = True
                    result['title'] = extracted_title
                    result['is_suspicious'] = self.is_suspicious_domain(url)
                    result['content'] = extracted_content
                    result['author'] = extracted_author
                    result['publish_date'] = extracted_date
                    result['description'] = extracted_description
                    result['analysis_note'] = '✅ Konten berhasil di-scrape, analisis dari artikel lengkap'
                    
                    # Batasi panjang konten
                    if len(result['content']) > self.max_content_length:
                        result['content'] = result['content'][:self.max_content_length] + '...'
                        logger.info(f"Content truncated to {self.max_content_length} chars")
                    
                    # Remove error field jika ada
                    if 'error' in result:
                        del result['error']
                    
                    logger.info(f"✅ Successfully scraped: {url}")
                    scraping_success = True
                    break
                else:
                    result['error'] = 'Content too short or empty'
                    logger.warning(f"Content too short for {url}")
                    
            except requests.exceptions.Timeout:
                result['error'] = f'Timeout after {self.timeout}s'
                logger.warning(f"⏱️ Timeout scraping {url}")
                
            except requests.exceptions.RequestException as e:
                result['error'] = f'Request error: {str(e)}'
                logger.error(f"❌ Request error: {e}")
                
            except Exception as e:
                result['error'] = f'Parsing error: {str(e)}'
                logger.error(f"❌ Parsing error: {e}")
            
            # Wait before retry
            if attempt < retry - 1:
                time.sleep(1)
        
        # === FASE 2: FALLBACK JIKA SCRAPING GAGAL ===
        if not scraping_success:
            logger.warning(f"⚠️ Scraping failed for {url}, using URL text as fallback")
            fallback = self._create_fallback_result(
                url,
                domain=result['domain'],
                is_trusted=result['is_trusted'],
                error=result.get('error', 'Scraping failed'),
                note='⚠️ Link tidak bisa dibuka, tapi tetap dianalisis dari teks dan pola URL-nya'
            )
            fallback['is_suspicious'] = self.is_suspicious_domain(url)
            return fallback

    
    def _create_fallback_result(self, url: str, domain: str = '', 
                                is_trusted: bool = False, 
                                error: str = '', note: str = '') -> Dict:
        """
        Buat result fallback ketika scraping gagal
        PENTING: Content = URL text agar RulesPrecheck bisa analisis
        
        Args:
            url: URL original
            domain: Domain (jika sudah di-extract)
            is_trusted: Status trusted (jika sudah di-check)
            error: Error message
            note: Note untuk user/system
            
        Returns:
            Dict result dengan URL sebagai content
        """
        # Extract domain jika belum ada
        if not domain:
            try:
                domain = urlparse(url).netloc.replace('www.', '')
            except:
                domain_match = re.findall(r"https?://([^/]+)/?", url)
                domain = domain_match[0] if domain_match else url
        
        # Check trusted jika belum
        if not is_trusted:
            is_trusted = self.is_trusted_source(url)
        
        return {
            'success': False,
            'scraped': False,
            'url': url,
            'domain': domain,
            'is_trusted': is_trusted,
            'title': f'Link: {domain}',
            'content': url,  # KUNCI: URL text untuk analisis fallback
            'author': '',
            'publish_date': '',
            'description': '',
            'error': error,
            'analysis_note': note,
            'scraped_at': datetime.now().isoformat()
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Ekstrak judul artikel"""
        selectors = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in selectors:
            try:
                element = soup.find(tag, attrs)
                if element:
                    if tag == 'meta':
                        title = element.get('content', '').strip()
                    else:
                        title = element.get_text().strip()
                    if title:
                        return title
            except:
                continue
        
        return 'Tidak ada judul'
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Ekstrak konten utama artikel"""
        try:
            # Remove script, style, nav, footer, ads
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # Try common article selectors
            article_selectors = [
                'article',
                {'class': re.compile(r'article|content|post|entry', re.I)},
                {'id': re.compile(r'article|content|post|entry', re.I)}
            ]
            
            for selector in article_selectors:
                if isinstance(selector, str):
                    article = soup.find(selector)
                else:
                    article = soup.find('div', selector)
                
                if article:
                    paragraphs = article.find_all('p')
                    if paragraphs:
                        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                        if len(content) > 100:
                            return self._clean_text(content)
            
            # Fallback: get all paragraphs
            all_paragraphs = soup.find_all('p')
            if all_paragraphs:
                content = ' '.join([p.get_text().strip() for p in all_paragraphs])
                if content:
                    return self._clean_text(content)
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
        
        return ''
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Ekstrak nama author"""
        try:
            author_metas = [
                soup.find('meta', {'name': 'author'}),
                soup.find('meta', {'property': 'article:author'}),
                soup.find('meta', {'name': 'twitter:creator'})
            ]
            
            for meta in author_metas:
                if meta and meta.get('content'):
                    return meta.get('content').strip()
            
            author_selectors = [
                {'class': re.compile(r'author|penulis|reporter', re.I)},
                {'rel': 'author'}
            ]
            
            for selector in author_selectors:
                author = soup.find(['span', 'a', 'div'], selector)
                if author:
                    return author.get_text().strip()
        except:
            pass
        
        return ''
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Ekstrak tanggal publikasi"""
        try:
            date_metas = [
                soup.find('meta', {'property': 'article:published_time'}),
                soup.find('meta', {'name': 'publish_date'}),
                soup.find('meta', {'name': 'date'}),
                soup.find('time')
            ]
            
            for meta in date_metas:
                if meta:
                    date_str = meta.get('content') or meta.get('datetime') or meta.get_text()
                    if date_str:
                        return date_str.strip()
            
            date_selectors = [
                {'class': re.compile(r'date|time|publish|tanggal', re.I)}
            ]
            
            for selector in date_selectors:
                date_elem = soup.find(['time', 'span', 'div'], selector)
                if date_elem:
                    return date_elem.get_text().strip()
        except:
            pass
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Ekstrak deskripsi/summary artikel"""
        try:
            desc_metas = [
                soup.find('meta', {'property': 'og:description'}),
                soup.find('meta', {'name': 'description'}),
                soup.find('meta', {'name': 'twitter:description'})
            ]
            
            for meta in desc_metas:
                if meta and meta.get('content'):
                    return meta.get('content').strip()
        except:
            pass
        
        return ''
    
    def _clean_text(self, text: str) -> str:
        """Bersihkan teks dari whitespace berlebih"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def scrape_multiple(self, urls: List[str], delay: float = 1.0) -> List[Dict]:
        """
        Scrape multiple URLs dengan delay
        SEMUA URL akan di-process, yang gagal jadi fallback analysis
        
        Args:
            urls: List URL yang akan di-scrape
            delay: Delay antar request (seconds)
            
        Returns:
            List hasil scraping (always complete, never empty)
        """
        results = []
        total = len(urls)
        
        logger.info(f"🚀 Starting to scrape {total} URLs")
        
        for idx, url in enumerate(urls, 1):
            logger.info(f"📊 Progress: {idx}/{total}")
            result = self.scrape_url(url)
            results.append(result)
            
            # Delay between requests
            if idx < total:
                time.sleep(delay)
        
        # Statistics
        success_count = sum(1 for r in results if r['success'])
        fallback_count = total - success_count
        
        logger.info(f"✅ Completed: {total} URLs processed")
        logger.info(f"   - Scraped successfully: {success_count}")
        logger.info(f"   - Fallback analysis: {fallback_count}")
        
        return results
    
    def scrape_from_file(self, filepath: str, delay: float = 1.0) -> List[Dict]:
        """
        Scrape URLs dari file
        
        Args:
            filepath: Path ke file berisi list URL
            delay: Delay antar request
            
        Returns:
            List hasil scraping
        """
        urls = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
            logger.info(f"📁 Loaded {len(urls)} URLs from file")
        except FileNotFoundError:
            logger.error(f"❌ File not found: {filepath}")
            return []
        
        return self.scrape_multiple(urls, delay)


def main():
    """Contoh penggunaan URL Scraper dengan Defensive Analysis"""
    print("=" * 70)
    print("URL SCRAPER - Defensive Analysis Mode")
    print("Prinsip: Scraping gagal? Tetap analisis dari URL text!")
    print("=" * 70)
    print()
    
    scraper = URLScraper()
    
    # Test case 1: URL normal (scraping berhasil)
    print("📰 Test 1: Normal News URL (Expected: Scraping Success)")
    print("-" * 70)
    url1 = "https://www.kompas.com/"
    result1 = scraper.scrape_url(url1)
    
    print(f"URL: {url1}")
    print(f"Status: {'✅ SCRAPED' if result1['scraped'] else '⚠️ FALLBACK'}")
    print(f"Trusted: {'🔒' if result1['is_trusted'] else '⚠️'} {result1['domain']}")
    print(f"Content: {result1['content'][:150]}...")
    print(f"Note: {result1['analysis_note']}")
    print()
    
    # Test case 2: URL suspicious (scraping gagal, tapi tetap analisis)
    print("🚨 Test 2: Suspicious URL (Expected: Fallback Analysis)")
    print("-" * 70)
    url2 = "https://bit.ly/verifikasi-dana-bansos-2024"
    result2 = scraper.scrape_url(url2)
    
    print(f"URL: {url2}")
    print(f"Status: {'✅ SCRAPED' if result2['scraped'] else '⚠️ FALLBACK'}")
    print(f"Trusted: {'🔒' if result2['is_trusted'] else '⚠️'} {result2['domain']}")
    print(f"Content for analysis: {result2['content']}")  # Ini URL text-nya
    print(f"Note: {result2['analysis_note']}")
    print(f"Error: {result2.get('error', 'N/A')}")
    print()
    
    # Test case 3: Invalid URL format
    print("❌ Test 3: Invalid URL Format")
    print("-" * 70)
    url3 = "bukan-url-valid"
    result3 = scraper.scrape_url(url3)
    
    print(f"Input: {url3}")
    print(f"Status: {'✅ SCRAPED' if result3['scraped'] else '⚠️ FALLBACK'}")
    print(f"Content for analysis: {result3['content']}")
    print(f"Note: {result3['analysis_note']}")
    print()
    
    # Test case 4: Batch processing
    print("🔄 Test 4: Batch Processing (Mixed URLs)")
    print("-" * 70)
    test_urls = [
        "https://www.detik.com/",
        "https://fake-phishing-site.xyz/claim-prize",
        "https://turnbackhoax.id/"
    ]
    
    results = scraper.scrape_multiple(test_urls, delay=0.5)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['scraped'] else "⚠️"
        trusted = "🔒" if result['is_trusted'] else "⚠️"
        print(f"{i}. {status} {trusted} {result['domain']}")
        print(f"   Analysis ready: {len(result['content'])} chars")
        print(f"   {result['analysis_note']}")
    
    print()
    print("=" * 70)
    print("💡 Key Concepts:")
    print("-" * 70)
    print("1. ✅ Scraping berhasil → Analisis dari article content")
    print("2. ⚠️ Scraping gagal → Analisis dari URL text (fallback)")
    print("3. 🔒 Always return analyzable data (never fully fail)")
    print("4. 🎯 RulesPrecheck bisa deteksi pattern dari URL text")
    print("=" * 70)


if __name__ == "__main__":
    main()