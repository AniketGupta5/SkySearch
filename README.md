# ✈ SkySearch — AI Flight Finder

An AI-powered Skyscanner-style flight explorer built with **Streamlit** and **Groq (Llama 3)**.
Search flights between any two airports — realistic results, no booking, no payment.

## 🚀 Features
- 🤖 AI-generated realistic flight data via Groq (Llama 3 70B)
- 🌍 Search any route using IATA codes
- 💰 Multi-currency support (USD, INR, EUR, GBP, AED, SGD)
- 🛫 Economy / Business / First class options
- ⚡ Sort by price, duration, or departure time
- 📊 Stats bar — cheapest, average, most expensive fares
- 🤖 AI travel recommendation for each search
- 🌙 Dark sky-themed UI

## ⚡ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 → paste your Groq key in the sidebar → search!

## 🔑 Get a Free Groq API Key
1. Go to https://console.groq.com
2. Sign up free (no credit card)
3. Create an API key → copy it
4. Paste in the app sidebar

## 📁 Project Structure
```
skysearch/
├── app.py           # Main Streamlit app
├── requirements.txt
└── README.md
```

## 🛠 Tech Stack
- Python + Streamlit
- Groq API (Llama 3 70B) for flight generation + AI recommendations
- Zero external flight API needed

---
Built for Hackathon 2026 · Solo project · Powered by Groq
