"""
Modul RAG Retriever - Retrieval Augmented Generation
Mengambil data referensi dari situs cek fakta (Kominfo, Mafindo, Cekfakta)
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus
import time


class RAGRetriever:
    def __init__(self, timeout: int = 10):
        """
        Initialize RAG Retriever
        
        Args:
            timeout: Timeout untuk request dalam detik
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Situs cek fakta yang didukung
        self.fact_check_sites = {
            'turnbackhoax': {
                'name': 'TurnBackHoax Mafindo',
                'base_url': 'https://turnbackhoax.id',
                'search_url': 'https://turnbackhoax.id/?s={query}',
                'selectors': {
                    'articles': 'article.post',
                    'title': 'h2.entry-title a',
                    'link': 'h2.entry-title a',
                    'excerpt': 'div.entry-summary',
                    'date': 'time.entry-date'
                }
            },
            'cekfakta': {
                'name': 'Cek Fakta Tempo',
                'base_url': 'https://cekfakta.tempo.co',
                'search_url': 'https://cekfakta.tempo.co/search?q={query}',
                'selectors': {
                    'articles': 'div.card',
                    'title': 'h2.title a',
                    'link': 'h2.title a',
                    'excerpt': 'p.text',
                    'date': 'span.date'
                }
            },
            'kominfo': {
                'name': 'AIS Kominfo',
                'base_url': 'https://www.kominfo.go.id',
                'search_url': 'https://www.kominfo.go.id/index.php/search/hasil?q={query}',
                'selectors': {
                    'articles': 'div.search-result-item',
                    'title': 'h3 a',
                    'link': 'h3 a',
                    'excerpt': 'p',
                    'date': 'span.date'
                }
            }
        }
    
    def search_fact_checks(
        self, 
        query: str, 
        sites: Optional[List[str]] = None,
        max_results: int = 5
    ) -> Dict:
        """
        Search fact-checking dari berbagai situs
        
        Args:
            query: Query pencarian
            sites: List nama situs ('turnbackhoax', 'cekfakta', 'kominfo')
            max_results: Maksimal hasil per situs
            
        Returns:
            Dict berisi hasil fact-checking
        """
        if sites is None:
            sites = ['turnbackhoax', 'cekfakta']
        
        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'fact_checks': [],
            'sources_checked': [],
            'total_found': 0,
            'errors': []
        }
        
        for site_key in sites:
            if site_key not in self.fact_check_sites:
                results['errors'].append(f"Situs '{site_key}' tidak dikenal")
                continue
            
            site_config = self.fact_check_sites[site_key]
            results['sources_checked'].append(site_config['name'])
            
            try:
                site_results = self._search_site(query, site_config, max_results)
                results['fact_checks'].extend(site_results)
                results['total_found'] += len(site_results)
                
                # Delay antar request
                time.sleep(1)
                
            except Exception as e:
                results['errors'].append(f"Error saat scraping {site_config['name']}: {str(e)}")
        
        # Sort berdasarkan relevance (bisa ditingkatkan dengan scoring)
        results['fact_checks'] = self._rank_results(results['fact_checks'], query)
        
        return results
    
    def _search_site(self, query: str, site_config: Dict, max_results: int) -> List[Dict]:
        """Search di satu situs fact-checking"""
        results = []
        
        # Buat search URL
        search_url = site_config['search_url'].format(query=quote_plus(query))
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find articles
            articles = soup.select(site_config['selectors']['articles'])
            
            for article in articles[:max_results]:
                try:
                    # Extract title
                    title_elem = article.select_one(site_config['selectors']['title'])
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Extract link
                    link_elem = article.select_one(site_config['selectors']['link'])
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    # Pastikan link lengkap
                    if link and not link.startswith('http'):
                        link = site_config['base_url'] + link
                    
                    # Extract excerpt
                    excerpt_elem = article.select_one(site_config['selectors']['excerpt'])
                    excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ''
                    
                    # Extract date
                    date_elem = article.select_one(site_config['selectors']['date'])
                    date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    # Extract verdict jika ada
                    verdict = self._extract_verdict(title, excerpt)
                    
                    if title and link:
                        results.append({
                            'source': site_config['name'],
                            'title': title,
                            'url': link,
                            'excerpt': excerpt[:300],  # Limit excerpt
                            'date': date,
                            'verdict': verdict,
                            'scraped_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    continue  # Skip artikel yang error
        
        except Exception as e:
            raise Exception(f"Gagal mengakses {site_config['name']}: {str(e)}")
        
        return results
    
    def _extract_verdict(self, title: str, excerpt: str) -> str:
        """Extract verdict dari title atau excerpt"""
        text = (title + ' ' + excerpt).lower()
        
        verdicts = {
            'hoax': ['hoax', 'hoaks', 'salah', 'keliru', 'tidak benar', 'bohong'],
            'misleading': ['menyesatkan', 'misleading', 'kurang konteks', 'sebagian benar'],
            'true': ['benar', 'fakta', 'verified', 'terverifikasi'],
            'unverified': ['belum terverifikasi', 'tidak dapat diverifikasi', 'belum dikonfirmasi']
        }
        
        for verdict, keywords in verdicts.items():
            if any(keyword in text for keyword in keywords):
                return verdict
        
        return 'unknown'
    
    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Ranking hasil berdasarkan relevansi"""
        query_terms = set(query.lower().split())
        
        for result in results:
            score = 0
            text = (result['title'] + ' ' + result['excerpt']).lower()
            
            # Score based on query terms
            for term in query_terms:
                if term in text:
                    score += text.count(term)
            
            # Bonus untuk verdict yang jelas
            if result['verdict'] in ['hoax', 'true']:
                score += 5
            
            # Bonus untuk tanggal baru (jika bisa di-parse)
            try:
                # Ini simplified, bisa ditingkatkan dengan proper date parsing
                if 'hari' in result.get('date', '').lower() or \
                   'jam' in result.get('date', '').lower():
                    score += 3
            except:
                pass
            
            result['relevance_score'] = score
        
        # Sort berdasarkan score
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def get_fact_check_detail(self, url: str) -> Dict:
        """
        Ambil detail lengkap dari satu artikel fact-check
        
        Args:
            url: URL artikel fact-check
            
        Returns:
            Dict berisi detail artikel
        """
        result = {
            'url': url,
            'success': False,
            'title': '',
            'content': '',
            'verdict': '',
            'date': '',
            'author': '',
            'error': None
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script dan style
            for script in soup(['script', 'style', 'nav', 'footer']):
                script.decompose()
            
            # Extract title
            title = soup.find('h1')
            result['title'] = title.get_text(strip=True) if title else ''
            
            # Extract content (general approach)
            content_div = soup.find('article') or soup.find('div', class_='content')
            if content_div:
                paragraphs = content_div.find_all('p')
                result['content'] = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            # Extract verdict
            result['verdict'] = self._extract_verdict(result['title'], result['content'])
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_similarity(self, text1: str, text2: str) -> float:
        """
        Hitung similarity antara dua teks (simple Jaccard similarity)
        
        Args:
            text1: Teks pertama
            text2: Teks kedua
            
        Returns:
            Float similarity score (0-1)
        """
        # Tokenize dan normalize
        tokens1 = set(re.findall(r'\w+', text1.lower()))
        tokens2 = set(re.findall(r'\w+', text2.lower()))
        
        # Jaccard similarity
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_related_fact_checks(self, content: str, threshold: float = 0.3) -> Dict:
        """
        Cari fact-check yang related dengan konten
        
        Args:
            content: Konten yang akan dicek
            threshold: Minimum similarity threshold
            
        Returns:
            Dict hasil pencarian
        """
        # Extract keywords dari content
        keywords = self._extract_keywords(content)
        
        # Search dengan keywords
        all_results = []
        for keyword in keywords[:3]:  # Ambil 3 keyword teratas
            search_result = self.search_fact_checks(keyword, max_results=3)
            all_results.extend(search_result['fact_checks'])
        
        # Filter berdasarkan similarity
        related = []
        for fact_check in all_results:
            similarity = self.check_similarity(
                content, 
                fact_check['title'] + ' ' + fact_check['excerpt']
            )
            
            if similarity >= threshold:
                fact_check['similarity_score'] = round(similarity, 3)
                related.append(fact_check)
        
        # Sort berdasarkan similarity
        related = sorted(related, key=lambda x: x['similarity_score'], reverse=True)
        
        # Remove duplicates berdasarkan URL
        seen_urls = set()
        unique_related = []
        for item in related:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_related.append(item)
        
        return {
            'query': 'Related fact-checks',
            'content_keywords': keywords,
            'fact_checks': unique_related[:5],  # Maksimal 5
            'total_found': len(unique_related),
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract keywords dari teks"""
        # Stopwords bahasa Indonesia (simplified)
        stopwords = {
            'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'dengan', 
            'untuk', 'pada', 'adalah', 'oleh', 'akan', 'telah', 'dapat',
            'tidak', 'ada', 'dalam', 'juga', 'atau', 'sebagai', 'tersebut'
        }
        
        # Tokenize
        words = re.findall(r'\w+', text.lower())
        
        # Filter stopwords dan kata pendek
        filtered = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Count frequency
        word_freq = {}
        for word in filtered:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_n]]


