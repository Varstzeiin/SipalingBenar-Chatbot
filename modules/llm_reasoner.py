"""
Modul LLM Reasoner - Analisis Lanjutan dengan LLM
Menggunakan Gemini/GPT untuk reasoning & verification
"""

import os
from typing import Dict, Optional
import json
from datetime import datetime

# Support untuk multiple LLM providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMReasoner:
    def __init__(self, provider: str = 'gemini', api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM Reasoner
        
        Args:
            provider: 'gemini' atau 'openai'
            api_key: API key untuk provider yang dipilih
            model: Model yang akan digunakan (opsional)
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f'{provider.upper()}_API_KEY')
        
        if not self.api_key:
            raise ValueError(f"API key untuk {provider} tidak ditemukan")
        
        if self.provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai tidak terinstall. Install dengan: pip install google-generativeai")
            genai.configure(api_key=self.api_key)
            self.model = model or 'gemini-flash-2.5'
            self.client = genai.GenerativeModel(self.model)
        
        elif self.provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai tidak terinstall. Install dengan: pip install openai")
            openai.api_key = self.api_key
            self.model = model or 'gpt-4'
            self.client = openai
        
        else:
            raise ValueError(f"Provider '{provider}' tidak didukung. Gunakan 'gemini' atau 'openai'")
        
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Buat system prompt untuk analisis"""
        return """Anda adalah sistem analisis konten berbahasa Indonesia yang bertugas mengidentifikasi hoaks, disinformasi, dan misinformasi.

Tugas Anda:
1. Analisis konten yang diberikan secara mendalam
2. Identifikasi tanda-tanda hoaks, disinformasi, atau misinformasi
3. Berikan kategori: HOAX, DISINFORMASI, MISINFORMASI, CLICKBAIT, PHISHING, atau VALID
4. Berikan confidence score (0-100)
5. Berikan reasoning yang jelas dan terstruktur
6. Identifikasi fakta yang bisa diverifikasi
7. Deteksi bias dan manipulasi informasi

Kriteria penilaian:
- HOAX: Informasi yang sepenuhnya salah dan dibuat untuk menyesatkan
- DISINFORMASI: Informasi salah yang disebarkan dengan sengaja untuk tujuan tertentu
- MISINFORMASI: Informasi salah yang disebarkan tanpa niat jahat
- CLICKBAIT: Judul menyesatkan untuk mendapatkan klik
- PHISHING: Upaya penipuan untuk mendapatkan data/uang
- VALID: Informasi yang dapat dipercaya dengan sumber jelas

Berikan output dalam format JSON berikut:
{
    "category": "kategori utama",
    "confidence": confidence_score,
    "reasoning": "penjelasan detail",
    "red_flags": ["daftar tanda bahaya"],
    "verifiable_claims": ["klaim yang bisa diverifikasi"],
    "sources_needed": ["sumber yang diperlukan untuk verifikasi"],
    "bias_detected": "jenis bias jika ada",
    "recommendation": "rekomendasi untuk pembaca"
}"""
    
    def analyze(self, content: Dict, precheck_results: Optional[Dict] = None) -> Dict:
        """
        Analisis konten menggunakan LLM
        
        Args:
            content: Dict berisi 'title', 'text', 'url', dll
            precheck_results: Hasil dari rules precheck (opsional)
            
        Returns:
            Dict hasil analisis LLM
        """
        # Persiapkan prompt
        user_prompt = self._create_user_prompt(content, precheck_results)
        
        # Panggil LLM
        try:
            if self.provider == 'gemini':
                response = self._call_gemini(user_prompt)
            elif self.provider == 'openai':
                response = self._call_openai(user_prompt)
            
            # Parse response
            result = self._parse_response(response)
            
            # Tambahkan metadata
            result['timestamp'] = datetime.now().isoformat()
            result['provider'] = self.provider
            result['model'] = self.model
            result['success'] = True
            result['error'] = None
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'category': 'unknown',
                'confidence': 0,
                'reasoning': f'Error saat analisis: {str(e)}'
            }
    
    def _create_user_prompt(self, content: Dict, precheck_results: Optional[Dict] = None) -> str:
        """Buat user prompt dari content"""
        prompt = f"""Analisis konten berikut:

