import streamlit as st
import requests
import json
import re
from datetime import date, timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkySearch – Find Flights",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Translations ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "hero_title": "✈ SkySearch",
        "hero_sub": "AI-powered flight explorer — search routes across 400+ airlines.",
        "ai_backend_header": "### 🤖 AI Backend",
        "backend_groq": "☁️ Groq (Cloud)",
        "backend_ollama": "🖥️ Ollama (Local)",
        "groq_key_header": "**🔑 Groq API Key**",
        "groq_key_caption": "Free key at [console.groq.com](https://console.groq.com)",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq Model",
        "ollama_url_label": "**🖥️ Ollama Base URL**",
        "ollama_url_caption": "Default: http://localhost:11434",
        "ollama_model_label": "Ollama Model",
        "ollama_model_placeholder": "e.g. llama3, mistral, phi3",
        "ollama_tip": "💡 Run `ollama serve` locally before searching.",
        "quick_route": "✈ Quick route picker",
        "currency_label": "Currency",
        "cabin_label": "Cabin class",
        "from_label": "From (IATA)",
        "to_label": "To (IATA)",
        "from_placeholder": "e.g. HYD",
        "to_placeholder": "e.g. DXB",
        "date_label": "Departure date",
        "passengers_label": "Passengers",
        "search_btn": "🔍  Search Flights with AI",
        "sort_label": "Sort by",
        "sort_price": "💰 Price (low → high)",
        "sort_duration": "⏱ Duration (shortest first)",
        "sort_depart": "🛫 Departure time",
        "stat_found": "Flights found",
        "stat_cheapest": "Cheapest fare",
        "stat_expensive": "Most expensive",
        "stat_avg": "Average price",
        "ai_badge": "🤖 AI Recommendation",
        "nonstop": "Nonstop",
        "stop": "stop", "stops": "stops",
        "via_label": "via",
        "refundable": "Refundable",
        "non_refundable": "Non-refundable",
        "per_person": "per person", "pax": "pax",
        "next_day": "+1 day",
        "spinner_flights": "✈ AI is finding flights...",
        "spinner_rec": "🤖 Getting AI recommendation...",
        "err_no_key": "⚠️ Please enter your Groq API Key in the sidebar.",
        "err_no_model": "⚠️ Please enter an Ollama model name (e.g. llama3).",
        "err_no_iata": "⚠️ Please enter both origin and destination IATA codes.",
        "err_iata_len": "⚠️ IATA codes are exactly 3 letters (e.g. HYD, DXB, LHR).",
        "err_same": "⚠️ Origin and destination cannot be the same.",
        "err_ollama": "⚠️ Could not reach Ollama. Is `ollama serve` running?",
        "footer": "SkySearch · Streamlit + Groq / Ollama · Hackathon 2026",
        "powered_groq": "⚡ Powered by Groq Cloud · Results are AI-generated for informational purposes",
        "powered_ollama": "⚡ Powered by Ollama (local) · Results are AI-generated for informational purposes",
        "flights_heading": "Flights",
        "language_label": "🌐 Language / भाषा / భాష",
        "cabin_options": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in English.",
    },
    "हिंदी": {
        "hero_title": "✈ स्काईसर्च",
        "hero_sub": "AI-संचालित फ्लाइट एक्सप्लोरर — 400+ एयरलाइंस में रूट खोजें।",
        "ai_backend_header": "### 🤖 AI बैकएंड",
        "backend_groq": "☁️ Groq (क्लाउड)",
        "backend_ollama": "🖥️ Ollama (लोकल)",
        "groq_key_header": "**🔑 Groq API कुंजी**",
        "groq_key_caption": "[console.groq.com](https://console.groq.com) पर मुफ्त कुंजी पाएं",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq मॉडल",
        "ollama_url_label": "**🖥️ Ollama URL**",
        "ollama_url_caption": "डिफ़ॉल्ट: http://localhost:11434",
        "ollama_model_label": "Ollama मॉडल",
        "ollama_model_placeholder": "जैसे llama3, mistral, phi3",
        "ollama_tip": "💡 खोज से पहले `ollama serve` चलाएं।",
        "quick_route": "✈ त्वरित रूट चुनें",
        "currency_label": "मुद्रा",
        "cabin_label": "केबिन श्रेणी",
        "from_label": "से (IATA कोड)",
        "to_label": "तक (IATA कोड)",
        "from_placeholder": "जैसे HYD",
        "to_placeholder": "जैसे DXB",
        "date_label": "प्रस्थान तिथि",
        "passengers_label": "यात्री",
        "search_btn": "🔍  AI से फ्लाइट खोजें",
        "sort_label": "क्रमबद्ध करें",
        "sort_price": "💰 मूल्य (कम → अधिक)",
        "sort_duration": "⏱ अवधि (सबसे कम पहले)",
        "sort_depart": "🛫 प्रस्थान समय",
        "stat_found": "फ्लाइट मिली",
        "stat_cheapest": "सबसे सस्ता किराया",
        "stat_expensive": "सबसे महंगा",
        "stat_avg": "औसत मूल्य",
        "ai_badge": "🤖 AI सुझाव",
        "nonstop": "सीधी उड़ान",
        "stop": "स्टॉप", "stops": "स्टॉप",
        "via_label": "होते हुए",
        "refundable": "वापसी योग्य",
        "non_refundable": "वापसी योग्य नहीं",
        "per_person": "प्रति व्यक्ति", "pax": "यात्री",
        "next_day": "+1 दिन",
        "spinner_flights": "✈ AI फ्लाइट खोज रहा है...",
        "spinner_rec": "🤖 AI सुझाव आ रहा है...",
        "err_no_key": "⚠️ कृपया साइडबार में Groq API कुंजी दर्ज करें।",
        "err_no_model": "⚠️ कृपया Ollama मॉडल नाम दर्ज करें (जैसे llama3)।",
        "err_no_iata": "⚠️ कृपया स्रोत और गंतव्य दोनों IATA कोड दर्ज करें।",
        "err_iata_len": "⚠️ IATA कोड ठीक 3 अक्षर के होते हैं (जैसे HYD, DXB, LHR)।",
        "err_same": "⚠️ स्रोत और गंतव्य एक समान नहीं हो सकते।",
        "err_ollama": "⚠️ Ollama से कनेक्ट नहीं हो सका। क्या `ollama serve` चल रहा है?",
        "footer": "स्काईसर्च · Streamlit + Groq / Ollama · हैकाथॉन 2026",
        "powered_groq": "⚡ Groq क्लाउड द्वारा · परिणाम AI-जनित हैं",
        "powered_ollama": "⚡ Ollama (लोकल) द्वारा · परिणाम AI-जनित हैं",
        "flights_heading": "फ्लाइट",
        "language_label": "🌐 Language / भाषा / భాష",
        "cabin_options": ["इकोनॉमी", "प्रीमियम इकोनॉमी", "बिज़नेस", "फर्स्ट"],
        "cabin_api_map": {"इकोनॉमी": "ECONOMY", "प्रीमियम इकोनॉमी": "PREMIUM_ECONOMY", "बिज़नेस": "BUSINESS", "फर्स्ट": "FIRST"},
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in Hindi (Devanagari script).",
    },
    "తెలుగు": {
        "hero_title": "✈ స్కైసెర్చ్",
        "hero_sub": "AI-ఆధారిత విమాన అన్వేషకుడు — 400+ ఎయిర్‌లైన్లలో మార్గాలు వెతకండి.",
        "ai_backend_header": "### 🤖 AI బ్యాకెండ్",
        "backend_groq": "☁️ Groq (క్లౌడ్)",
        "backend_ollama": "🖥️ Ollama (లోకల్)",
        "groq_key_header": "**🔑 Groq API కీ**",
        "groq_key_caption": "[console.groq.com](https://console.groq.com) వద్ద ఉచిత కీ పొందండి",
        "groq_key_placeholder": "gsk_...",
        "groq_model_label": "Groq మోడల్",
        "ollama_url_label": "**🖥️ Ollama URL**",
        "ollama_url_caption": "డిఫాల్ట్: http://localhost:11434",
        "ollama_model_label": "Ollama మోడల్",
        "ollama_model_placeholder": "ఉదా: llama3, mistral, phi3",
        "ollama_tip": "💡 వెతకడానికి ముందు `ollama serve` రన్ చేయండి.",
        "quick_route": "✈ త్వరిత మార్గం ఎంచుకోండి",
        "currency_label": "కరెన్సీ",
        "cabin_label": "క్యాబిన్ తరగతి",
        "from_label": "నుండి (IATA కోడ్)",
        "to_label": "వరకు (IATA కోడ్)",
        "from_placeholder": "ఉదా: HYD",
        "to_placeholder": "ఉదా: DXB",
        "date_label": "బయలుదేరే తేదీ",
        "passengers_label": "ప్రయాణికులు",
        "search_btn": "🔍  AI తో విమానాలు వెతకండి",
        "sort_label": "క్రమపరచండి",
        "sort_price": "💰 ధర (తక్కువ → ఎక్కువ)",
        "sort_duration": "⏱ వ్యవధి (తక్కువ మొదట)",
        "sort_depart": "🛫 బయలుదేరే సమయం",
        "stat_found": "విమానాలు దొరికాయి",
        "stat_cheapest": "అత్యంత చౌకైన చార్జీ",
        "stat_expensive": "అత్యంత ఖరీదైన",
        "stat_avg": "సగటు ధర",
        "ai_badge": "🤖 AI సూచన",
        "nonstop": "నేరుగా",
        "stop": "స్టాప్", "stops": "స్టాప్‌లు",
        "via_label": "మీదుగా",
        "refundable": "రీఫండ్ అవుతుంది",
        "non_refundable": "రీఫండ్ కాదు",
        "per_person": "తలసరి", "pax": "ప్రయాణికులు",
        "next_day": "+1 రోజు",
        "spinner_flights": "✈ AI విమానాలు వెతుకుతోంది...",
        "spinner_rec": "🤖 AI సూచన వస్తోంది...",
        "err_no_key": "⚠️ దయచేసి సైడ్‌బార్‌లో Groq API కీని నమోదు చేయండి.",
        "err_no_model": "⚠️ దయచేసి Ollama మోడల్ పేరు నమోదు చేయండి (ఉదా: llama3).",
        "err_no_iata": "⚠️ దయచేసి మూలం మరియు గమ్యం రెండు IATA కోడ్‌లు నమోదు చేయండి.",
        "err_iata_len": "⚠️ IATA కోడ్‌లు సరిగ్గా 3 అక్షరాలు (ఉదా: HYD, DXB, LHR).",
        "err_same": "⚠️ మూలం మరియు గమ్యం ఒకే విమానాశ్రయం కాకూడదు.",
        "err_ollama": "⚠️ Ollama కి కనెక్ట్ కాలేదు. `ollama serve` రన్ అవుతోందా?",
        "footer": "స్కైసెర్చ్ · Streamlit + Groq / Ollama · హ్యాకథాన్ 2026",
        "powered_groq": "⚡ Groq క్లౌడ్ ద్వారా · ఫలితాలు AI-రూపొందించబడినవి",
        "powered_ollama": "⚡ Ollama (లోకల్) ద్వారా · ఫలితాలు AI-రూపొందించబడినవి",
        "flights_heading": "విమానాలు",
        "language_label": "🌐 Language / భాషా / భాష",
        "cabin_options": ["ఎకానమీ", "ప్రీమియం ఎకానమీ", "బిజినెస్", "ఫస్ట్"],
        "cabin_api_map": {"ఎకానమీ": "ECONOMY", "ప్రీమియం ఎకానమీ": "PREMIUM_ECONOMY", "బిజినెస్": "BUSINESS", "ఫస్ట్": "FIRST"},
        "rec_prompt": "Which is best value and which is best for comfort? Be brief. Reply in Telugu script.",
    },
}

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# ── AI Backend calls ───────────────────────────────────────────────────────────
def call_groq(api_key, prompt, system_prompt, model, max_tokens=3000):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=body, timeout=30
    )
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    raise Exception(f"Groq error {r.status_code}: {r.text[:300]}")


