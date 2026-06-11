# SkySearch — Technical Blueprint

## Architecture

```
User Browser
    │
    ▼
Streamlit (app.py)
    ├── UI Layer        → st.markdown (custom CSS), st.columns, st.selectbox, etc.
    ├── State Layer     → st.session_state (flights list, ai_tip, sort order)
    └── API Layer       → call_groq() → requests.post → Groq /openai/v1/chat/completions
                              │
                              ▼
                         Groq Cloud (llama-3.3-70b-versatile)
                         Returns: JSON array of flight objects
```

## Key Functions

| Function | Purpose |
|---|---|
| `call_groq(api_key, prompt, model)` | Raw Groq API call → returns content string |
| `parse_flights(raw)` | Strips markdown fences, parses JSON, validates list |
| `build_flight_prompt(...)` | Constructs the structured prompt for flight generation |
| `build_ai_tip_prompt(...)` | Constructs prompt for travel recommendation |
| `render_flight_card(f, currency)` | Renders a single flight as styled HTML |
| `render_stats_bar(flights, currency)` | Renders cheapest/avg/expensive pills |

## Data Model — Flight Object (LLM Output)

```json
{
  "airline": "IndiGo",
  "flight_number": "6E-204",
  "departure": "06:30",
  "arrival": "08:15",
  "duration": "1h 45m",
  "stops": 0,
  "price_usd": 87,
  "baggage": "15kg checked",
  "aircraft": "Airbus A320",
  "meal": "Paid meal",
  "refundable": false
}
```

## Tech Stack Details

| Layer | Technology | Version |
|---|---|---|
| UI Framework | Streamlit | ≥1.32 |
| LLM Provider | Groq API | REST (openai-compat) |
| LLM Model | llama-3.3-70b-versatile | — |
| HTTP Client | requests | ≥2.31 |
| Language | Python | ≥3.10 |
| Font | Inter (Google Fonts CDN) | — |

## Environment

- **API Key**: Runtime sidebar input (`st.text_input`, type=password)
- **No `.env` file needed**
- **No database**
- **Deployment**: `streamlit run app.py` locally or Streamlit Community Cloud

## Prompt Engineering Strategy

Flight prompt instructs the model to:
1. Return **only** a JSON array (no markdown, no preamble)
2. Generate `n` realistic flights for the given route + date
3. Vary airlines, times, prices realistically for the origin/destination region
4. Respect cabin class (Economy / Business / First) in pricing

AI tip prompt instructs the model to return 2–3 sentences of travel advice for the route.

## Error Handling

| Scenario | Handling |
|---|---|
| Groq API error (4xx/5xx) | `st.error()` with status code |
| JSON parse failure | `st.warning()` + raw response shown for debug |
| Empty API key | Button disabled / early return with `st.warning()` |
| Timeout (>30s) | requests timeout exception caught → `st.error()` |
