import streamlit as st
import requests
import json
import re
from datetime import date, timedelta, datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkySearch – Find Flights",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background: #0b1120; color: #e2e8f0; }
  .hero {
    background: linear-gradient(135deg, #0f2144 0%, #1a3a6e 50%, #0f2144 100%);
    border-radius: 20px; padding: 2.5rem 2rem 2rem;
    margin-bottom: 2rem; border: 1px solid #1e3a6e;
    position: relative; overflow: hidden;
  }
  .hero::before {
    content: '✈'; position: absolute; right: 2rem; top: 1.5rem;
    font-size: 6rem; opacity: 0.07; transform: rotate(-30deg);
  }
  .hero h1 { font-size: 2.8rem; font-weight: 700; margin: 0; color: #fff; letter-spacing: -1px; }
  .hero p  { color: #94a3b8; font-size: 1.1rem; margin: 0.5rem 0 0; }
  .search-card { background: #111827; border: 1px solid #1f2d45; border-radius: 16px; padding: 1.8rem; margin-bottom: 1.5rem; }
  .flight-card { background: #111827; border: 1px solid #1f2d45; border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }
  .flight-card:hover { border-color: #3b82f6; }
  .airline-name { font-weight: 600; font-size: 1rem; color: #e2e8f0; }
  .time-big     { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
  .city-code    { font-size: 0.78rem; color: #64748b; margin-top: 2px; }
  .duration-pill { background: #1e3a6e; color: #93c5fd; border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; font-weight: 500; display: inline-block; }
  .stops-badge { font-size: 0.75rem; padding: 3px 10px; border-radius: 20px; font-weight: 500; }
  .nonstop { background: #14532d; color: #86efac; }
  .oneplus  { background: #431407; color: #fdba74; }
  .price-main  { font-size: 2rem; font-weight: 700; color: #60a5fa; }
  .price-label { font-size: 0.75rem; color: #475569; }
  .cabin-tag { background: #1e293b; color: #94a3b8; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; display: inline-block; }
  .tag-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px; align-items: center; }
  .info-tag { background: #1e293b; border: 1px solid #334155; color: #94a3b8; border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; }
  .dot-line { flex: 1; border-top: 1px dashed #334155; }
  .stat-pill { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 0.8rem 1.2rem; text-align: center; }
  .stat-value { font-size: 1.4rem; font-weight: 700; color: #60a5fa; }
  .stat-desc  { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
  .ai-badge { background: #312e81; color: #a5b4fc; border-radius: 8px; padding: 3px 10px; font-size: 0.75rem; font-weight: 500; display: inline-block; margin-bottom: 8px; }
  .stSelectbox > div > div   { background: #1e293b !important; border-color: #334155 !important; color: #e2e8f0 !important; border-radius: 10px !important; }
  .stDateInput > div > div > input { background: #1e293b !important; border-color: #334155 !important; color: #e2e8f0 !important; border-radius: 10px !important; }
  .stNumberInput > div > div > input { background: #1e293b !important; border-color: #334155 !important; color: #e2e8f0 !important; }
  .stTextInput > div > div > input   { background: #1e293b !important; border-color: #334155 !important; color: #e2e8f0 !important; border-radius: 10px !important; }
  label { color: #94a3b8 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
  .stButton > button { background: linear-gradient(135deg, #2563eb, #1d4ed8) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 0.7rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important; width: 100% !important; }
  .stButton > button:hover { opacity: 0.9 !important; }
</style>
""", unsafe_allow_html=True)


# ── Groq API ───────────────────────────────────────────────────────────────────
def call_groq(api_key, prompt, model="llama-3.3-70b-versatile"):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a flight data engine. Always respond with valid JSON only. No explanation, no markdown fences, no extra text — pure JSON array."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 3000,
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=30)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    raise Exception(f"Groq API error {r.status_code}: {r.text[:300]}")


def generate_flights(api_key, origin, destination, depart_date, adults, cabin, currency):
    prompt = f"""
Generate exactly 10 realistic flight options from {origin} to {destination}
on {depart_date} for {adults} adult(s) in {cabin} class. Currency: {currency}.

Use real airlines that actually fly this route. Include a mix of nonstop and 1-stop flights.
Make prices, durations, and times realistic for this route.

Return a JSON array of 10 objects, each with exactly these fields:
- airline: string (full airline name)
- airline_code: string (2-letter IATA)
- flight_number: string (e.g. EK512)
- departure_time: string HH:MM
- arrival_time: string HH:MM
- arrival_date_offset: integer 0 or 1
- duration: string (e.g. "2h 30m")
- stops: integer 0 or 1
- via: string (layover airport code, empty string if nonstop)
- price: integer
- aircraft: string
- baggage: string (e.g. "23kg included")
- meal: string (e.g. "Meal included")
- refundable: boolean

Return ONLY the JSON array, nothing else.
"""
    raw = call_groq(api_key, prompt).strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def get_recommendation(api_key, flights, origin, destination, cabin):
    summary = json.dumps([
        {"airline": f["airline"], "price": f["price"], "duration": f["duration"], "stops": f["stops"]}
        for f in flights[:6]
    ])
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a friendly travel advisor. Be concise, max 2-3 sentences."},
            {"role": "user", "content": f"Flights from {origin} to {destination} in {cabin}: {summary}. Which is best value and which is best for comfort? Be brief."},
        ],
        "temperature": 0.6,
        "max_tokens": 150,
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=20)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return ""


# ── Data ───────────────────────────────────────────────────────────────────────
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


# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>&#x2708; SkySearch</h1>
  <p>AI-powered flight explorer &mdash; search routes across 400+ airlines. Powered by Groq &amp; Llama 3.3.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔑 Groq API Key")
    st.caption("Get a free key at [console.groq.com](https://console.groq.com)")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.divider()
    st.markdown("**Model:** Llama 3.3 70B Versatile")
    st.caption("Free tier · No credit card needed")

st.markdown('<div class="search-card">', unsafe_allow_html=True)
r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
with r1c1:
    quick = st.selectbox("✈ Quick route picker", list(POPULAR.keys()))
with r1c2:
    currency_label = st.selectbox("Currency", list(CURRENCY_MAP.keys()))
    currency = CURRENCY_MAP[currency_label]
with r1c3:
    cabin = st.selectbox("Cabin class", ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"])

default_o, default_d = POPULAR[quick]
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.1, 0.7])
with c1:
    origin = st.text_input("From (IATA)", value=default_o, placeholder="e.g. HYD").strip().upper()
with c2:
    destination = st.text_input("To (IATA)", value=default_d, placeholder="e.g. DXB").strip().upper()
with c3:
    depart_date = st.date_input("Departure date", value=date.today() + timedelta(days=7), min_value=date.today())
with c4:
    adults = st.number_input("Passengers", min_value=1, max_value=9, value=1)

if origin and destination:
    ho = IATA_HINT.get(origin, "Unknown")
    hd = IATA_HINT.get(destination, "Unknown")
    st.caption(f"📍 {origin} = {ho}   →   {destination} = {hd}")

search_clicked = st.button("🔍  Search Flights with AI")
st.markdown('</div>', unsafe_allow_html=True)


# ── Results ────────────────────────────────────────────────────────────────────
if search_clicked:
    if not api_key:
        st.error("⚠️ Please enter your Groq API Key in the sidebar.")
    elif not origin or not destination:
        st.error("⚠️ Please enter both origin and destination IATA codes.")
    elif len(origin) != 3 or len(destination) != 3:
        st.error("⚠️ IATA codes are exactly 3 letters (e.g. HYD, DXB, LHR).")
    elif origin == destination:
        st.error("⚠️ Origin and destination cannot be the same.")
    else:
        with st.spinner("✈ Groq AI is finding flights..."):
            try:
                flights = generate_flights(api_key, origin, destination,
                                           depart_date.strftime("%Y-%m-%d"),
                                           adults, cabin, currency)
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

        prices = [f["price"] for f in flights if isinstance(f.get("price"), (int, float))]
        st.markdown("---")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{len(flights)}</div><div class="stat-desc">Flights found</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {min(prices):,}</div><div class="stat-desc">Cheapest fare</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {max(prices):,}</div><div class="stat-desc">Most expensive</div></div>', unsafe_allow_html=True)
        with s4:
            avg = int(sum(prices) / len(prices))
            st.markdown(f'<div class="stat-pill"><div class="stat-value">{currency} {avg:,}</div><div class="stat-desc">Average price</div></div>', unsafe_allow_html=True)

        with st.spinner("🤖 Getting AI recommendation..."):
            try:
                rec = get_recommendation(api_key, flights, origin, destination, cabin)
                if rec:
                    st.markdown(
                        '<div style="background:#1e1b4b;border:1px solid #3730a3;border-radius:12px;padding:1.2rem 1.5rem;margin:1rem 0;">'
                        '<span class="ai-badge">&#x1F916; Groq AI Recommendation</span><br>'
                        '<span style="color:#c7d2fe;font-size:0.95rem;line-height:1.6;">' + rec + '</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            except:
                pass

        st.markdown("<br>", unsafe_allow_html=True)
        sort_by = st.selectbox("Sort by", ["💰 Price (low → high)", "⏱ Duration (shortest first)", "🛫 Departure time"])
        if "Price" in sort_by:
            flights.sort(key=lambda x: x.get("price", 9999))
        elif "Duration" in sort_by:
            def dur_mins(d):
                h = int(re.search(r"(\d+)h", d).group(1)) if re.search(r"(\d+)h", d) else 0
                m = int(re.search(r"(\d+)m", d).group(1)) if re.search(r"(\d+)m", d) else 0
                return h * 60 + m
            flights.sort(key=lambda x: dur_mins(x.get("duration", "99h 99m")))
        else:
            flights.sort(key=lambda x: x.get("departure_time", "00:00"))

        st.markdown(f"### Flights &middot; {origin} &#x2192; {destination} &middot; {depart_date.strftime('%d %b %Y')}")

        for f in flights:
            stops      = int(f.get("stops", 0))
            stops_txt  = "Nonstop" if stops == 0 else (str(stops) + (" stop" if stops == 1 else " stops"))
            stops_cls  = "nonstop" if stops == 0 else "oneplus"
            via        = f.get("via", "")
            via_part   = (' <span class="info-tag">via ' + via + '</span>') if via else ""
            offset     = int(f.get("arrival_date_offset", 0))
            next_day   = ' <span style="color:#f87171;font-size:0.7rem;">+1 day</span>' if offset else ""
            refundable = f.get("refundable", False)
            ref_color  = "#4ade80" if refundable else "#f87171"
            ref_label  = "Refundable" if refundable else "Non-refundable"
            route_mid  = "Nonstop" if stops == 0 else ("1 stop via " + via if via else "1 stop")
            cabin_disp = cabin.replace("_", " ").title()
            price      = int(f.get("price", 0))
            total      = price * int(adults)

            html = (
                '<div class="flight-card">'

                # Top row: airline + price
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                '<div>'
                '<div class="airline-name">&#x2708; ' + str(f.get("airline","")) + '&nbsp;&nbsp;'
                '<span style="font-weight:400;color:#475569;font-size:0.82rem;">' + str(f.get("flight_number","")) + '</span>'
                '</div>'
                '<div class="tag-row">'
                '<span class="stops-badge ' + stops_cls + '">' + stops_txt + '</span>'
                '<span class="cabin-tag">' + cabin_disp + '</span>'
                + via_part +
                '<span class="info-tag" style="color:' + ref_color + ';">' + ref_label + '</span>'
                '</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div class="price-main">' + currency + ' ' + f'{price:,}' + '</div>'
                '<div class="price-label">per person &middot; ' + str(adults) + ' pax = ' + currency + ' ' + f'{total:,}' + '</div>'
                '</div>'
                '</div>'

                # Time row
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

                # Footer row
                '<hr style="border:none;border-top:1px solid #1f2d45;margin:0.8rem 0;">'
                '<div style="display:flex;gap:1.5rem;font-size:0.78rem;color:#64748b;">'
                '<span>&#x2708; ' + str(f.get("aircraft","")) + '</span>'
                '<span>&#x1F9F3; ' + str(f.get("baggage","")) + '</span>'
                '<span>&#x1F37D; ' + str(f.get("meal","")) + '</span>'
                '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

        st.caption("⚡ Powered by Groq (Llama 3.3 70B) · Results are AI-generated for informational purposes")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#334155;font-size:0.8rem;padding:1rem 0;">SkySearch &middot; Built with Streamlit + Groq AI &middot; Hackathon 2026</div>', unsafe_allow_html=True)
