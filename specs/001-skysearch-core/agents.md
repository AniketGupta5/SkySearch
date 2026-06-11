# SkySearch — AI Agents

This file documents the AI agent(s) used in SkySearch — their roles, prompts, and behaviour contracts.

---

## Agent 1 · Flight Data Engine

**Role:** Generate realistic flight search results as structured JSON.

**Model:** `llama-3.3-70b-versatile` (via Groq)

**System Prompt:**
```
You are a flight data engine. Always respond with valid JSON only.
No explanation, no markdown fences, no extra text — pure JSON array.
```

**User Prompt Template:**
```
Generate {n} realistic flights from {origin} to {destination} on {date}.
Cabin class: {cabin_class}. 
Return a JSON array where each object has:
airline, flight_number, departure (HH:MM), arrival (HH:MM), duration,
stops (int), price_usd (int), baggage, aircraft, meal, refundable (bool).
Make prices and airlines realistic for this route.
```

**Output Contract:**
- Must return a valid JSON array
- Array length: 6–10 items
- All fields required per flight object (see `data-model.md`)
- `price_usd` should reflect cabin class (Business ~2–3x Economy, First ~4–5x)

**Failure Modes:**
- Returns markdown-fenced JSON → stripped by `parse_flights()` via regex
- Returns empty array → UI shows "no results" message
- Returns non-JSON → `st.warning()` with raw output for debugging

---

## Agent 2 · Travel Advisor

**Role:** Generate a short, helpful travel tip for the searched route.

**Model:** `llama-3.3-70b-versatile` (via Groq)

**System Prompt:** *(same as Agent 1 — reuses `call_groq()`)*

**User Prompt Template:**
```
Give a 2-3 sentence travel tip for someone flying from {origin} to {destination}.
Include something useful about the destination or the journey.
Plain text only, no bullet points.
```

**Output Contract:**
- 2–3 sentences of plain text
- No lists, no headers, no markdown
- Friendly, informative tone

---

## Future Agents (Backlog)

| Agent | Purpose | Status |
|---|---|---|
| Price Predictor | Predict if fare will rise/fall in next 7 days | Backlog |
| Itinerary Planner | Generate day-by-day trip plan for destination | Backlog |
| Baggage Advisor | Advise on baggage rules for specific airlines | Backlog |