# Contoh penggunaan
if __name__ == "__main__":
    retriever = RAGRetriever()
    
    print("=== Testing RAG Retriever ===\n")
    
    # Test 1: Search fact checks
    print("Test 1: Mencari fact-check tentang 'vaksin covid'")
    query = "vaksin covid"
    results = retriever.search_fact_checks(query, sites=['turnbackhoax'], max_results=3)
    
    print(f"Query: {results['query']}")
    print(f"Sumber yang dicek: {', '.join(results['sources_checked'])}")
    print(f"Total ditemukan: {results['total_found']}")
    
    if results['fact_checks']:
        print("\nHasil:")
        for i, fc in enumerate(results['fact_checks'][:3], 1):
            print(f"\n{i}. {fc['title']}")
            print(f"   Sumber: {fc['source']}")
            print(f"   Verdict: {fc['verdict']}")
            print(f"   URL: {fc['url']}")
    
    if results['errors']:
        print(f"\nErrors: {results['errors']}")
    
    print("\n" + "="*80 + "\n")
    
    # Test 2: Extract keywords
    print("Test 2: Extract keywords")
    sample_text = """
    Beredar informasi viral tentang vaksin COVID-19 yang mengandung chip untuk
    melacak masyarakat. Informasi ini tersebar luas di media sosial dan membuat
    masyarakat khawatir tentang keamanan vaksin.
    """
    
    keywords = retriever._extract_keywords(sample_text)
    print(f"Keywords extracted: {', '.join(keywords)}")
    
    print("\n" + "="*80 + "\n")
    
    # Test 3: Similarity check
    print("Test 3: Check similarity")
    text1 = "Pemerintah menutup media sosial untuk mencegah penyebaran hoaks"
    text2 = "Pemerintah akan memblokir media sosial jika hoaks terus menyebar"
    
    similarity = retriever.check_similarity(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {similarity:.3f}")
    
    print("\n=== End Testing ===")