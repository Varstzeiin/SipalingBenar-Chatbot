# ============================================================
# 💬 SiPalingBenar Chatbot — versi clean & stable (auto-dark + base64 logo)
# ============================================================

import streamlit as st
from datetime import datetime
import time
import os
import base64
from modules.analysis_engine import DisinfoAnalysisEngine

# ============================================================
# ⚙️ CONFIG
# ============================================================
st.set_page_config(page_title="SiPalingBenar 🤖", page_icon="💫", layout="centered")

# ============================================================
# 🎨 STYLING
# ============================================================
st.markdown("""
<style>
body { font-family: 'Poppins', sans-serif; }

/* Chat Bubble Styles */
.chat-bubble-user {
  background-color:#0f4c81;
  color:white;
  border-radius:15px 15px 0 15px;
  padding:0.8rem 1rem;
  margin:6px 0 8px auto;
  max-width:80%;
  text-align:right;
  line-height:1.5;
}
.chat-bubble-bot {
  background-color:#f3f5f9;
  color:#000;
  border-radius:15px 15px 15px 0;
  padding:0.8rem 1rem;
  margin:6px auto 8px 0;
  max-width:80%;
  line-height:1.5;
}
[data-testid="stAppViewContainer"][class*="dark"] .chat-bubble-bot {
  background-color:#1e1e1e;
  color:#f1f1f1;
}

/* Brand Card */
#brand-card {
  background-color:#f3f5f9;
  color:#0f0f0f;
  border-radius:18px;
  padding:2rem 1.5rem;
  text-align:center;
  max-width:700px;
  margin:2rem auto;
  box-shadow:0 2px 10px rgba(0,0,0,0.08);
  transition:all 0.3s ease;
}
[data-testid="stAppViewContainer"][class*="dark"] #brand-card {
  background-color:#1e1e1e;
  color:#f1f1f1;
  box-shadow:0 0 12px rgba(255,255,255,0.05);
}

/* Sidebar Title */
.sidebar-logo {
  text-align:center;
  margin-bottom:1rem;
}
.sidebar-logo img {
  border-radius:50%;
  width:80px;
  box-shadow:0 0 8px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧩 LOAD LOGO (Base64)
# ============================================================
LOGO_PATH = "Logoo-Fix-SipalingBener.png"
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
else:
    st.warning("⚠️ Logo tidak ditemukan. Pastikan file 'Logoo-Fix-SipalingBener.png' ada di direktori utama.")
    logo_base64 = None

# ============================================================
# 📦 STATE INIT
# ============================================================
if "engine" not in st.session_state:
    st.session_state.engine = DisinfoAnalysisEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_greeting" not in st.session_state:
    st.session_state.show_greeting = True

# ============================================================
# 🌟 HEADER — muncul hanya sebelum chat dimulai
# ============================================================
if len(st.session_state.messages) == 0:
    if logo_base64:
        st.markdown(f"""
        <div id="brand-card">
            <img src="data:image/png;base64,{logo_base64}" width="150" 
                 style="border-radius:50%; box-shadow:0 0 15px rgba(0,0,0,0.15);">
            <h1 style="font-weight:800; font-size:2rem; margin-top:1rem;">SiPalingBenar 🤖</h1>
            <p style="font-size:1.1rem; margin-top:0.4rem; font-style:italic;">
                “Bedain Fakta, Bukan Drama.”<br>
                <span style="font-size:0.95rem;">Anti-ngadi-ngadi, pro-fakta! 😎</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🧭 SIDEBAR SETTINGS
# ============================================================
with st.sidebar:
    # Pindahkan logo ke sidebar kalau user sudah mulai chat
    if len(st.session_state.messages) > 0 and logo_base64:
        st.markdown(f"""
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{logo_base64}">
            <h3>SiPalingBenar 🤖</h3>
            <p style="font-size:0.85rem; line-height:1.3;">
                <i>“Bedain Fakta, Bukan Drama.”</i><br>
                Anti-ngadi-ngadi, pro-fakta! 😎
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.header("⚙️ Pengaturan")
    google_api_key = st.text_input("🔑 Google API Key (Gemini)", type="password")
    reset = st.button("🔁 Reset Chat")
    st.markdown("---")
    st.caption("👋 Quick Start:")
    st.markdown("- Ketik teks / link berita untuk dicek\n- Tunggu analisis otomatis\n- Lihat hasilnya 👀")

if reset:
    st.session_state.clear()
    st.rerun()

# ============================================================
# 💬 GREETING PERTAMA
# ============================================================
if st.session_state.show_greeting and len(st.session_state.messages) == 0:
    greeting = (
        "Yo bro! 😎 Aku <b>SiPalingBenar</b> — temen lo yang anti-hoaks 💪<br><br>"
        "Ketik teks, kirim link berita, atau tempel langsung di bawah buat mulai 🔍"
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting, "time": datetime.now().strftime('%H:%M')})
    st.session_state.show_greeting = False

# ============================================================
# 💬 TAMPILKAN CHAT HISTORY
# ============================================================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'>{msg['content']}</div>", unsafe_allow_html=True)

# ============================================================
# ✏️ INPUT CHAT
# ============================================================
prompt = st.chat_input("Ketik pesan atau tempel link berita di sini...")

# ============================================================
# 🤖 CHAT HANDLER
# ============================================================
if prompt:
    # Simpan pesan user
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M")
    })
    st.markdown(f"<div class='chat-bubble-user'>{prompt}</div>", unsafe_allow_html=True)

    # 👋 Deteksi pesan penutup dari user
    lower_prompt = prompt.lower().strip()
    quit_keywords = [
        "makasih", "terimakasih", "thank you", "thanks",
        "udah ya", "sampai jumpa", "bye", "dadah"
    ]

    if any(q in lower_prompt for q in quit_keywords):
        reply = (
            "Sama-sama bro 😎! Senang bisa bantu lo bedain fakta dari drama 💫<br><br>"
            "Kalau nanti nemu berita mencurigakan lagi, panggil aja aku kapan pun 🔍<br>"
            "<i>Stay smart, stay critical, stay anti-hoaks!</i> 🧠🔥"
        )
        st.markdown(f"<div class='chat-bubble-bot'>{reply}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "time": datetime.now().strftime("%H:%M")
        })
        st.stop()  # ⛔ Stop di sini, biar gak lanjut ke analisis

    # ============================================================
    # 🔎 Analisis Hoaks / Phishing
    # ============================================================
    with st.spinner("🤖 SiPalingBenar lagi nyidik faktanya..."):
        time.sleep(0.7)

        if not google_api_key:
            reply = "😅 Bro, masukin dulu dong API Key Gemini di sidebar biar aku bisa menganalisis."
        else:
            result = st.session_state.engine.analyze(
                user_input=prompt,
                mode="link" if "http" in prompt else "text",
                provider="Gemini",
                api_key=google_api_key
            )

            if not result["success"]:
                reply = f"⚠️ Gagal menganalisis bro: {result.get('error', 'Error tak dikenal')}"
            else:
                pre = result["rule"]
                rag = result["rag"]
                cls = pre.get("classification", "unknown")

                # Mapping hasil klasifikasi
                if cls in ["hoax", "phishing"]:
                    emoji, tone = "🚨", "Fix, ini meragukan bro! Kemungkinan hoaks/phishing."
                elif cls == "suspicious":
                    emoji, tone = "⚠️", "Agak mencurigakan sih, mending dicek lagi ya bestie."
                else:
                    emoji, tone = "✅", "Aman cuy! Gak ada tanda-tanda hoaks."

                matches = []
                for p in pre.get("detected_patterns", []):
                    for m in p.get("matches", []):
                        if isinstance(m, (list, tuple)):
                            matches.extend(map(str, m))
                        else:
                            matches.append(str(m))
                found = ", ".join(matches) or "-"

                rag_text = (
                    "Belum ada sumber cek fakta relevan."
                    if rag["total_found"] == 0
                    else f"Cek fakta: {rag['fact_checks'][0]['source']} — "
                         f"{rag['fact_checks'][0]['title']} ({rag['fact_checks'][0]['verdict']})."
                )

                reply = f"""
<b>{emoji} {tone}</b><br><br>
🔍 Kata mencurigakan: {found}<br>
🧾 {rag_text}<br><br>
<i>Terima kasih udah cek bareng <b>SiPalingBenar 💫</b></i>
                """

    # Tampilkan hasil analisis ke layar
    st.markdown(f"<div class='chat-bubble-bot'>{reply}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": datetime.now().strftime("%H:%M")
    })