Judul: {content.get('title', 'Tidak ada judul')}

URL: {content.get('url', 'Tidak ada URL')}

Konten:
{content.get('text', content.get('plain_text', 'Tidak ada konten'))}

"""
        
        if precheck_results:
            prompt += f"""
Hasil Precheck:
- Klasifikasi awal: {precheck_results.get('classification', 'unknown')}
- Hoax score: {precheck_results.get('hoax_score', 0)}
- Phishing score: {precheck_results.get('phishing_score', 0)}
- Warning: {', '.join(precheck_results.get('warnings', []))}

"""
        
        prompt += """Berikan analisis mendalam dalam format JSON yang diminta."""
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> str:
        """Panggil Gemini API"""
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        response = self.client.generate_content(full_prompt)
        return response.text
    
    def _call_openai(self, prompt: str) -> str:
        """Panggil OpenAI API"""
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> Dict:
        """Parse response dari LLM"""
        try:
            # Cari JSON dalam response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result
            else:
                # Fallback jika tidak ada JSON
                return self._create_fallback_result(response)
                
        except json.JSONDecodeError:
            return self._create_fallback_result(response)
    
    def _create_fallback_result(self, response: str) -> Dict:
        """Buat hasil fallback jika parsing gagal"""
        return {
            'category': 'unknown',
            'confidence': 50,
            'reasoning': response,
            'red_flags': [],
            'verifiable_claims': [],
            'sources_needed': [],
            'bias_detected': 'unknown',
            'recommendation': 'Perlu verifikasi manual',
            'raw_response': response
        }
    
    def batch_analyze(self, contents: list, precheck_results: Optional[list] = None) -> list:
        """
        Analisis multiple konten
        
        Args:
            contents: List of content dicts
            precheck_results: List of precheck results (opsional)
            
        Returns:
            List hasil analisis
        """
        results = []
        
        for i, content in enumerate(contents):
            precheck = precheck_results[i] if precheck_results and i < len(precheck_results) else None
            result = self.analyze(content, precheck)
            results.append(result)
        
        return results


# Contoh penggunaan
if __name__ == "__main__":
    # PENTING: Ganti dengan API key Anda atau set environment variable
    # export GEMINI_API_KEY="your-api-key-here"
    
    # Test content
    test_content = {
        'title': 'VIRAL!!! Pemerintah Sembunyikan Fakta Mengejutkan Ini!!!',
        'text': '''
        Beredar informasi yang sangat mengejutkan tentang kebijakan baru pemerintah.
        Menurut sumber yang tidak bisa disebutkan, ternyata ada fakta yang disembunyikan
        dari publik. Share sebelum dihapus! Klik link untuk info lengkap.
        ''',
        'url': 'http://bit.ly/viral123'
    }
    
    test_precheck = {
        'classification': 'hoax',
        'hoax_score': 80,
        'phishing_score': 30,
        'warnings': ['Konten terdeteksi sebagai hoax', 'URL mencurigakan']
    }
    
    print("=== Testing LLM Reasoner ===\n")
    print("CATATAN: Anda perlu mengatur API key terlebih dahulu")
    print("Contoh: export GEMINI_API_KEY='your-key-here'\n")
    
    # Uncomment untuk test (setelah set API key)
    # try:
    #     reasoner = LLMReasoner(provider='gemini')
    #     result = reasoner.analyze(test_content, test_precheck)
    #     
    #     print("Hasil Analisis:")
    #     print(f"Kategori: {result.get('category')}")
    #     print(f"Confidence: {result.get('confidence')}%")
    #     print(f"Reasoning: {result.get('reasoning')}")
    #     print(f"Red Flags: {result.get('red_flags')}")
    #     print(f"Rekomendasi: {result.get('recommendation')}")
    # except Exception as e:
    #     print(f"Error: {e}")
    #     print("Pastikan API key sudah diatur dengan benar")