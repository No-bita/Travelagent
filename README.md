# Travel Agent - Flight Search MVP for India

A conversational flight search agent focused on Indian domestic flights, providing the top 3 flight options with best-in-category labeling.

## Features

- **Conversational Input Collection**: Collects user inputs in sequence (origin, destination, date, preference)
- **User-Friendly Date Input**: Accepts natural language dates like "tomorrow", "next monday", "25 Dec 2025"
- **Smart Loading Indicators**: Context-aware loading states with animated progress messages
- **Flight Search & Filtering**: Searches and filters Indian domestic flights
- **Smart Ranking**: Shows top 3 flights in categories: cheapest price, shortest duration, most convenient
- **Chat Interface**: User-friendly conversational UI with visual feedback
- **Input Validation**: Validates Indian airports and future dates with helpful error messages

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Server**
   ```bash
   npm start
   ```

3. **Open the Chat Interface**
   - Open `index.html` in your browser
   - Or serve it with a local server: `python -m http.server 8000`

### Backend (FastAPI) — Setup & Run

1. Install dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Configure environment (optional)
   - Copy `env.example` to `.env` at repo root and fill Amadeus credentials
   - For multi-source: add Cleartrip keys
     - `CLEARTRIP_API_KEY=...`
     - `CLEARTRIP_API_BASE=https://partner.cleartrip.com/api` (example)
     - `CLEARTRIP_API_HEADER=X-API-Key` (if required by partner)
   - Without credentials, system uses mock flight data
3. Start API server (default http://localhost:8000)
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Test endpoints
   - `GET http://localhost:8000/health`
   - `POST http://localhost:8000/chat` with `{ "session_id": "demo", "message": "Book Mumbai to Delhi tomorrow morning" }`

**Note**: The system works with mock data by default. For real Amadeus flight data, add your API credentials to `.env`.

### Frontend ↔ Backend
- The static `index.html` now talks to the backend at `http://localhost:8000`.
- A persistent `session_id` is stored in `localStorage` to keep conversation context.

## Usage

1. Start a conversation by typing "search flights"
2. Provide your origin city (e.g., "Delhi", "Mumbai")
3. Provide your destination city (e.g., "Bangalore", "Chennai")
4. Enter your travel date (YYYY-MM-DD format)
5. Choose your preference: price, time, or convenience
6. Get top 3 flight recommendations with clear labeling

## API Endpoints

- `POST /api/chat` - Main chat interface
- `GET /api/health` - Health check

## Supported Indian Cities

- Delhi (DEL)
- Mumbai (BOM)
- Bangalore (BLR)
- Kolkata (CCU)
- Chennai (MAA)
- Hyderabad (HYD)
- Ahmedabad (AMD)
- Pune (PNQ)
- Kochi (COK)
- Goa (GOI)
- Jaipur (JAI)
- Lucknow (LKO)
- And more...

## Current Implementation

- **Amadeus API Integration**: Real flight data from Amadeus API with fallback to mock data
- **Smart Fallback**: Automatically uses mock data if API is unavailable or rate-limited
- **Error Handling**: Comprehensive error handling for API failures
- **Responsive Design**: Works on desktop and mobile devices

## Future Enhancements

- Integration with real flight APIs
- Booking functionality
- Price alerts
- Multi-city search
- Hotel and car rental integration

## Development

```bash
# Development mode with auto-restart
npm run dev

# Production mode
npm start
```

## Environment Variables

Create a `.env` file based on `env.example`:

```
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
PORT=3000
NODE_ENV=development
```

**Note**: Get your Amadeus API credentials from [developers.amadeus.com](https://developers.amadeus.com/). See `AMADEUS_SETUP.md` for detailed setup instructions.

## License

MIT
