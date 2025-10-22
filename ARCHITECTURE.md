## Chat-Based Flight Booking Agent (India MVP) — Architecture

### Goals
- Non-linear, low-friction conversational booking with stateful memory and one-tap payment.

### High-Level Components
- Chat UI (Web/WhatsApp/App)
- Language & Intent Layer (LLM + rules fallback)
- Stateful Context Manager (Redis session + Postgres profile)
- Flow Controller (context-aware FSM)
- API Orchestrator (Flight, Payment, Notification connectors)
- Response Generator (natural language + templates)

### Data Model (Session Context)
- intent: book_flight | modify | confirm
- from, to: city/airport
- date: ISO date
- preference: morning/evening/airline/etc.
- booking_stage: collect_slots | search | review | payment | done

### Request Lifecycle (Chat Turn)
1) User message → NLP extracts intent/entities (code-mixed tolerant)
2) State Manager merges into session context (partial updates allowed)
3) Flow Controller checks missing slots; either prompts or triggers search
4) API Orchestrator calls Flight API(s), ranks top options
5) Response Generator formats flight cards + summary chips
6) For confirmation → Payment link via UPI, handle callback, then notify

### Non-Linear Updates
- Mid-flow corrections update session and re-run only necessary steps (e.g., re-rank by preference without refetch if possible).

### Connectors (MVP)
- Flight: Amadeus (search, filter, rank)
- Payment: Razorpay/PayU (UPI link, callback)
- Notification: WhatsApp Business or Email (tickets/receipts)

### Backend Structure (FastAPI)
- app/
  - main.py (app factory, routes)
  - api/routes.py (chat, health)
  - core/config.py (settings via env)
  - services/
    - nlp.py (intent/entities stub)
    - state_manager.py (Redis+PG facade)
    - flow_controller.py (FSM rules)
    - api_orchestrator.py (flight/payment/notify)
    - response_generator.py (templating)

### Future Hooks
- Multimodal travel (train/bus) via new connectors and schemas
- Voice support via Whisper/Indic ASR front-end adapter


