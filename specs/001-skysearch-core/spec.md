# SkySearch — Spec (User Stories & Requirements)

## Overview
SkySearch lets users search for flights between any two airports using IATA codes. Results are AI-generated via Groq and rendered in a polished dark-themed UI.

---

## User Stories

### US-001 · Flight Search
**As a** user,  
**I want to** enter origin, destination, date, passengers, and cabin class,  
**So that** I can see a list of realistic AI-generated flight options.

**Acceptance Criteria:**
- IATA code inputs (e.g. HYD → BOM)
- Date picker (today + future only)
- Passenger count (1–9)
- Cabin class: Economy / Business / First
- On submit → Groq API called → results rendered as flight cards

---

### US-002 · Multi-Currency Support
**As a** user,  
**I want to** choose my preferred currency (USD, INR, EUR, GBP, AED, SGD),  
**So that** prices are displayed in a format relevant to me.

---

### US-003 · Sort & Filter
**As a** user,  
**I want to** sort results by price / duration / departure time,  
**So that** I can find the best option for my needs.

---

### US-004 · Stats Bar
**As a** user,  
**I want to** see cheapest / average / most expensive fares at a glance,  
**So that** I can quickly understand the price range for the route.

---

### US-005 · AI Travel Recommendation
**As a** user,  
**I want to** receive an AI-generated travel tip for my route,  
**So that** I get destination context beyond just flight data.

---

### US-006 · API Key Input
**As a** user,  
**I want to** paste my Groq API key into the sidebar,  
**So that** I can use the app without any env file setup.

---

## Non-Functional Requirements
- Page load < 2s (before any API call)
- Groq API timeout: 30s
- Graceful error display if Groq fails or returns malformed JSON
- UI must be responsive across desktop screen widths
