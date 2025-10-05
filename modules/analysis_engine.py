# ============================================================
# 🧠 DisinfoAnalysisEngine (versi adaptif)
# ============================================================

from modules.rules_precheck import RulesPrecheck
from modules.url_scraper import URLScraper
from modules.rag_retriever import RAGRetriever
from modules.llm_reasoner import LLMReasoner
from modules.response_formatter import ResponseFormatter
import traceback

class DisinfoAnalysisEngine:
    def __init__(self):
        self.checker = RulesPrecheck()
        self.scraper = URLScraper()
        self.retriever = RAGRetriever()
        self.reasoner = None  # Inisialisasi nanti pas analisis jalan
        self.formatter = ResponseFormatter()

    def analyze(self, user_input, mode="text", provider="Gemini", api_key=None):
        try:
            # ===============================
            # 🔍 1️⃣ Tentukan teks yang mau dianalisis (dengan fallback adaptif)
            # ===============================
            scraped = None

            # Deteksi otomatis: kalau mengandung "http", treat sebagai URL
            if mode == "link" or ("http" in user_input):
                scraped = self.scraper.scrape_url(user_input)

                # Gunakan hasil scraping kalau berhasil, atau fallback URL text kalau gagal
                text_to_analyze = scraped.get("content", user_input)

                # Deteksi tambahan: domain mencurigakan (.xyz, .site, dll)
                if scraped.get("is_suspicious"):
                    # Tambahkan pattern ekstra ke rule_result nanti
                    suspicious_domain = scraped.get("domain", "domain mencurigakan")
                    print(f"⚠️ Detected suspicious domain: {suspicious_domain}")

            else:
                # Input berupa teks langsung
                text_to_analyze = user_input

            # ===============================
            # 🧱 2️⃣ Rules-based Precheck
            # ===============================
            rule_result = self.checker.analyze(text_to_analyze, url=user_input)

            # 🔎 Tambahan: jika domain mencurigakan dari URLScraper → auto-flag phishing
            if scraped and scraped.get("is_suspicious"):
                rule_result["detected_patterns"].append({
                    "type": "suspicious_domain",
                    "matches": [scraped.get("domain", "unknown-domain")]
                })
                rule_result["classification"] = "phishing"



            # ===============================
            # 🧠 3️⃣ LLM Reasoner (Gemini/GPT)
            # ===============================
            if not self.reasoner:
                self.reasoner = LLMReasoner(provider=provider, api_key=api_key)

            llm_result = self.reasoner.analyze(
                {
                    "text": text_to_analyze,
                    "rule_result": rule_result,
                    "provider": provider,
                    "api_key": api_key,
                }
            )

            # ===============================
            # 🔎 4️⃣ RAG Fact-Checking
            # ===============================
            rag_result = self.retriever.find_related_fact_checks(text_to_analyze)

            # ===============================
            # 🧩 5️⃣ Format hasil akhir
            # ===============================
            formatted = self.formatter.format_output(
                rule_result, llm_result, rag_result
            )

            return {
                "success": True,
                "rule": rule_result,
                "llm": llm_result,
                "rag": rag_result,
                "formatted": formatted,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "trace": traceback.format_exc()}
