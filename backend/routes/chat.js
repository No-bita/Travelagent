/**
 * Legacy chat API route
 * Maintains backward compatibility with existing frontend
 */

const express = require('express');
const router = express.Router();

const amadeusClient = require('../services/amadeusClient');
const mockFlights = require('../services/mockFlights');
const rankingService = require('../services/ranking');
const cityValidation = require('../services/cityValidation');
const DateUtils = require('../utils/dates');
const logger = require('../utils/logger');

/**
 * POST /api/chat
 * Legacy chat endpoint - maintains existing functionality
 */
router.post('/', async (req, res) => {
  try {
    const { message, session_id, context } = req.body;
    
    if (!message) {
      return res.json({
        response: "Please provide a message.",
        context: { step: 'initial', origin: null, destination: null, date: null, preference: null }
      });
    }

    logger.info(`Chat request: ${message.substring(0, 100)}...`);

    // Try single-line parsing first
    const singleLinePattern = parseSingleLineFlightRequest(message);
    
    if (singleLinePattern) {
      const { origin, destination, date, preference } = singleLinePattern;
      
      // Validate inputs in parallel for better performance
      const [validOrigin, validDestination] = await Promise.all([
        cityValidation.validateCity(origin),
        cityValidation.validateCity(destination)
      ]);
      
      const validDate = DateUtils.parseDate(date);
      const validPreference = preference || 'price';
      
      if (!validOrigin) {
        return res.json({
          response: "I didn't recognize the origin city. Please try a major Indian city like Delhi, Mumbai, Bangalore, etc.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null },
          actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
        });
      }
      
      if (!validDestination) {
        return res.json({
          response: "I didn't recognize the destination city. Please try a major Indian city like Delhi, Mumbai, Bangalore, etc.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null },
          actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
        });
      }
      
      if (!validDate || !DateUtils.isValidFutureDate(validDate)) {
        return res.json({
          response: "I didn't understand that date. Please try something like 'tomorrow', 'next Monday', '25 Dec', or '2025-12-25'.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null },
          actions: ['Tomorrow', 'Next Monday', '25 Dec 2025', 'Next Week']
        });
      }
      
      // Search flights
      const flights = await searchFlights(validOrigin.code, validDestination.code, validDate);
      const rankedFlights = rankingService.rankFlights(flights, validPreference);
      
      // Format response
      const response = formatFlightResponse(rankedFlights, validOrigin, validDestination, validDate);
      const flightCards = formatFlightCards(rankedFlights);
      
      return res.json({
        response,
        flight_cards: flightCards,
        context: { step: 'complete', origin: validOrigin, destination: validDestination, date: validDate, preference: validPreference, flights: rankedFlights },
        actions: ['Book Flight 1', 'Book Flight 2', 'Book Flight 3', 'Search again', 'Change dates']
      });
    }
    
    // Handle multi-step conversation flow
    if (!context || context.step === 'initial') {
      return res.json({
        response: `✈️ Hi! I'm your flight booking assistant. I can help you find the best flights in India.\n\nTry saying:\n• "search flights"\n• "Delhi to Mumbai tomorrow"  \n• "book flight Bangalore to Chennai next week"\n• "cheap flights from Delhi to Goa"\n\nOr just tell me where you want to go!`,
        context: { step: 'collecting', origin: null, destination: null, date: null, preference: null },
        actions: ['Search flights', 'Delhi to Mumbai', 'Bangalore to Chennai', 'Mumbai to Goa']
      });
    }
    
    // Step-by-step collection
    if (context && context.step === 'collecting') {
      // Collect origin
      if (!context.origin) {
        const originMatch = await cityValidation.findCityMatch(message);
        if (originMatch) {
          return res.json({
            response: `Great! Flying from ${originMatch.name} (${originMatch.airportName}). Where would you like to go?`,
            context: { ...context, origin: originMatch.code, step: 'collecting' },
            actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
          });
        }
        return res.json({
          response: `I didn't recognize that city. Please try one of these major cities:\n\n${['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'].map(city => `• ${city}`).join('\n')}\n\nOr type the city name again.`,
          context: { ...context, step: 'collecting' },
          actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
        });
      }
      
      // Collect destination
      if (!context.destination) {
        const destMatch = await cityValidation.findCityMatch(message);
        if (destMatch && destMatch.code !== context.origin) {
          return res.json({
            response: `Perfect! ${context.origin} to ${destMatch.name} (${destMatch.airportName}). When would you like to travel?`,
            context: { ...context, destination: destMatch.code, step: 'collecting' },
            actions: ['Tomorrow', 'Next Monday', '25 Dec 2025', 'Next Week']
          });
        } else if (destMatch && destMatch.code === context.origin) {
          return res.json({
            response: "Please choose a different destination city. You can't fly from a city to itself!",
            context: { ...context, step: 'collecting' },
            actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
          });
        }
        return res.json({
          response: `I didn't recognize that city. Please try one of these destinations:\n\n${['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'].map(city => `• ${city}`).join('\n')}\n\nOr type the city name again.`,
          context: { ...context, step: 'collecting' },
          actions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata']
        });
      }
      
      // Collect date
      if (!context.date) {
        const validDate = DateUtils.parseDate(message);
        if (validDate && DateUtils.isValidFutureDate(validDate)) {
          return res.json({
            response: `Got it! Travel date: ${DateUtils.formatHumanReadable(validDate)}. What's most important to you: price, time, or convenience?`,
            context: { ...context, date: validDate, step: 'collecting' },
            actions: ['💰 Cheapest', '⚡ Fastest', '🎯 Best Schedule']
          });
        }
        return res.json({
          response: "I didn't understand that date. Please try something like 'tomorrow', 'next Monday', '25 Dec', '25' (for 25th of current/next month), or '2025-12-25'. Make sure it's a future date!",
          context: { ...context, step: 'collecting' },
          actions: ['Tomorrow', 'Next Monday', '25 Dec 2025', 'Next Week']
        });
      }
      
      // Collect preference and trigger search
      if (!context.preference) {
        const lowerMessage = message.toLowerCase();
        const preference = (lowerMessage.includes('price') || lowerMessage.includes('cheap') || lowerMessage.includes('budget')) ? 'price' :
                          (lowerMessage.includes('time') || lowerMessage.includes('fast') || lowerMessage.includes('quick')) ? 'time' :
                          (lowerMessage.includes('convenience') || lowerMessage.includes('comfort') || lowerMessage.includes('direct')) ? 'convenience' : null;
        
        if (!preference) {
          return res.json({
            response: `What's most important to you when choosing a flight?\n\n💰 **Cheapest** - Lowest price flights\n⚡ **Fastest** - Shortest travel time  \n🎯 **Best Schedule** - Optimal departure times, fewer stops\n\nChoose your preference:`,
            context: { ...context, step: 'collecting' },
            actions: ['💰 Cheapest', '⚡ Fastest', '🎯 Best Schedule']
          });
        }
        
        // Trigger search when we have everything
        const [validOrigin, validDestination] = await Promise.all([
          cityValidation.validateCity(context.origin),
          cityValidation.validateCity(context.destination)
        ]);
        
        const flights = await searchFlights(validOrigin.code, validDestination.code, context.date);
        const rankedFlights = rankingService.rankFlights(flights, preference);
        
        const response = formatFlightResponse(rankedFlights, validOrigin, validDestination, context.date);
        const flightCards = formatFlightCards(rankedFlights);
        
        return res.json({
          response,
          flight_cards: flightCards,
          context: { step: 'complete', origin: validOrigin, destination: validDestination, date: context.date, preference, flights: rankedFlights },
          actions: ['Book Flight 1', 'Book Flight 2', 'Book Flight 3', 'Search again', 'Change dates']
        });
      }
    }
    
    // Default response for non-flight queries
    return res.json({
      response: "I'm here to help you find flights! Try saying something like 'Book Mumbai to Delhi tomorrow' or 'Find flights from Bangalore to Chennai next week'.",
      context: { step: 'initial', origin: null, destination: null, date: null, preference: null },
      actions: ['Search flights', 'Delhi to Mumbai', 'Bangalore to Chennai', 'Mumbai to Goa']
    });

  } catch (error) {
    logger.error('Chat endpoint error:', error);
    res.json({
      response: "Sorry, I encountered an error. Please try again.",
      context: { step: 'collecting', origin: null, destination: null, date: null, preference: null }
    });
  }
});

