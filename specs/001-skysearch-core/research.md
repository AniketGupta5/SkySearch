# SkySearch — Research & References

## Why Groq over OpenAI?
- Groq offers **free tier** with generous limits — ideal for hackathon demos
- `llama-3.3-70b-versatile` is fast (low-latency inference on Groq hardware)
- OpenAI-compatible API format → easy swap if needed

## Prompt Engineering Findings
- Model must be explicitly told "return only JSON array, no markdown fences, no preamble" — otherwise it wraps output in ```json blocks
- Temperature 0.7 gives realistic variety without hallucinating impossible routes
- 3000 max_tokens is sufficient for 8–10 flight objects

## Streamlit Notes
- `st.session_state` is the only state persistence (resets on page refresh)
- Custom CSS via `st.markdown(..., unsafe_allow_html=True)` — works well for theming
- `st.columns()` used for card layout; Streamlit doesn't support CSS Grid natively

## Alternatives Considered

| Option | Decision | Reason |
|---|---|---|
| OpenAI GPT-4o | Not used | Paid, overkill for hackathon |
| AviationStack / Skyscanner API | Not used | Requires paid plan or approval |
| FastAPI + React | Not used | Too complex for solo hackathon |
| Gradio | Not used | Less flexible UI customisation |

## Deployment Options
1. **Streamlit Community Cloud** (free) — recommended for sharing
2. **Hugging Face Spaces** — supports Streamlit apps
3. **Railway / Render** — works with `streamlit run app.py` as start command
4. **Local only** — `pip install -r requirements.txt && streamlit run app.py`
