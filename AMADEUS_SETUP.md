# Amadeus API Integration Setup

This guide will help you set up the Amadeus API integration for real flight data.

## 1. Get Amadeus API Credentials

1. **Register for Amadeus for Developers**
   - Go to [https://developers.amadeus.com/](https://developers.amadeus.com/)
   - Create a free account
   - Complete the registration process

2. **Create a New App**
   - Log in to your Amadeus for Developers dashboard
   - Click "Create New App"
   - Fill in the required information:
     - App Name: "Travel Agent Flight Search"
     - Description: "Flight search for Indian domestic routes"
     - Category: "Travel"
   - Select "Self-Service" for the API type
   - Choose the "Flight Search API" service

3. **Get Your Credentials**
   - After creating the app, you'll get:
     - `Client ID` (API Key)
     - `Client Secret` (API Secret)
   - Copy these values - you'll need them for the environment variables

## 2. Configure Environment Variables

1. **Create a `.env` file** in your project root:
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file** with your Amadeus credentials:
   ```
   AMADEUS_CLIENT_ID=your_actual_client_id_here
   AMADEUS_CLIENT_SECRET=your_actual_client_secret_here
   PORT=3000
   NODE_ENV=development
   ```

## 3. Test the Integration

1. **Start the server:**
   ```bash
   npm start
   ```

2. **Test with the demo:**
   ```bash
   node demo.js
   ```

3. **Check the console logs** to see if the API is working:
   - If you see "Found X flights from Amadeus API" - ✅ API is working
   - If you see "Amadeus API credentials not configured" - ❌ Check your .env file
   - If you see "Authentication failed" - ❌ Check your credentials

## 4. API Limits and Considerations

### Free Tier Limits
- **Monthly Requests**: 2,000 requests per month
- **Rate Limit**: 10 requests per second
- **Data Freshness**: Real-time data

### Production Considerations
- **Rate Limiting**: The app includes automatic fallback to mock data if rate limits are exceeded
- **Error Handling**: Comprehensive error handling for API failures
- **Caching**: Consider implementing caching for frequently searched routes
- **Monitoring**: Monitor API usage in your Amadeus dashboard

## 5. Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Double-check your Client ID and Client Secret
   - Ensure there are no extra spaces in the .env file
   - Verify the credentials in your Amadeus dashboard

2. **"No flights found"**
   - This is normal for some routes or dates
   - The app will automatically fall back to mock data
   - Try different popular routes like DEL-BOM or BOM-BLR

3. **"Rate limit exceeded"**
   - The app will wait 2 seconds and use mock data
   - Consider upgrading your Amadeus plan for higher limits

4. **API not responding**
   - Check your internet connection
   - Verify the Amadeus API status
   - The app will gracefully fall back to mock data

### Testing Different Scenarios

```bash
# Test with popular Indian routes
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "search flights", "context": {"step": "initial"}}'
```

## 6. Production Deployment

For production deployment:

1. **Use Environment Variables**: Never commit API keys to version control
2. **Monitor Usage**: Set up alerts for API quota limits
3. **Implement Caching**: Cache flight results for popular routes
4. **Error Monitoring**: Set up proper logging and monitoring
5. **Rate Limiting**: Implement client-side rate limiting

## 7. API Response Format

The Amadeus API returns flight data in this format:
```json
{
  "data": [
    {
      "itineraries": [
        {
          "segments": [
            {
              "departure": {"at": "2025-12-25T15:30:00"},
              "arrival": {"at": "2025-12-25T17:30:00"},
              "carrierCode": "6E",
              "number": "123"
            }
          ]
        }
      ],
      "price": {
        "total": "4500.00",
        "currency": "INR"
      }
    }
  ]
}
```

The app processes this data and presents it in a user-friendly format with proper Indian airline names and pricing.

## 8. Next Steps

- **Upgrade Plan**: Consider upgrading to a paid plan for higher limits
- **Add Features**: Implement flight booking, seat selection, etc.
- **Optimize**: Add caching and performance optimizations
- **Monitor**: Set up proper monitoring and alerting

---

**Note**: The app is designed to work seamlessly with or without the Amadeus API. If the API is not configured or fails, it will automatically use mock data to ensure the user experience is not interrupted.

