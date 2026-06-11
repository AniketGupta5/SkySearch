# SkySearch — Task List

## Status Legend
- [x] Done
- [ ] Todo
- [~] In Progress

---

## Phase 1 · Core MVP
- [x] T-001 · Set up Streamlit project (`app.py`, `requirements.txt`)
- [x] T-002 · Implement `call_groq()` with Groq REST API
- [x] T-003 · Build flight search form (IATA inputs, date, passengers, cabin, currency)
- [x] T-004 · Implement `build_flight_prompt()` for structured JSON output
- [x] T-005 · Implement `parse_flights()` with JSON fence stripping + validation
- [x] T-006 · Render flight cards with custom CSS (airline, times, price, badges)
- [x] T-007 · Add stats bar (cheapest / average / most expensive)
- [x] T-008 · Add sort controls (price / duration / departure)
- [x] T-009 · Add AI travel tip section
- [x] T-010 · Dark sky theme (CSS variables, hero section, Inter font)
- [x] T-011 · Sidebar API key input (password type)
- [x] T-012 · Write README with run instructions + Groq key setup

---

## Phase 2 · Enhancements (Backlog)
- [ ] T-013 · Add round-trip / multi-city toggle
- [ ] T-014 · Add airline logo placeholders (emoji or initials avatar)
- [ ] T-015 · Add filter sidebar (max price, stops: nonstop only)
- [ ] T-016 · Export results as CSV download button
- [ ] T-017 · Add skeleton loading animation while Groq is processing
- [ ] T-018 · Add IATA code autocomplete (static list of major airports)
- [ ] T-019 · Deploy to Streamlit Community Cloud + add live URL to README

---

## Phase 3 · Polish / Nice-to-Have
- [ ] T-020 · Add fare trend chart (mock data, Altair/Plotly)
- [ ] T-021 · Mobile-responsive layout tweaks
- [ ] T-022 · Add "copy shareable link" with route encoded in query params
