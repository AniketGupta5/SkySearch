# SkySearch — Skills

Skills are discrete capabilities the system has. Each maps to one or more functions in `app.py`.

---

## SK-001 · JSON Flight Generation

**What it does:** Sends a structured prompt to Groq and parses the response into a Python list of flight dicts.

**Functions:** `call_groq()`, `build_flight_prompt()`, `parse_flights()`

**Input:**
- `api_key` (str)
- `origin`, `destination` (IATA codes)
- `travel_date` (date string)
- `passengers` (int)
- `cabin_class` (str)
- `num_results` (int, default 8)

**Output:** `list[dict]` — validated flight objects

**Error Handling:**
- JSON parse failure → returns `[]`, shows `st.warning()`
- API error → raises exception, caught at call site → `st.error()`

---

## SK-002 · Multi-Currency Price Display

**What it does:** Converts `price_usd` to the user's selected currency using hardcoded rates and formats it with the appropriate symbol.

**Functions:** `convert_price()`, `format_price()`

**Supported Currencies:** USD ($), INR (₹), EUR (€), GBP (£), AED (د.إ), SGD (S$)

**Notes:** Rates are static approximations. Suitable for display only.

---

## SK-003 · Flight Card Rendering

**What it does:** Takes a flight dict and renders it as a styled HTML card using Streamlit's `st.markdown(unsafe_allow_html=True)`.

**Functions:** `render_flight_card(f, currency)`

**Card Contains:**
- Airline name + flight number
- Departure / arrival times with city codes
- Duration pill + stops badge (Nonstop / 1 Stop)
- Price in selected currency
- Tags: baggage, aircraft, meal, refundable status

---

## SK-004 · Stats Bar

**What it does:** Computes and displays cheapest, average, and most expensive fares from the current results list.

**Functions:** `render_stats_bar(flights, currency)`

**Computed Values:**
- `min(price_usd)` → cheapest
- `mean(price_usd)` → average (rounded)
- `max(price_usd)` → most expensive

---

## SK-005 · Sort & Reorder

**What it does:** Sorts the flights list in-place based on user's sort preference.

**Sort Keys:**

| Sort Option | Sort Key | Order |
|---|---|---|
| Price | `price_usd` | Ascending |
| Duration | parsed minutes from `duration` string | Ascending |
| Departure | `departure` (HH:MM string) | Ascending |

---

## SK-006 · AI Travel Tip

**What it does:** Generates a 2–3 sentence destination tip via Groq and displays it in a styled card.

**Functions:** `build_ai_tip_prompt()`, `call_groq()`

**Trigger:** Runs once per search, after flight results are displayed.

---

## SK-007 · API Key Management

**What it does:** Accepts the Groq API key via a sidebar password input and stores it in `st.session_state`. Validates that the key is non-empty before allowing search.

**Functions:** Inline in main Streamlit flow

**Security:** `type="password"` hides the key in the UI. Key is never logged or stored outside session.
