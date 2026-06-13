# ✈ SkySearch — AI Flight Finder

An AI-powered Skyscanner-style flight explorer built with **Streamlit** and **Groq (Llama 3.3)**.
Search flights between any two airports — realistic results, no booking, no payment needed.

## 🚀 Live Demo
Deployed on Streamlit Cloud.

## ✨ Features
- 🤖 AI-generated realistic flight data via Groq (Llama 3.3 70B)
- 🌍 Search any route using IATA airport codes
- 💰 Multi-currency support (USD, INR, EUR, GBP, AED, SGD)
- 🛫 Economy / Premium Economy / Business / First class
- ⚡ Sort by price, duration, or departure time
- 📊 Stats bar — cheapest, average, most expensive fares
- 🤖 AI travel recommendation on every search
- 🌙 Dark sky-themed professional UI

## ⚡ Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 → paste your Groq API key in the sidebar → search!

## 🔑 Get a Free Groq API Key
1. Go to https://console.groq.com
2. Sign up (no credit card required)
3. Create an API key and paste it in the app sidebar

## 🛠 Tech Stack
- **Python 3.11** + **Streamlit** (UI framework)
- **Groq API** with **Llama 3.3 70B** (AI flight generation)
- **Ruff** (linting) · **Mypy** (type checking) · **Pytest** (testing)

## 🧪 Running Tests

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## 🔍 Linting

```bash
ruff check app.py
mypy app.py --ignore-missing-imports
```

## 📁 Project Structure

```
skysearch/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Ruff + Mypy + Pytest config
├── cliff.toml              # Changelog automation config
├── .gitlab-ci.yml          # GitLab CI/CD pipeline
├── .pre-commit-config.yaml # Pre-commit hooks
├── LICENSE                 # AGPLv3 License
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guidelines
├── README.md               # This file
├── tests/                  # Unit tests
│   └── test_app.py
├── specs/                  # Feature specifications
│   └── 001-skysearch-core/
└── .specify/               # Spec-Kit configuration
    ├── memory/
    └── templates/
```

## 📄 License
This project is licensed under the GNU Affero General Public License v3.0.
See [LICENSE](LICENSE) for details.

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---
Built for Swecha Hackathon 2026 · Solo project · Powered by Groq AI
