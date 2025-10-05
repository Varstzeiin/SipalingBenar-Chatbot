# ============================================================
# 🧩 Rules Precheck Module — versi upgrade (lebih tajam & adaptif)
# ============================================================

import re
import json

class RulesPrecheck:
    def __init__(self):
        # =====================================================
        # 🔎 Keyword patterns untuk deteksi HOAX
        # =====================================================
        self.hoax_keywords = [
            r'\b(viral|heboh|mengejutkan|mengerikan|menghebohkan|gempar)\b',
            r'\b(ternyata|rahasia|dibongkar|terungkap|terbongkar|fakta tersembunyi)\b',
            r'\b(wajib tahu|harus tau|penting banget|sangat penting|info penting)\b',
            r'\b(jangan sampai|awas|hati-hati|waspada|darurat)\b',
            r'\b(share|bagikan|sebarkan|forward)\s*(sebelum|agar|ke teman|segera)?\b',
            r'\b(fakta mengejutkan|info rahasia|bocoran penting|berita panas)\b',
            r'\b(dilarang keras|akan dihapus|jangan diam saja|jangan diabaikan)\b',
            r'\b(bukan hoax|katanya|teman saya|keluarga di|orang dalam)\b',
            r'\b(kabar ini|beredar luas|dari sumber terpercaya tapi dirahasiakan)\b'
        ]

        # =====================================================
        # 🎣 Keyword untuk PHISHING / SCAM
        # =====================================================
        self.phishing_keywords = [
            r'\b(gratis|free|hadiah|bonus|menang|jackpot|reward|saldo gratis)\b',
            r'\b(klik|click|link|tautan)\s+(disini|di sini|sekarang|untuk|langsung)\b',
            r'\b(transfer|kirim|setor)\s+(uang|dana|saldo|biaya)\b',
            r'\b(verifikasi|aktivasi|konfirmasi|cek|validasi)\s+(akun|rekening|data|identitas)\b',
            r'\b(expired|kadaluarsa|hangus|batas waktu|akan diblokir|terkunci)\b',
            r'\b(segera|cepat|buruan|jangan sampai telat|waktunya terbatas)\b',
            r'\b(OTP|kode rahasia|login|masukkan kode|security code)\b'
        ]

        # =====================================================
        # 🪧 Keyword untuk CLICKBAIT
        # =====================================================
        self.clickbait_patterns = [
            r'\b(gak|tidak|tak)\s+(akan|bakal)\s+percaya\b',
            r'\b(nomor|no\.|angka)\s+\d+\s+(bikin|buat|akan)\b',
            r'\b(inilah|beginilah|ternyata begini|lihat hasilnya|simak faktanya)\b',
            r'\b(kamu pasti|orang ini|cewek ini|pria ini)\s+(tidak|gak)\s+(akan|bakal)\s+percaya\b',
            r'\?\?\?+|\!\!\!+',  # Multiple question/exclamation marks
            r'\b(hasilnya luar biasa|bisa bikin kamu tercengang|tak disangka)\b',
        ]

        # =====================================================
        # 📰 Sumber berita terpercaya
        # =====================================================
        self.trusted_sources = [
            'kompas.com', 'detik.com', 'tempo.co', 'antaranews.com',
            'cnnindonesia.com', 'liputan6.com', 'tribunnews.com',
            'republika.co.id', 'mediaindonesia.com', 'sindonews.com',
            'kominfo.go.id', 'turnbackhoax.id', 'mafindo.or.id'
        ]

        # =====================================================
        # ⚠️ Pattern URL mencurigakan
        # =====================================================
        self.suspicious_url_patterns = [
            r'bit\.ly|tinyurl|short\.link|cutt\.ly|s\.id',       # Shorteners
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',               # IP-based URL
            r'[a-z0-9]{10,}\.(xyz|top|buzz|online|shop)',        # Random low-tier domain
            r'(giveaway|hadiah|freegift|promo)\.[a-z]{2,3}',     # Fake promo
            r'(update|claim|login|redeem)\.(app|xyz|io)'         # Fake login domain
        ]

    # =====================================================
    # 🔍 Analisis teks
    # =====================================================
    def analyze(self, text, url=None):
        if not text or not isinstance(text, str):
            return {"success": False, "error": "Input text kosong atau tidak valid"}

        text_lower = text.lower()
        results = {
            "success": True,
            "source_url": url,
            "hoax_score": 0,
            "phishing_score": 0,
            "clickbait_score": 0,
            "trust_score": 0,
            "suspicious_url_score": 0,
            "extra_flags": 0,
            "confidence": 0.0,
            "classification": "unknown",
            "detected_patterns": []
        }

        # =====================================================
        # 🚨 Deteksi HOAX
        # =====================================================
        for pattern in self.hoax_keywords:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                results["hoax_score"] += len(matches)
                results["detected_patterns"].append({
                    "type": "hoax_keyword",
                    "pattern": pattern,
                    "matches": matches
                })

        # =====================================================
        # 🎣 Deteksi PHISHING
        # =====================================================
        for pattern in self.phishing_keywords:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                results["phishing_score"] += len(matches)
                results["detected_patterns"].append({
                    "type": "phishing_keyword",
                    "pattern": pattern,
                    "matches": matches
                })

        # =====================================================
        # 🪧 Deteksi CLICKBAIT
        # =====================================================
        for pattern in self.clickbait_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                results["clickbait_score"] += len(matches)
                results["detected_patterns"].append({
                    "type": "clickbait_pattern",
                    "pattern": pattern,
                    "matches": matches
                })

        # =====================================================
        # 🧩 Bonus Rule: Gaya HOAX broadcast
        # =====================================================
        uppercase_words = len(re.findall(r'\b[A-Z]{4,}\b', text))  # kata kapital semua
        exclamations = text.count("!")
        urgent_phrases = len(re.findall(r'(segera|darurat|penting|buruan|cepat)', text_lower))
        if uppercase_words > 5 or exclamations > 3 or urgent_phrases > 3:
            results["extra_flags"] += 1
            results["detected_patterns"].append({
                "type": "broadcast_pattern",
                "pattern": "capslock/urgency",
                "matches": [f"{uppercase_words} caps", f"{exclamations} !", f"{urgent_phrases} urgency words"]
            })

        # =====================================================
        # 🌐 Deteksi URL mencurigakan
        # =====================================================
        if url:
            for pattern in self.suspicious_url_patterns:
                matches = re.findall(pattern, url.lower(), re.IGNORECASE)
                if matches:
                    results["suspicious_url_score"] += len(matches)
                    results["detected_patterns"].append({
                        "type": "suspicious_url",
                        "pattern": pattern,
                        "matches": matches
                    })

        # =====================================================
        # 🏛️ Deteksi sumber terpercaya
        # =====================================================
        if url:
            for domain in self.trusted_sources:
                if domain in url.lower():
                    results["trust_score"] += 1
                    results["detected_patterns"].append({
                        "type": "trusted_source",
                        "pattern": domain,
                        "matches": [domain]
                    })

        # =====================================================
        # 🧮 Klasifikasi akhir + confidence adaptif
        # =====================================================
        total_flags = (
            results["hoax_score"] + 
            results["phishing_score"] + 
            results["clickbait_score"] + 
            results["extra_flags"]
        )
        trust = results["trust_score"]
        suspicious = results["suspicious_url_score"]

        if total_flags >= 5 or (results["hoax_score"] >= 3 and trust == 0):
            classification = "hoax"
            confidence = 0.95
        elif results["phishing_score"] >= 1 and suspicious > 0:
            classification = "phishing"
            confidence = 0.9
        elif 2 <= total_flags <= 4:
            classification = "suspicious"
            confidence = 0.7
        else:
            classification = "valid"
            confidence = 0.85 if trust > 0 else 0.55

        results["classification"] = classification
        results["confidence"] = round(confidence, 2)

        return results


# ============================================================
# 🔧 Standalone Test
# ============================================================
if __name__ == "__main__":
    sample_text = (
        "FORWARD!!! BRO, SEBARKAN SEGERA! "
        "Katanya mulai besok uang Rp100 ribu akan ditarik BI. "
        "Jangan diam saja, buruan tukarkan sebelum dihapus!"
    )
    sample_url = "https://bit.ly/info-baru"
    checker = RulesPrecheck()
    res = checker.analyze(sample_text, sample_url)
    print(json.dumps(res, indent=2, ensure_ascii=False))
