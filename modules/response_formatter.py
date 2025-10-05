# ============================================================
# 🧩 ResponseFormatter — Modul untuk format hasil analisis akhir
# ============================================================

class ResponseFormatter:
    """
    Gabungkan hasil dari RulesPrecheck, LLMReasoner, dan RAGRetriever 
    menjadi satu output rapi untuk chatbot SiPalingBenar.
    """

    def format_output(self, rule_result, llm_result, rag_result):
        """
        Format hasil pipeline menjadi ringkasan text.
        Args:
            rule_result: hasil dari RulesPrecheck
            llm_result: hasil dari LLMReasoner
            rag_result: hasil dari RAGRetriever
        Returns:
            dict berisi teks ringkasan & info penting
        """
        classification = rule_result.get("classification", "unknown").capitalize()

        summary_parts = []
        summary_parts.append(f"🧩 **Kategori:** {classification}")

        # 🔍 Deteksi kata/pola mencurigakan
        detected = rule_result.get("detected_patterns", [])
        if detected:
            matches = []
            for d in detected:
                m = ", ".join(
                    [x if isinstance(x, str) else " ".join(map(str, x)) for x in d.get("matches", [])]
                )
                if m:
                    matches.append(f"- {d.get('type', 'unknown')}: {m}")
            if matches:
                summary_parts.append("\n**🔍 Pola mencurigakan:**\n" + "\n".join(matches))

        # 🔎 Hasil RAG (cek fakta)
        if rag_result and rag_result.get("total_found", 0) > 0:
            fc = rag_result["fact_checks"][0]
            summary_parts.append(
                f"**🔎 Cek Fakta:** {fc['source']} — {fc['title']} ({fc['verdict']})"
            )
        else:
            summary_parts.append("**🔎 Cek Fakta:** Tidak ditemukan sumber relevan")

        # 🧠 Reasoning AI
        if llm_result and llm_result.get("success", True):
            reasoning = (
                llm_result.get("summary")
                or llm_result.get("reasoning")
                or llm_result.get("analysis")
                or ""
            )
            if reasoning:
                summary_parts.append(f"\n🧠 **Analisis AI:** {reasoning}")

        # Gabung semua hasil
        return {
            "summary_text": "\n".join(summary_parts),
            "classification": classification.lower(),
            "sources": rag_result.get("fact_checks", []) if rag_result else [],
        }