def call_ollama(base_url, model, prompt, system_prompt, max_tokens=3000):
    url = base_url.rstrip("/") + "/api/chat"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.7},
    }
    try:
        r = requests.post(url, json=body, timeout=120)
    except requests.exceptions.ConnectionError:
        raise Exception("ollama_unreachable")
    if r.status_code == 200:
        return r.json()["message"]["content"]
    raise Exception(f"Ollama error {r.status_code}: {r.text[:300]}")


def call_ai(prompt, system_prompt, backend_cfg, max_tokens=3000):
    """Unified call — routes to Groq or Ollama based on sidebar config."""
    if backend_cfg["backend"] == "groq":
        return call_groq(
            backend_cfg["groq_key"], prompt, system_prompt,
            backend_cfg["groq_model"], max_tokens
        )
    else:
        return call_ollama(
            backend_cfg["ollama_url"], backend_cfg["ollama_model"],
            prompt, system_prompt, max_tokens
        )


# ── Flight logic ───────────────────────────────────────────────────────────────
FLIGHT_SYSTEM = (
    "You are a flight data engine. Always respond with valid JSON only. "
    "No explanation, no markdown fences, no extra text — pure JSON array."
)

def generate_flights(backend_cfg, origin, destination, depart_date, adults, cabin, currency):
    prompt = f"""
Generate exactly 10 realistic flight options from {origin} to {destination}
on {depart_date} for {adults} adult(s) in {cabin} class. Currency: {currency}.

Use real airlines that actually fly this route. Include a mix of nonstop and 1-stop flights.
Make prices, durations, and times realistic for this route.

Return a JSON array of 10 objects, each with exactly these fields:
- airline: string
- airline_code: string (2-letter IATA)
- flight_number: string (e.g. EK512)
- departure_time: string HH:MM
- arrival_time: string HH:MM
- arrival_date_offset: integer 0 or 1
- duration: string (e.g. "2h 30m")
- stops: integer 0 or 1
- via: string (layover airport code, empty string if nonstop)
- price: integer (in {currency})
- aircraft: string
- baggage: string
- meal: string
- refundable: boolean

Return ONLY the JSON array, nothing else.
"""
    raw = call_ai(prompt, FLIGHT_SYSTEM, backend_cfg).strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def get_recommendation(backend_cfg, flights, origin, destination, cabin, rec_prompt):
    summary = json.dumps([
        {"airline": f["airline"], "price": f["price"],
         "duration": f["duration"], "stops": f["stops"]}
        for f in flights[:6]
    ])
    prompt = f"Flights from {origin} to {destination} in {cabin}: {summary}. {rec_prompt}"
    return call_ai(prompt,
                   "You are a friendly travel advisor. Be concise, max 2-3 sentences.",
                   backend_cfg, max_tokens=250)


