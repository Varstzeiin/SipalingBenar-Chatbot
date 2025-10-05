# 🧠 **SiPalingBenar** — Chatbot Anti-Disinformasi Indonesia  
> 🗞️ *“Bedain Fakta, Bukan Drama.”*  
> Chatbot edukatif untuk bantu generasi muda melawan hoaks, phishing, dan misinformasi online.

<p align="center">
  <img src="static_assets/SipalingBenar-Logo.png" alt="SiPalingBenar Logo" width="220"/>
</p>

---

### 🏷️ **Badges**
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/LLM-Gemini%2FOpenAI-6B46C1?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?logo=github" />
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen" />
</p>

---

## 🌐 **Deskripsi Singkat**

**SiPalingBenar** adalah *chatbot detektor disinformasi* berbasis **LLM + Rule-Based + Fact-Checking**.  
Didesain untuk mengenali dan menganalisis **berita hoaks, pesan phishing, dan informasi menyesatkan** dalam Bahasa Indonesia.  
Dengan gaya interaktif yang **Gen Z friendly**, ia bukan cuma informatif — tapi juga fun 😎.

---

## ⚙️ **Fitur Utama**

| Fitur | Deskripsi |
|-------|------------|
| 🧱 **Rules Precheck** | Deteksi cepat kata dan pola mencurigakan via regex + lexicon |
| 🧠 **LLM Reasoning** | Analisis konteks menggunakan Gemini/OpenAI |
| 🔎 **RAG Fact-Checking** | Cek silang ke sumber kredibel (Kominfo, Tempo, Mafindo) |
| 💬 **UI Streamlit** | Bubble chat + dark mode otomatis + logo base64 |
| 👋 **Auto Greeting & Farewell** | “Stay anti-hoaks!” pas user pamit |
| 🧯 **Error-safe System** | Fallback otomatis, aman dari tuple/string error |

---

## 🧩 **Struktur Proyek**

disinfo_guardian/
├── data/
│ ├── lexicons/
│ │ ├── hoax_keywords.txt
│ │ ├── phishing_keywords.txt
│ │ └── trusted_sources.txt
│ └── samples/
│ ├── example_texts.csv
│ └── sample_links.txt
│
├── modules/
│ ├── rules_precheck.py
│ ├── url_scraper.py
│ ├── rag_retriever.py
│ ├── llm_reasoner.py
│ ├── response_formatter.py
│ └── analysis_engine.py
│
└── app_chatbot.py

🧪 Contoh Input

📝 Teks:

“Viral! Pemerintah akan menghapus semua akun media sosial minggu depan. Sebarkan sebelum dihapus!”

🔗 Link:

https://contoh-berita.com/post123

🎯 Output:

✅ Kategori: HOAX
⚠️ Kata mencurigakan: viral, sebar, sebelum dihapus
📚 Sumber rujukan: kominfo.go.id, turnbackhoax.id
💡 Rekomendasi: Jangan sebarkan sebelum cek sumber resmi.

Dilisensikan di bawah MIT License — bebas digunakan untuk riset, edukasi, dan pengembangan lebih lanjut.

© 2025 FoviKreatif x Hacktiv8 Final Project — “Stay Anti-Hoaks!”

🤝 Kontributor

👤 Muhammad Vito Aristawidya (Pito)
🎓 Universitas Logistik dan Bisnis Internasional (ULBI)
💼 Developer & Researcher — [LinkedIn](https://www.linkedin.com/in/muhammad-vito-aristawidya-362549191/)