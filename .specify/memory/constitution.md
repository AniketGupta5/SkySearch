# SkySearch — Project Constitution

## Purpose
SkySearch is an AI-powered flight explorer that generates realistic flight data using LLMs (Groq / Llama 3). It is NOT a booking engine — no payments, no real reservations. It is a demo/hackathon project showcasing AI-generated structured data in a Skyscanner-style UI.

## Core Principles
1. **AI-first data** — All flight results are LLM-generated JSON. No real flight API is used.
2. **Zero friction** — Users only need a free Groq API key (sidebar input). No auth, no accounts.
3. **Realistic UX** — UI must feel like a real flight search product (stats bar, sorting, cabin classes).
4. **Single-file simplicity** — `app.py` is the entire app. Keep it that way unless complexity demands splitting.
5. **Dark sky theme** — `#0b1120` background, blue accents (`#3b82f6`, `#60a5fa`), Inter font.

## Tech Stack
- **Frontend/Backend**: Python + Streamlit (single-file)
- **LLM**: Groq API — `llama-3.3-70b-versatile`
- **Language**: Python 3.10+
- **Deployment target**: Streamlit Community Cloud or local

## Non-Goals
- No real booking or payment flow
- No database / persistent storage
- No user authentication
- No mobile-native app

## Constraints
- Must run with `streamlit run app.py` — zero config files needed
- API key is runtime-injected via sidebar (never hardcoded)
- All LLM responses must be pure JSON (no markdown fences, no preamble)