/**
 * Parse single-line flight request with comprehensive pattern matching
 * @param {string} message - User message
 * @returns {Object|null} - Parsed flight request or null
 */
function parseSingleLineFlightRequest(message) {
  const lowerMessage = message.toLowerCase().trim();
  
  // Comprehensive patterns for flight requests
  const patterns = [
    // "Book Mumbai to Delhi tomorrow"
    /book\s+(\w+)\s+to\s+(\w+)\s+(.+)/i,
    // "Find flights from Bangalore to Chennai next week"
    /find\s+flights?\s+from\s+(\w+)\s+to\s+(\w+)\s+(.+)/i,
    // "Mumbai Delhi tomorrow"
    /^(\w+)\s+(\w+)\s+(.+)$/i,
    // "I want to go from Mumbai to Delhi tomorrow"
    /i\s+want\s+to\s+go\s+from\s+(\w+)\s+to\s+(\w+)\s+(.+)/i,
    // "Search flights Mumbai to Delhi tomorrow"
    /search\s+flights?\s+(\w+)\s+to\s+(\w+)\s+(.+)/i,
    // "Flights from Mumbai to Delhi tomorrow"
    /flights?\s+from\s+(\w+)\s+to\s+(\w+)\s+(.+)/i,
    // "Mumbai to Delhi tomorrow" (with "to")
    /^(\w+)\s+to\s+(\w+)\s+(.+)$/i,
    // "Cheap flights Mumbai Delhi tomorrow"
    /cheap\s+flights?\s+(\w+)\s+(\w+)\s+(.+)/i,
    // "Fastest flights from Mumbai to Delhi tomorrow"
    /fastest\s+flights?\s+from\s+(\w+)\s+to\s+(\w+)\s+(.+)/i
  ];
  
  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match) {
      let origin = match[1].trim();
      let destination = match[2].trim();
      let date = match[3].trim();
      
      // Extract preference from the message
      const preferenceKeywords = {
        cheap: 'price',
        cheapest: 'price',
        budget: 'price',
        price: 'price',
        fast: 'time',
        fastest: 'time',
        quick: 'time',
        time: 'time',
        convenient: 'convenience',
        convenience: 'convenience',
        comfort: 'convenience',
        direct: 'convenience'
      };
      
      let preference = 'price'; // default
      for (const [keyword, pref] of Object.entries(preferenceKeywords)) {
        if (lowerMessage.includes(keyword)) {
          preference = pref;
          break;
        }
      }
      
      // Clean up date string
      date = date.replace(/[,\-.]/g, ' ').replace(/\s+/g, ' ').trim();
      
      return { origin, destination, date, preference };
    }
  }
  
  return null;
}