# ── Static data ────────────────────────────────────────────────────────────────
POPULAR = {
    "— type your own —":       ("", ""),
    "Hyderabad → Dubai":       ("HYD", "DXB"),
    "Mumbai → London":         ("BOM", "LHR"),
    "Delhi → Singapore":       ("DEL", "SIN"),
    "Bangalore → New York":    ("BLR", "JFK"),
    "Chennai → Kuala Lumpur":  ("MAA", "KUL"),
    "Hyderabad → London":      ("HYD", "LHR"),
    "Delhi → Dubai":           ("DEL", "DXB"),
    "Mumbai → New York":       ("BOM", "JFK"),
    "New York → London":       ("JFK", "LHR"),
    "Los Angeles → Tokyo":     ("LAX", "NRT"),
}
CURRENCY_MAP = {
    "USD 🇺🇸": "USD", "INR 🇮🇳": "INR", "EUR 🇪🇺": "EUR",
    "GBP 🇬🇧": "GBP", "AED 🇦🇪": "AED", "SGD 🇸🇬": "SGD",
}
IATA_HINT = {
    "HYD":"Hyderabad","DEL":"Delhi","BOM":"Mumbai","BLR":"Bangalore",
    "MAA":"Chennai","CCU":"Kolkata","GOI":"Goa","AMD":"Ahmedabad",
    "DXB":"Dubai","LHR":"London","JFK":"New York","SIN":"Singapore",
    "NRT":"Tokyo","CDG":"Paris","FRA":"Frankfurt","AMS":"Amsterdam",
    "DFW":"Dallas","LAX":"Los Angeles","KUL":"Kuala Lumpur",
    "SYD":"Sydney","AUH":"Abu Dhabi","DOH":"Doha","IST":"Istanbul",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter','Noto Sans Devanagari','Noto Sans Telugu',sans-serif; }
  .stApp { background: #0b1120; color: #e2e8f0; }
  .hero {
    background: linear-gradient(135deg,#0f2144 0%,#1a3a6e 50%,#0f2144 100%);
    border-radius:20px; padding:2.5rem 2rem 2rem;
    margin-bottom:2rem; border:1px solid #1e3a6e;
    position:relative; overflow:hidden;
  }
  .hero::before {
    content:'✈'; position:absolute; right:2rem; top:1.5rem;
    font-size:6rem; opacity:0.07; transform:rotate(-30deg);
  }
  .hero h1 { font-size:2.8rem; font-weight:700; margin:0; color:#fff; letter-spacing:-1px; }
  .hero p  { color:#94a3b8; font-size:1.1rem; margin:0.5rem 0 0; }
  .backend-pill {
    display:inline-block; padding:3px 12px; border-radius:20px;
    font-size:0.78rem; font-weight:600; margin-top:6px;
  }
  .pill-groq   { background:#1e3a6e; color:#93c5fd; }
  .pill-ollama { background:#14532d; color:#86efac; }
  .search-card { background:#111827; border:1px solid #1f2d45; border-radius:16px; padding:1.8rem; margin-bottom:1.5rem; }
  .flight-card { background:#111827; border:1px solid #1f2d45; border-radius:14px; padding:1.4rem 1.6rem; margin-bottom:1rem; }
  .flight-card:hover { border-color:#3b82f6; }
  .airline-name { font-weight:600; font-size:1rem; color:#e2e8f0; }
  .time-big     { font-size:1.8rem; font-weight:700; color:#ffffff; }
  .city-code    { font-size:0.78rem; color:#64748b; margin-top:2px; }
  .duration-pill { background:#1e3a6e; color:#93c5fd; border-radius:20px; padding:4px 14px; font-size:0.8rem; font-weight:500; display:inline-block; }
  .stops-badge { font-size:0.75rem; padding:3px 10px; border-radius:20px; font-weight:500; }
  .nonstop { background:#14532d; color:#86efac; }
  .oneplus  { background:#431407; color:#fdba74; }
  .price-main  { font-size:2rem; font-weight:700; color:#60a5fa; }
  .price-label { font-size:0.75rem; color:#475569; }
  .cabin-tag { background:#1e293b; color:#94a3b8; border-radius:6px; padding:2px 8px; font-size:0.72rem; display:inline-block; }
  .tag-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:6px; align-items:center; }
  .info-tag { background:#1e293b; border:1px solid #334155; color:#94a3b8; border-radius:6px; padding:2px 10px; font-size:0.75rem; }
  .dot-line { flex:1; border-top:1px dashed #334155; }
  .stat-pill { background:#1e293b; border:1px solid #334155; border-radius:10px; padding:0.8rem 1.2rem; text-align:center; }
  .stat-value { font-size:1.4rem; font-weight:700; color:#60a5fa; }
  .stat-desc  { font-size:0.75rem; color:#64748b; margin-top:2px; }
  .ai-badge { background:#312e81; color:#a5b4fc; border-radius:8px; padding:3px 10px; font-size:0.75rem; font-weight:500; display:inline-block; margin-bottom:8px; }
  .stSelectbox>div>div   { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  .stDateInput>div>div>input { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  .stNumberInput>div>div>input { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; }
  .stTextInput>div>div>input  { background:#1e293b!important; border-color:#334155!important; color:#e2e8f0!important; border-radius:10px!important; }
  label { color:#94a3b8!important; font-size:0.85rem!important; font-weight:500!important; }
  .stButton>button { background:linear-gradient(135deg,#2563eb,#1d4ed8)!important; color:white!important; border:none!important; border-radius:12px!important; padding:0.7rem 2rem!important; font-weight:600!important; font-size:1rem!important; width:100%!important; }
  .stButton>button:hover { opacity:0.9!important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Language
    lang = st.radio(
        "🌐 Language / भाषा / భాష",
        options=["English", "हिंदी", "తెలుగు"],
        horizontal=True, key="lang_select",
    )

T = TRANSLATIONS[lang]

with st.sidebar:
    st.divider()

    # ── AI Backend selector ────────────────────────────────────────────────
    st.markdown(T["ai_backend_header"])
    backend_choice = st.radio(
        "Backend",
        options=[T["backend_groq"], T["backend_ollama"]],
        label_visibility="collapsed",
    )
    is_groq = backend_choice == T["backend_groq"]

    st.divider()

    if is_groq:
        # BYOK — Groq
        st.markdown(T["groq_key_header"])
        st.caption(T["groq_key_caption"])
        groq_key = st.text_input(
            "Groq Key", type="password",
            placeholder=T["groq_key_placeholder"],
            label_visibility="collapsed",
        )
        groq_model = st.selectbox(T["groq_model_label"], GROQ_MODELS)
        backend_cfg = {
            "backend": "groq",
            "groq_key": groq_key,
            "groq_model": groq_model,
        }
    else:
        # Local Ollama
        st.markdown(T["ollama_url_label"])
        st.caption(T["ollama_url_caption"])
        ollama_url = st.text_input(
            "Ollama URL", value="http://localhost:11434",
            label_visibility="collapsed",
        )
        ollama_model = st.text_input(
            T["ollama_model_label"],
            placeholder=T["ollama_model_placeholder"],
        )
        st.info(T["ollama_tip"])
        backend_cfg = {
            "backend": "ollama",
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
        }

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
pill_cls  = "pill-groq" if is_groq else "pill-ollama"
pill_text = (T["backend_groq"] if is_groq else T["backend_ollama"])

st.markdown(f"""
<div class="hero">
  <h1>{T['hero_title']}</h1>
  <p>{T['hero_sub']}</p>
  <span class="backend-pill {pill_cls}">{pill_text}</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEARCH FORM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="search-card">', unsafe_allow_html=True)
r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
with r1c1:
    quick = st.selectbox(T["quick_route"], list(POPULAR.keys()))
with r1c2:
    currency_label = st.selectbox(T["currency_label"], list(CURRENCY_MAP.keys()))
    currency = CURRENCY_MAP[currency_label]
with r1c3:
    cabin_display = st.selectbox(T["cabin_label"], T["cabin_options"])
    cabin = T.get("cabin_api_map", {}).get(cabin_display, cabin_display)

default_o, default_d = POPULAR[quick]
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.1, 0.7])
with c1:
    origin = st.text_input(T["from_label"], value=default_o, placeholder=T["from_placeholder"]).strip().upper()
with c2:
    destination = st.text_input(T["to_label"], value=default_d, placeholder=T["to_placeholder"]).strip().upper()
with c3:
    depart_date = st.date_input(T["date_label"], value=date.today() + timedelta(days=7), min_value=date.today())
with c4:
    adults = st.number_input(T["passengers_label"], min_value=1, max_value=9, value=1)

if origin and destination:
    ho = IATA_HINT.get(origin, "?")
    hd = IATA_HINT.get(destination, "?")
    st.caption(f"📍 {origin} = {ho}   →   {destination} = {hd}")

search_clicked = st.button(T["search_btn"])
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
if search_clicked:
    if is_groq and not groq_key:
        st.error(T["err_no_key"]); st.stop()
    if not is_groq and not ollama_model.strip():
        st.error(T["err_no_model"]); st.stop()
    if not origin or not destination:
        st.error(T["err_no_iata"]); st.stop()
    if len(origin) != 3 or len(destination) != 3:
        st.error(T["err_iata_len"]); st.stop()
    if origin == destination:
        st.error(T["err_same"]); st.stop()

    # ── Fetch flights ──────────────────────────────────────────────────────
    with st.spinner(T["spinner_flights"]):
        try:
            flights = generate_flights(
                backend_cfg, origin, destination,
                depart_date.strftime("%Y-%m-%d"), adults, cabin, currency
            )
        except Exception as e:
            if "ollama_unreachable" in str(e):
                st.error(T["err_ollama"])
            else:
                st.error(f"❌ {e}")
            st.stop()

    # ── Stats bar ──────────────────────────────────────────────────────────
    prices = [f["price"] for f in flights if isinstance(f.get("price"), (int, float))]
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-pill"><div class="stat-value">{len(flights)}</div><div class="stat-desc">{T["stat_found"]}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {min(prices):,}</div><div class="stat-desc">{T["stat_cheapest"]}</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {max(prices):,}</div><div class="stat-desc">{T["stat_expensive"]}</div></div>', unsafe_allow_html=True)
    with s4:
        avg = int(sum(prices) / len(prices))
        st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {avg:,}</div><div class="stat-desc">{T["stat_avg"]}</div></div>', unsafe_allow_html=True)

    # ── AI Recommendation ──────────────────────────────────────────────────
    with st.spinner(T["spinner_rec"]):
        try:
            rec = get_recommendation(backend_cfg, flights, origin, destination, cabin, T["rec_prompt"])
            if rec:
                st.markdown(
                    '<div style="background:#1e1b4b;border:1px solid #3730a3;border-radius:12px;padding:1.2rem 1.5rem;margin:1rem 0;">'
                    f'<span class="ai-badge">{T["ai_badge"]}</span><br>'
                    '<span style="color:#c7d2fe;font-size:0.95rem;line-height:1.6;">' + rec + '</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            pass

    # ── Sort ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    sort_opts = [T["sort_price"], T["sort_duration"], T["sort_depart"]]
    sort_by = st.selectbox(T["sort_label"], sort_opts)
    if sort_by == T["sort_price"]:
        flights.sort(key=lambda x: x.get("price", 9999))
    elif sort_by == T["sort_duration"]:
        def dur_mins(d):
            h = int(re.search(r"(\d+)h", d).group(1)) if re.search(r"(\d+)h", d) else 0
            m = int(re.search(r"(\d+)m", d).group(1)) if re.search(r"(\d+)m", d) else 0
            return h * 60 + m
        flights.sort(key=lambda x: dur_mins(x.get("duration", "99h 99m")))
    else:
        flights.sort(key=lambda x: x.get("departure_time", "00:00"))

    st.markdown(f"### {T['flights_heading']} &middot; {origin} &#x2192; {destination} &middot; {depart_date.strftime('%d %b %Y')}")

    # ── Flight cards ───────────────────────────────────────────────────────
    for f in flights:
        stops     = int(f.get("stops", 0))
        stops_txt = T["nonstop"] if stops == 0 else f"{stops} {T['stop'] if stops==1 else T['stops']}"
        stops_cls = "nonstop" if stops == 0 else "oneplus"
        via       = f.get("via", "")
        via_part  = f' <span class="info-tag">{T["via_label"]} {via}</span>' if via else ""
        offset    = int(f.get("arrival_date_offset", 0))
        next_day  = f' <span style="color:#f87171;font-size:0.7rem;">{T["next_day"]}</span>' if offset else ""
        refundable = f.get("refundable", False)
        ref_color  = "#4ade80" if refundable else "#f87171"
        ref_label  = T["refundable"] if refundable else T["non_refundable"]
        route_mid  = T["nonstop"] if stops == 0 else (f'1 {T["stop"]} {T["via_label"]} {via}' if via else f'1 {T["stop"]}')
        price      = int(f.get("price", 0))
        total      = price * int(adults)

        html = (
            '<div class="flight-card">'
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            '<div>'
            '<div class="airline-name">&#x2708; ' + str(f.get("airline","")) + '&nbsp;&nbsp;'
            '<span style="font-weight:400;color:#475569;font-size:0.82rem;">' + str(f.get("flight_number","")) + '</span>'
            '</div>'
            '<div class="tag-row">'
            '<span class="stops-badge ' + stops_cls + '">' + stops_txt + '</span>'
            '<span class="cabin-tag">' + cabin_display + '</span>'
            + via_part +
            '<span class="info-tag" style="color:' + ref_color + ';">' + ref_label + '</span>'
            '</div>'
            '</div>'
            '<div style="text-align:right;">'
            '<div class="price-main">' + currency + ' ' + f'{price:,}' + '</div>'
            '<div class="price-label">' + T["per_person"] + ' &middot; ' + str(adults) + ' ' + T["pax"] + ' = ' + currency + ' ' + f'{total:,}' + '</div>'
            '</div>'
            '</div>'
            '<div style="display:flex;align-items:center;gap:1.5rem;margin-top:1rem;">'
            '<div>'
            '<div class="time-big">' + str(f.get("departure_time","--:--")) + '</div>'
            '<div class="city-code">' + origin + '</div>'
            '</div>'
            '<div style="flex:1;text-align:center;">'
            '<div class="duration-pill">&#x23F1; ' + str(f.get("duration","")) + '</div>'
            '<div style="display:flex;align-items:center;gap:6px;color:#475569;font-size:0.78rem;margin-top:6px;">'
            '<div class="dot-line"></div><span>' + route_mid + '</span><div class="dot-line"></div>'
            '</div>'
            '</div>'
            '<div style="text-align:right;">'
            '<div class="time-big">' + str(f.get("arrival_time","--:--")) + next_day + '</div>'
            '<div class="city-code">' + destination + '</div>'
            '</div>'
            '</div>'
            '<hr style="border:none;border-top:1px solid #1f2d45;margin:0.8rem 0;">'
            '<div style="display:flex;gap:1.5rem;font-size:0.78rem;color:#64748b;">'
            '<span>&#x2708; ' + str(f.get("aircraft","")) + '</span>'
            '<span>&#x1F9F3; ' + str(f.get("baggage","")) + '</span>'
            '<span>&#x1F37D; ' + str(f.get("meal","")) + '</span>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    powered_key = "powered_groq" if is_groq else "powered_ollama"
    st.caption(T[powered_key])

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f'<div style="text-align:center;color:#334155;font-size:0.8rem;padding:1rem 0;">{T["footer"]}</div>', unsafe_allow_html=True)
