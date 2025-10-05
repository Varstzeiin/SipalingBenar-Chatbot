import streamlit as st
import os
import subprocess
from datetime import datetime
import traceback

# Import modul utama
from modules.rules_precheck import RulesPrecheck
from modules.url_scraper import URLScraper
from modules.llm_reasoner import LLMReasoner
from modules.rag_retriever import RAGRetriever


# ============================================================
# 🎨 GLOBAL STYLE (responsive + dark mode aware)
# ============================================================
st.markdown("""
<style>
/* Root font and spacing */
body {
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.6;
}

/* Responsive container for blocks */
.responsive-card {
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin: 0 auto 1.5rem auto;
    width: 95%;
    max-width: 850px;
    transition: all 0.3s ease;
}

/* Light theme (default Streamlit) */
.responsive-card {
    background-color: #f3f5f9;
    color: #0f0f0f;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}

/* Dark theme override (Streamlit dark mode) */
[data-testid="stAppViewContainer"][class*="dark"] .responsive-card {
    background-color: #1e1e1e;
    color: #f1f1f1;
    box-shadow: 0 0 12px rgba(255,255,255,0.08);
}

/* Responsive behavior for small devices */
@media (max-width: 768px) {
    .responsive-card {
        padding: 1.2rem 1.4rem;
        width: 96%;
    }
    .responsive-card h1 {
        font-size: 1.8rem !important;
    }
    .responsive-card p {
        font-size: 1rem !important;
    }
}

/* Headings */
h1, h2, h3, h4 {
    color: #0f4c81;
    font-weight: 800;
}

/* Accent color adjustment in dark mode */
[data-testid="stAppViewContainer"][class*="dark"] h1,
[data-testid="stAppViewContainer"][class*="dark"] h2,
[data-testid="stAppViewContainer"][class*="dark"] h3 {
    color: #79b8ff;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔁 HELPER: fallback ringkasan sederhana kalau LLM gagal
# ============================================================
def generate_plain_summary(precheck: dict, text: str) -> dict:
    """Buat ringkasan mudah dipahami untuk pengguna awam."""
    cls = precheck.get("classification", "unknown")
    conf = precheck.get("confidence", 0.0)
    red_flags = []
    for p in precheck.get("detected_patterns", []):
        t = p.get("type")
        matches = p.get("matches", [])
        if matches:
            red_flags.append(f"{t.replace('_', ' ')}: {', '.join(map(str, matches))}")

    if cls in ("hoax", "phishing"):
        status = "🚨 Terindikasi Berbahaya"
        rec = [
            "Jangan sebar atau bagikan dulu.",
            "Cek di situs resmi seperti turnbackhoax.id atau kominfo.go.id.",
            "Laporkan ke admin grup atau pihak terkait."
        ]
    elif cls == "suspicious":
        status = "⚠️ Mencurigakan, Perlu Verifikasi"
        rec = [
            "Periksa klaim ini di situs cek fakta.",
            "Jangan panik, jangan langsung percaya.",
            "Cari sumber resmi sebelum membagikan."
        ]
    else:
        status = "✅ Kemungkinan Aman"
        rec = ["Tampaknya tidak berbahaya, tapi tetap cek sumber."]

    return {
        "status": status,
        "confidence": round(conf * 100, 1),
        "reasons": red_flags[:5],
        "recommendations": rec
    }


# ============================================================
# 🧩 PAGE CONFIG
# ============================================================
st.set_page_config(page_title="🛡️ Disinfo Guardian", page_icon="🧠", layout="centered")

st.markdown("""
<div class="responsive-card" style="text-align:center;">
    <h1>🛡️ Disinfo Guardian</h1>
    <p style="font-size:1.15rem; margin-top:0.5rem;">
        Sistem Analisis <b>Hoaks</b>, <b>Phishing</b>, dan <b>Disinformasi</b><br>
        berbasis kombinasi teknologi modern:
    </p>
    <p style="font-size:1.05rem; line-height:1.7; margin-top:1rem;">
        🧱 <b>Rule-based Precheck</b> untuk deteksi cepat<br>
        🧠 <b>LLM Reasoning</b> (Gemini / GPT) untuk analisis kontekstual<br>
        🔎 <b>RAG Fact Checking</b> (Kominfo, Tempo, Mafindo) untuk verifikasi fakta
    </p>
</div>
""", unsafe_allow_html=True)



# ============================================================
# ⚙️ INITIAL SETUP CHECK
# ============================================================
if not os.path.exists("static_assets/lexicons"):
    st.warning("⚠️ Folder `static_assets/` belum ditemukan. Menjalankan setup otomatis...")
    try:
        subprocess.run(["python", "data/setup_static_assets.py"], check=True)
        st.success("✅ Berhasil membuat static assets!")
    except Exception as e:
        st.error(f"Gagal menjalankan setup: {e}")
        st.stop()

# ============================================================
# 🔧 MODULE INITIALIZATION
# ============================================================
if "checker" not in st.session_state:
    st.session_state.checker = RulesPrecheck()
if "scraper" not in st.session_state:
    st.session_state.scraper = URLScraper()
if "retriever" not in st.session_state:
    st.session_state.retriever = RAGRetriever()

# ============================================================
# 📝 INPUT SECTION
# ============================================================
st.divider()

# Blok informasi besar dan menonjol di atas input
st.markdown("""
<div class="responsive-card" style="text-align:center;">
    <h2>🧠 Sistem Analisis Disinformasi</h2>
    <p class="desc-text">
        Masukkan <b>teks</b> atau <b>tautan berita</b> untuk mendeteksi apakah konten tersebut mengandung
        <span class="hoax-text">hoaks</span>,
        <span class="phish-text">phishing</span>,
        atau <span class="valid-text">informasi valid</span>.
    </p>
</div>

<style>
/* Gaya untuk teks deskriptif adaptif ke tema */
.desc-text {
    font-size: 1.1rem;
    line-height: 1.6;
    margin-top: 0.5rem;
    color: #1a1a1a;  /* default untuk light mode */
}

/* Warna kata spesifik */
.hoax-text { color: #e74c3c; font-weight: 700; }
.phish-text { color: #f1c40f; font-weight: 700; }
.valid-text { color: #2ecc71; font-weight: 700; }

/* Override warna utama di dark mode */
[data-testid="stAppViewContainer"][class*="dark"] .desc-text {
    color: #f1f1f1 !important;  /* teks utama jadi terang di dark mode */
}
</style>
""", unsafe_allow_html=True)


st.write("")  # spacer

# Ubah radio jadi selectbox
input_mode = st.selectbox("📥 **Pilih Jenis Input**", ["📝 Teks langsung", "🔗 Link berita"])
user_input = st.text_area(
    "Masukkan teks berita:" if input_mode == "📝 Teks langsung" else "Masukkan link berita:",
    height=160,
    placeholder="Ketik atau tempel teks / link berita di sini..."
)

st.write("")  # spacer

# Buat judul bagian model LLM jadi besar dan bold
st.markdown("""
<h3 style="font-weight:700; color:#0f4c81;">⚙️ Pilih Model LLM</h3>
""", unsafe_allow_html=True)

provider = st.selectbox("🧩 Model LLM yang digunakan", ["Gemini", "OpenAI"])
api_key = st.text_input(f"🔑 Masukkan API Key untuk {provider.upper()}:", type="password")

st.write("")  # spacer
analyze_btn = st.button("🚀 Jalankan Analisis Sekarang", use_container_width=True)

# ============================================================
# 🔍 PIPELINE PROCESSING
# ============================================================
if analyze_btn:
    if not user_input.strip():
        st.warning("⚠️ Harap masukkan teks atau link terlebih dahulu.")
        st.stop()

    if not api_key.strip():
        st.warning("⚠️ Harap isi API key terlebih dahulu.")
        st.stop()

    try:
        with st.spinner("Sedang menganalisis... ⏳"):
            # 1️⃣ Scrape URL jika input berupa link
            if input_mode == "🔗 Link berita":
                scrape_result = st.session_state.scraper.scrape_url(user_input)
                if not scrape_result["success"]:
                    st.error(f"Gagal scraping: {scrape_result.get('error')}")
                    st.stop()
                text_to_analyze = scrape_result["content"]
                url = scrape_result["url"]
            else:
                scrape_result = None
                text_to_analyze = user_input
                url = None

            # 2️⃣ Rule-based Precheck
            checker = st.session_state.checker
            precheck_result = checker.analyze(text_to_analyze, url=url)

            # 3️⃣ LLM Reasoning
            llm = LLMReasoner(provider=provider, api_key=api_key)
            llm_input = {
                "title": scrape_result["title"] if scrape_result else "Teks Langsung",
                "text": text_to_analyze,
                "url": url or "—"
            }
            llm_result = llm.analyze(llm_input, precheck_result)

            # 4️⃣ RAG Fact Checking
            retriever = st.session_state.retriever
            rag_result = retriever.find_related_fact_checks(text_to_analyze)

            # 5️⃣ Gabungkan hasil akhir
            final_output = {
                "timestamp": datetime.now().isoformat(),
                "rule_result": precheck_result,
                "llm_result": llm_result,
                "rag_result": rag_result,
                "source_meta": {
                    "provider": provider,
                    "scraped_domain": scrape_result["domain"] if scrape_result else None,
                    "trusted_source": scrape_result["is_trusted"] if scrape_result else None
                }
            }

        # ============================================================
        # 🧠 DISPLAY OUTPUT
        # ============================================================
        st.success("✅ Analisis selesai!")

        # ---------- RULES RESULT ----------
        st.subheader("📊 Deteksi Awal (Rules Precheck)")

        # Ambil data penting
        hoax_score = precheck_result.get("hoax_score", 0)
        phish_score = precheck_result.get("phishing_score", 0)
        clickbait_score = precheck_result.get("clickbait_score", 0)
        trust_score = precheck_result.get("trust_score", 0)
        detected = precheck_result.get("detected_patterns", [])

        # Ringkasan angka
        st.markdown("""
        <div style="display:flex; justify-content:space-around; padding:10px; text-align:center;">
            <div style="background:#ffe6e6; border-radius:10px; padding:10px 25px;">
                <h4 style="color:#b30000;">🔥 Hoax Score</h4>
                <p style="font-size:1.5rem; font-weight:800;">{}</p>
            </div>
            <div style="background:#fff3cd; border-radius:10px; padding:10px 25px;">
                <h4 style="color:#856404;">🎣 Phishing Score</h4>
                <p style="font-size:1.5rem; font-weight:800;">{}</p>
            </div>
            <div style="background:#d1ecf1; border-radius:10px; padding:10px 25px;">
                <h4 style="color:#0c5460;">🪧 Clickbait Score</h4>
                <p style="font-size:1.5rem; font-weight:800;">{}</p>
            </div>
        </div>
        """.format(hoax_score, phish_score, clickbait_score), unsafe_allow_html=True)

        # Daftar pola yang terdeteksi
        if detected:
            st.markdown("### 🔍 Pola Mencurigakan yang Ditemukan:")
            for p in detected:
                matches = ", ".join(p.get("matches", []))
                tipe = p.get("type", "").replace("_", " ").title()
                st.write(f"- **{tipe}:** {matches}")
        else:
            st.info("Tidak ditemukan pola mencurigakan di teks ini.")

        # Indikator klasifikasi umum
        classification = precheck_result.get("classification", "unknown")
        if classification in ["hoax", "phishing"]:
            st.error("🚨 Konten terindikasi **Berbahaya (Hoaks / Phishing)**")
        elif classification == "suspicious":
            st.warning("⚠️ Konten **Mencurigakan**, perlu verifikasi lanjutan.")
        else:
            st.success("✅ Konten tampaknya **Aman / Valid**")


        # Tambahkan indikator cepat agar mudah dimengerti
        if precheck_result["classification"] in ["hoax", "phishing"]:
            st.error("🚨 Konten terindikasi **Berbahaya (Hoaks/Phishing)**")
        elif precheck_result["classification"] == "suspicious":
            st.warning("⚠️ Konten **Mencurigakan**, sebaiknya diverifikasi dulu.")
        else:
            st.success("✅ Konten tampaknya **Aman / Valid**")

        # ---------- LLM RESULT ----------
        st.subheader("🧠 Analisis Kontekstual (LLM)")

        if not llm_result.get("success", True):
            st.warning("⚠️ Analisis AI tidak tersedia — menampilkan ringkasan sederhana berdasarkan sistem aturan.")

            # fallback ringkasan
            fallback = generate_plain_summary(precheck_result, text_to_analyze)
            st.markdown(f"### {fallback['status']}")
            st.markdown(f"**Tingkat keyakinan sistem:** {fallback['confidence']}%")

            if fallback["reasons"]:
                st.markdown("**Tanda mencurigakan yang terdeteksi:**")
                for r in fallback["reasons"]:
                    st.write(f"- {r}")

            st.markdown("**Rekomendasi tindakan:**")
            for r in fallback["recommendations"]:
                st.write(f"- {r}")

            plain_text = (
                f"{fallback['status']}\n"
                f"Keyakinan: {fallback['confidence']}%\n"
                f"Alasan: {', '.join(fallback['reasons'])}\n"
                f"Rekomendasi: {'; '.join(fallback['recommendations'])}"
            )
            st.download_button("📋 Simpan Ringkasan (TXT)", data=plain_text, file_name="ringkasan_disinfo.txt")

        else:
            st.json(llm_result)

        # ---------- RAG RESULT ----------
        st.subheader("🔎 Cek Fakta (RAG Retrieval)")
        if rag_result["total_found"] == 0:
            st.info("Tidak ditemukan hasil cek fakta relevan.")
        else:
            for item in rag_result["fact_checks"]:
                st.markdown(
                    f"**{item['title']}** — *{item['source']} ({item['verdict']})*  \n"
                    f"[Baca selengkapnya]({item['url']})"
                )

        st.divider()
        st.download_button(
            label="⬇️ Unduh Hasil Analisis (JSON)",
            data=str(final_output),
            file_name=f"disinfo_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    except Exception as e:
        st.error("❌ Terjadi kesalahan saat analisis.")
        st.code(traceback.format_exc())

        # ============================================================
        # 🧠 DISPLAY OUTPUT
        # ============================================================
        st.success("✅ Analisis selesai!")
        st.subheader("📊 Deteksi Awal (Rules Precheck)")
        st.json(precheck_result)

        st.subheader("🧠 Analisis Kontekstual (LLM)")
        if not llm_result.get("success", True):
            st.warning("⚠️ Analisis AI tidak tersedia — menampilkan ringkasan sederhana berdasarkan sistem aturan.")

            fallback = generate_plain_summary(precheck_result, text_to_analyze)

            st.markdown(f"### {fallback['status']}")
            st.markdown(f"**Tingkat keyakinan sistem:** {fallback['confidence']}%")

            if fallback["reasons"]:
                st.markdown("**Tanda mencurigakan yang terdeteksi:**")
                for r in fallback["reasons"]:
                    st.write(f"- {r}")

            st.markdown("**Rekomendasi tindakan:**")
            for r in fallback["recommendations"]:
                st.write(f"- {r}")

            # Tombol download hasil ringkasan
            plain_text = (
                f"{fallback['status']}\n"
                f"Keyakinan: {fallback['confidence']}%\n"
                f"Alasan: {', '.join(fallback['reasons'])}\n"
                f"Rekomendasi: {'; '.join(fallback['recommendations'])}"
            )
            st.download_button("📋 Simpan Ringkasan (TXT)", data=plain_text, file_name="ringkasan_disinfo.txt")
        else:
            st.json(llm_result)


        st.subheader("🔎 Cek Fakta (RAG Retrieval)")
        if rag_result["total_found"] == 0:
            st.info("Tidak ditemukan hasil cek fakta relevan.")
        else:
            for item in rag_result["fact_checks"]:
                st.markdown(f"**{item['title']}** — *{item['source']} ({item['verdict']})*  \n"
                            f"[Baca selengkapnya]({item['url']})")

        st.divider()
        st.download_button(
            label="⬇️ Unduh Hasil Analisis (JSON)",
            data=str(final_output),
            file_name=f"disinfo_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    except Exception as e:
        st.error("❌ Terjadi kesalahan saat analisis.")
        st.code(traceback.format_exc())