/**
 * Search flights using available services
 * @param {string} origin - Origin airport code
 * @param {string} destination - Destination airport code
 * @param {string} date - Departure date
 * @returns {Array} - Flight offers
 */
async function searchFlights(origin, destination, date) {
  try {
    if (amadeusClient.isAvailable()) {
      logger.info('Using Amadeus API for chat flight search');
      return await amadeusClient.searchFlights(origin, destination, date);
    } else {
      logger.info('Amadeus API not available, using mock data for chat');
      return mockFlights.generateMockFlights(origin, destination, date, 15);
    }
  } catch (error) {
    logger.warn('Flight search failed in chat, using mock data:', error.message);
    return mockFlights.generateMockFlights(origin, destination, date, 15);
  }
}

/**
 * Format flight response text with enhanced user experience
 * @param {Array} flights - Ranked flights
 * @param {Object} origin - Origin city info
 * @param {Object} destination - Destination city info
 * @param {string} date - Departure date
 * @returns {string} - Formatted response
 */
function formatFlightResponse(flights, origin, destination, date) {
  if (!flights || flights.length === 0) {
    return `Sorry, I couldn't find any flights from ${origin.name} to ${destination.name} on ${DateUtils.formatHumanReadable(date)}.`;
  }
  
  const topFlights = flights.slice(0, 3); // Show top 3 flights
  const readableDate = DateUtils.formatHumanReadable(date);
  
  let response = `Here are the top ${Math.min(3, flights.length)} flights from ${origin.name} to ${destination.name} on ${readableDate}:\n\n`;
  
  topFlights.forEach((flight, index) => {
    const price = parseFloat(flight.price.total);
    const duration = flight.itineraries[0]?.duration || 'Unknown';
    const segments = flight.itineraries[0]?.segments || [];
    const isDirect = segments.length === 1;
    const carrierCode = flight.validatingAirlineCodes?.[0] || 'Unknown';
    const airlineName = require('../utils/airlines').getAirlineName(carrierCode);
    
    // Format departure and arrival times
    const departureTime = segments[0]?.departure?.at ? 
      new Date(segments[0].departure.at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Unknown';
    const arrivalTime = segments[segments.length - 1]?.arrival?.at ? 
      new Date(segments[segments.length - 1].arrival.at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Unknown';
    
    response += `${index + 1}. **${airlineName}** - ₹${price.toLocaleString()}\n`;
    response += `   Departure: ${departureTime} | Arrival: ${arrivalTime}\n`;
    response += `   Duration: ${duration}\n`;
    response += `   ${isDirect ? 'Direct flight' : `${segments.length - 1} stop(s)`}\n`;
    
    // Add badges if available
    if (flight.badges && flight.badges.length > 0) {
      const badgeLabels = flight.badges.map(badge => badge.label).join(', ');
      response += `   🏷️ ${badgeLabels}\n`;
    }
    
    response += '\n';
  });
  
  response += `Which flight interests you most? I can provide more details or help you with the next steps!`;
  
  return response;
}

/**
 * Format flight cards for frontend with enhanced structure
 * @param {Array} flights - Ranked flights
 * @returns {Array} - Formatted flight cards
 */
function formatFlightCards(flights) {
  return flights.slice(0, 5).map((flight, index) => {
    const segments = flight.itineraries[0]?.segments || [];
    const firstSegment = segments[0];
    const lastSegment = segments[segments.length - 1];
    const price = parseFloat(flight.price.total);
    const duration = flight.itineraries[0]?.duration || 'Unknown';
    const carrierCode = flight.validatingAirlineCodes?.[0] || 'Unknown';
    const airlineName = require('../utils/airlines').getAirlineName(carrierCode);
    const airlineColor = require('../utils/airlines').getAirlineColor(carrierCode);
    
    // Format times
    const departureTime = firstSegment?.departure?.at ? 
      new Date(firstSegment.departure.at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Unknown';
    const arrivalTime = lastSegment?.arrival?.at ? 
      new Date(lastSegment.arrival.at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Unknown';
    
    // Determine flight characteristics
    const isDirect = segments.length === 1;
    const stops = isDirect ? 0 : segments.length - 1;
    
    return {
      id: flight.id,
      rank: index + 1,
      airline: carrierCode,
      airline_name: airlineName,
      airline_color: airlineColor,
      flight_number: `${carrierCode}${Math.floor(Math.random() * 9999) + 1}`,
      departure_time: departureTime,
      arrival_time: arrivalTime,
      duration: duration,
      stops: stops,
      stops_text: isDirect ? 'Direct' : `${stops} stop(s)`,
      price: price,
      formatted_price: `₹${price.toLocaleString()}`,
      currency: 'INR',
      class: 'Economy',
      class_icon: '💺',
      class_color: '#4CAF50',
      confidence: 0.85 + Math.random() * 0.15,
      source: 'Travel Agent',
      bookable: true,
      // Badge information
      is_cheapest: flight.badges?.some(b => b.type === 'cheapest') || false,
      is_fastest: flight.badges?.some(b => b.type === 'fastest') || false,
      is_direct: flight.badges?.some(b => b.type === 'direct') || false,
      is_convenient: flight.badges?.some(b => b.type === 'convenient') || false,
      badges: flight.badges || [],
      // Additional metadata
      aircraft: firstSegment?.aircraft?.code || 'Unknown',
      origin_airport: firstSegment?.departure?.iataCode || 'Unknown',
      destination_airport: lastSegment?.arrival?.iataCode || 'Unknown'
    };
  });
}

module.exports = router;
