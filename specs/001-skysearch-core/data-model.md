# SkySearch — Data Model

## Flight Object (LLM-generated)

All flight data is ephemeral (session state only). No database.

```typescript
interface Flight {
  airline: string;          // e.g. "IndiGo", "Air India", "Emirates"
  flight_number: string;    // e.g. "6E-204"
  departure: string;        // "HH:MM" format
  arrival: string;          // "HH:MM" format
  duration: string;         // e.g. "1h 45m"
  stops: number;            // 0 = nonstop, 1+ = connecting
  price_usd: number;        // base price in USD
  baggage: string;          // e.g. "15kg checked", "7kg cabin only"
  aircraft: string;         // e.g. "Airbus A320", "Boeing 737"
  meal: string;             // e.g. "Complimentary", "Paid meal", "None"
  refundable: boolean;
}
```

## Search Parameters (Session State)

```typescript
interface SearchParams {
  origin: string;           // IATA code, e.g. "HYD"
  destination: string;      // IATA code, e.g. "BOM"
  travel_date: date;
  passengers: number;       // 1–9
  cabin_class: "Economy" | "Business" | "First";
  currency: "USD" | "INR" | "EUR" | "GBP" | "AED" | "SGD";
  sort_by: "price" | "duration" | "departure";
}
```

## Currency Conversion Rates (Hardcoded Approximations)

| Currency | Rate vs USD |
|---|---|
| USD | 1.0 |
| INR | 83.5 |
| EUR | 0.92 |
| GBP | 0.79 |
| AED | 3.67 |
| SGD | 1.34 |

> Note: Rates are static approximations for display purposes only. Not live exchange rates.
