const express = require('express');
const cors = require('cors');
const axios = require('axios');
const moment = require('moment');
const Amadeus = require('amadeus');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Amadeus API (only if credentials are provided)
let amadeus = null;
if (process.env.AMADEUS_CLIENT_ID && process.env.AMADEUS_CLIENT_SECRET) {
  amadeus = new Amadeus({
    clientId: process.env.AMADEUS_CLIENT_ID,
    clientSecret: process.env.AMADEUS_CLIENT_SECRET
  });
  console.log('Amadeus API initialized with credentials');
} else {
  console.log('Amadeus API credentials not found - using mock data mode');
}

// Middleware
app.use(cors());
app.use(express.json());

// City recognition is now handled entirely by the backend API
// No local city data needed in frontend - all city logic moved to backend

// Amadeus API flight search function with error handling and rate limiting
async function searchFlightsWithAmadeus(origin, destination, date) {
  try {
    console.log(`Searching flights: ${origin} → ${destination} on ${date}`);
    
    // Check if Amadeus client is initialized
    if (!amadeus) {
      console.log('Amadeus API not initialized, using mock data');
      return generateMockFlights(origin, destination, date);
    }
    
    const response = await amadeus.shopping.flightOffersSearch.get({
      originLocationCode: origin,
      destinationLocationCode: destination,
      departureDate: date,
      adults: 1,
      max: 20 // Get more options to choose from
    });

    if (!response.data || !response.data.length) {
      console.log('No flights found in Amadeus API, falling back to mock data');
      return generateMockFlights(origin, destination, date);
    }

    const flights = response.data.map((offer, index) => {
      const itinerary = offer.itineraries[0];
      const segments = itinerary.segments;
      const price = parseFloat(offer.price.total);
      const currency = offer.price.currency;
      
      // Calculate total duration
      const departureTime = moment(segments[0].departure.at);
      const arrivalTime = moment(segments[segments.length - 1].arrival.at);
      const duration = arrivalTime.diff(departureTime, 'minutes');
      
      // Count stops
      const stops = segments.length - 1;
      
      // Get airline name from first segment
      const airlineCode = segments[0].carrierCode;
      const airlineName = getAirlineName(airlineCode);
      
      return {
        id: `AM${index + 1}`,
        airline: airlineName,
        price: Math.round(price),
        duration: duration,
        departureTime: departureTime.format('HH:mm'),
        arrivalTime: arrivalTime.format('HH:mm'),
        departureDate: departureTime.format('YYYY-MM-DD'),
        arrivalDate: arrivalTime.format('YYYY-MM-DD'),
        origin: origin,
        destination: destination,
        stops: stops,
        layoverTime: stops > 0 ? calculateLayoverTime(segments) : 0,
        currency: currency,
        flightNumber: segments[0].number,
        aircraft: segments[0].aircraft?.code || 'Unknown'
      };
    });

    console.log(`Found ${flights.length} flights from Amadeus API`);
    return flights;

  } catch (error) {
    console.error('Amadeus API Error:', error.message);
    
    // Handle specific error types
    if (error.code === 401) {
      console.log('Authentication failed - check API credentials');
    } else if (error.code === 429) {
      console.log('Rate limit exceeded - implementing delay');
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      return generateMockFlights(origin, destination, date);
    } else if (error.code === 400) {
      console.log('Invalid request parameters');
    }
    
    console.log('Falling back to mock data due to API error');
    return generateMockFlights(origin, destination, date);
  }
}

// Fallback mock flight data generator
function generateMockFlights(origin, destination, date) {
  const airlines = ['IndiGo', 'Air India', 'SpiceJet', 'Vistara', 'GoAir', 'AirAsia India'];
  const flights = [];
  
  // Generate 10-15 mock flights
  const numFlights = Math.floor(Math.random() * 6) + 10;
  
  for (let i = 0; i < numFlights; i++) {
    const airline = airlines[Math.floor(Math.random() * airlines.length)];
    const basePrice = Math.floor(Math.random() * 15000) + 3000; // ₹3000-18000
    const duration = Math.floor(Math.random() * 300) + 60; // 1-6 hours
    const departureHour = Math.floor(Math.random() * 24);
    const departureMinute = Math.floor(Math.random() * 60);
    
    const departureTime = moment(date).hour(departureHour).minute(departureMinute);
    const arrivalTime = moment(departureTime).add(duration, 'minutes');
    
    flights.push({
      id: `FL${i + 1}`,
      airline,
      price: basePrice,
      duration: duration,
      departureTime: departureTime.format('HH:mm'),
      arrivalTime: arrivalTime.format('HH:mm'),
      departureDate: departureTime.format('YYYY-MM-DD'),
      arrivalDate: arrivalTime.format('YYYY-MM-DD'),
      origin: origin,
      destination: destination,
      stops: Math.random() > 0.7 ? 1 : 0, // 30% chance of layover
      layoverTime: Math.random() > 0.7 ? Math.floor(Math.random() * 180) + 30 : 0,
      currency: 'INR'
    });
  }
  
  return flights;
}

// Helper function to get airline name from code
function getAirlineName(code) {
  const airlines = {
    '6E': 'IndiGo',
    'AI': 'Air India',
    'SG': 'SpiceJet',
    'UK': 'Vistara',
    'G8': 'GoAir',
    'I5': 'AirAsia India',
    '9W': 'Jet Airways',
    'S2': 'JetLite'
  };
  return airlines[code] || code;
}

// Helper function to calculate layover time
function calculateLayoverTime(segments) {
  if (segments.length < 2) return 0;
  
  let totalLayover = 0;
  for (let i = 0; i < segments.length - 1; i++) {
    const arrival = moment(segments[i].arrival.at);
    const departure = moment(segments[i + 1].departure.at);
    totalLayover += departure.diff(arrival, 'minutes');
  }
  return totalLayover;
}

// Input validation functions - now handled by backend API
async function validateCityCode(cityCode) {
  try {
    const response = await fetch('http://localhost:8000/api/cities/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: cityCode })
    });
    
    if (!response.ok) return null;
    
    const data = await response.json();
    return data.found ? {
      code: data.city.airport_code,
      name: data.city.canonical_name,
      airportName: `${data.city.canonical_name} Airport`
    } : null;
  } catch (error) {
    console.error('City validation error:', error);
    return null;
  }
}

// Enhanced city matching using backend API
async function findCityMatch(input) {
  try {
    const response = await fetch('http://localhost:8000/api/cities/match', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input })
    });
    
    if (!response.ok) {
      console.error('City matching API failed:', response.status);
      return null;
    }
    
    const data = await response.json();
    
    if (data.found && data.city) {
      // Convert backend response to frontend format
      return {
        name: data.city.canonical_name,
        city: data.city.canonical_name,
        code: data.city.airport_code,
        aliases: data.city.variations,
        airportName: `${data.city.canonical_name} Airport`,
        matchType: data.city.match_type,
        confidence: data.city.confidence
      };
    }
    
    return null;
  } catch (error) {
    console.error('City matching error:', error);
    return null;
  }
}

// Similarity calculations removed - now handled by backend API

function validateDate(dateString) {
  const lowerString = dateString.toLowerCase().trim();
  
  // Handle natural language dates first
  if (lowerString.includes('tomorrow')) {
    return moment().add(1, 'day').format('YYYY-MM-DD');
  } else if (lowerString.includes('day after tomorrow')) {
    return moment().add(2, 'days').format('YYYY-MM-DD');
  } else if (lowerString.includes('next week')) {
    return moment().add(1, 'week').format('YYYY-MM-DD');
  } else if (lowerString.includes('next month')) {
    return moment().add(1, 'month').format('YYYY-MM-DD');
  } else if (lowerString.includes('next year')) {
    return moment().add(1, 'year').format('YYYY-MM-DD');
  }
  
  // Handle "next [day of week]"
  const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  for (let i = 0; i < daysOfWeek.length; i++) {
    if (lowerString.includes(`next ${daysOfWeek[i]}`)) {
      return moment().day(i + 7).format('YYYY-MM-DD');
    }
  }
  
  // Handle "this [day of week]"
  for (let i = 0; i < daysOfWeek.length; i++) {
    if (lowerString.includes(`this ${daysOfWeek[i]}`)) {
      const thisWeekDay = moment().day(i);
      const nextWeekDay = moment().day(i + 7);
      const date = thisWeekDay.isAfter(moment()) ? thisWeekDay : nextWeekDay;
      return date.format('YYYY-MM-DD');
    }
  }
  
  // Handle "in X days/weeks/months"
  const inDaysMatch = lowerString.match(/in (\d+) days?/);
  if (inDaysMatch) {
    return moment().add(parseInt(inDaysMatch[1]), 'days').format('YYYY-MM-DD');
  }
  
  const inWeeksMatch = lowerString.match(/in (\d+) weeks?/);
  if (inWeeksMatch) {
    return moment().add(parseInt(inWeeksMatch[1]), 'weeks').format('YYYY-MM-DD');
  }
  
  const inMonthsMatch = lowerString.match(/in (\d+) months?/);
  if (inMonthsMatch) {
    return moment().add(parseInt(inMonthsMatch[1]), 'months').format('YYYY-MM-DD');
  }
  
  // NEW: Handle partial dates - just day number (e.g., "25", "25th")
  const dayOnlyMatch = lowerString.match(/^(\d{1,2})(?:st|nd|rd|th)?$/);
  if (dayOnlyMatch) {
    const day = parseInt(dayOnlyMatch[1]);
    if (day >= 1 && day <= 31) {
      return handlePartialDate(day);
    }
  }
  
  // Try parsing with moment's flexible parsing
  let date = moment(dateString);
  
  // If that didn't work, try with common formats
  if (!date.isValid()) {
    const formats = [
      'YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'MM/DD/YYYY',
      'DD MMM YYYY', 'DD MMMM YYYY', 'MMM DD, YYYY', 'MMMM DD, YYYY',
      'DD-MM-YY', 'DD/MM/YY', 'MM/DD/YY', 'YYYY/MM/DD',
      'DD.MM.YYYY', 'MM-DD-YYYY', 'DD-MMM-YYYY',
      'DD MMM', 'MMM DD', 'DD MMMM', 'MMMM DD'
    ];
    date = moment(dateString, formats, true);
  }
  
  if (!date.isValid()) return null;
  if (date.isBefore(moment(), 'day')) return null;
  
  return date.format('YYYY-MM-DD');
}

function handlePartialDate(day) {
  const today = moment();
  const currentMonth = today.month();
  const currentYear = today.year();
  
  // Try current month first
  const currentMonthDate = moment([currentYear, currentMonth, day]);
  if (currentMonthDate.isValid() && currentMonthDate.isAfter(today, 'day')) {
    return currentMonthDate.format('YYYY-MM-DD');
  }
  
  // Try next month
  const nextMonth = currentMonth === 11 ? 0 : currentMonth + 1;
  const nextMonthYear = currentMonth === 11 ? currentYear + 1 : currentYear;
  const nextMonthDate = moment([nextMonthYear, nextMonth, day]);
  if (nextMonthDate.isValid()) {
    return nextMonthDate.format('YYYY-MM-DD');
  }
  
  // Try next year
  const nextYearDate = moment([currentYear + 1, currentMonth, day]);
  if (nextYearDate.isValid()) {
    return nextYearDate.format('YYYY-MM-DD');
  }
  
  return null;
}

function isPartialDateInput(input) {
  // Check if input is just a day number (partial date)
  const dayOnlyMatch = input.toLowerCase().match(/^(\d{1,2})(?:st|nd|rd|th)?$/);
  return dayOnlyMatch && parseInt(dayOnlyMatch[1]) >= 1 && parseInt(dayOnlyMatch[1]) <= 31;
}

function generateAlternativeDates(inferredDate) {
  const date = moment(inferredDate);
  const alternatives = [];
  
  // Add same day next month
  const nextMonth = date.clone().add(1, 'month');
  if (nextMonth.isValid()) {
    alternatives.push(`• ${nextMonth.format('DD MMM YYYY')} (next month)`);
  }
  
  // Add same day next year
  const nextYear = date.clone().add(1, 'year');
  if (nextYear.isValid()) {
    alternatives.push(`• ${nextYear.format('DD MMM YYYY')} (next year)`);
  }
  
  // Add nearby days in same month
  const dayBefore = date.clone().subtract(1, 'day');
  const dayAfter = date.clone().add(1, 'day');
  
  if (dayBefore.isValid() && dayBefore.isAfter(moment(), 'day')) {
    alternatives.push(`• ${dayBefore.format('DD MMM YYYY')} (day before)`);
  }
  if (dayAfter.isValid()) {
    alternatives.push(`• ${dayAfter.format('DD MMM YYYY')} (day after)`);
  }
  
  return alternatives.length > 0 ? 
    `Alternative dates:\n${alternatives.join('\n')}` : 
    'No alternative dates available.';
}

// Generate clickable option labels for confirmation UI
function generateAlternativeOptions(inferredDate) {
  const date = moment(inferredDate);
  const options = [];
  
  // Primary actions
  options.push('Yes');
  options.push('No');
  
  // Same day next month
  const nextMonth = date.clone().add(1, 'month');
  if (nextMonth.isValid()) options.push(nextMonth.format('DD MMM YYYY'));
  
  // Same day next year
  const nextYear = date.clone().add(1, 'year');
  if (nextYear.isValid()) options.push(nextYear.format('DD MMM YYYY'));
  
  // Nearby days
  const dayBefore = date.clone().subtract(1, 'day');
  const dayAfter = date.clone().add(1, 'day');
  if (dayBefore.isValid() && dayBefore.isAfter(moment(), 'day')) options.push(dayBefore.format('DD MMM YYYY'));
  if (dayAfter.isValid()) options.push(dayAfter.format('DD MMM YYYY'));
  
  // Ensure uniqueness and limit count
  return Array.from(new Set(options)).slice(0, 6);
}

function validatePreference(preference) {
  const validPreferences = ['price', 'time', 'convenience'];
  return validPreferences.includes(preference.toLowerCase());
}

// Flight ranking and filtering
function rankFlights(flights) {
  // Sort by different criteria
  const cheapest = [...flights].sort((a, b) => a.price - b.price)[0];
  const shortest = [...flights].sort((a, b) => a.duration - b.duration)[0];
  
  // Most convenient: best departure time (morning/evening) and no layovers
  const mostConvenient = [...flights]
    .filter(f => f.stops === 0)
    .sort((a, b) => {
      const aHour = parseInt(a.departureTime.split(':')[0]);
      const bHour = parseInt(b.departureTime.split(':')[0]);
      const aScore = Math.abs(aHour - 9) + Math.abs(aHour - 18); // Prefer 9 AM or 6 PM
      const bScore = Math.abs(bHour - 9) + Math.abs(bHour - 18);
      return aScore - bScore;
    })[0] || flights[0];
  
  return [
    { ...cheapest, category: 'Cheapest Price', reason: 'Best value for money' },
    { ...shortest, category: 'Shortest Duration', reason: 'Fastest travel time' },
    { ...mostConvenient, category: 'Most Convenient', reason: 'Best schedule with no layovers' }
  ];
}

// Function to parse single-line flight requests
function parseSingleLineFlightRequest(message) {
  const lowerMessage = message.toLowerCase().trim();
  
  // Common patterns for single-line flight requests
  const patterns = [
    // "bom to del tomorrow"
    /^([a-z]{3})\s+to\s+([a-z]{3})\s+(.+)$/,
    // "mumbai to delhi tomorrow"
    /^([a-z\s]+)\s+to\s+([a-z\s]+)\s+(.+)$/,
    // "bom del tomorrow"
    /^([a-z]{3})\s+([a-z]{3})\s+(.+)$/,
    // "mumbai delhi tomorrow"
    /^([a-z\s]+)\s+([a-z\s]+)\s+(.+)$/,
    // "flights from bom to del tomorrow"
    /^flights?\s+from\s+([a-z\s]+)\s+to\s+([a-z\s]+)\s+(.+)$/,
    // "search flights bom to del tomorrow"
    /^search\s+flights?\s+([a-z\s]+)\s+to\s+([a-z\s]+)\s+(.+)$/,
    // "book flight bom to del tomorrow"
    /^book\s+flight\s+([a-z\s]+)\s+to\s+([a-z\s]+)\s+(.+)$/
  ];
  
  for (const pattern of patterns) {
    const match = lowerMessage.match(pattern);
    if (match) {
      let origin = match[1].trim();
      let destination = match[2].trim();
      let date = match[3].trim();
      let preference = null;
      
      // Check if preference is mentioned in the date string
      const preferenceKeywords = {
        'cheap': 'price',
        'cheapest': 'price',
        'budget': 'price',
        'price': 'price',
        'fast': 'time',
        'fastest': 'time',
        'quick': 'time',
        'time': 'time',
        'convenient': 'convenience',
        'convenience': 'convenience',
        'comfort': 'convenience',
        'direct': 'convenience'
      };
      
      for (const [keyword, pref] of Object.entries(preferenceKeywords)) {
        if (date.includes(keyword)) {
          preference = pref;
          date = date.replace(keyword, '').trim();
          break;
        }
      }
      
      // Clean up date string
      date = date.replace(/[,\-\.]/g, ' ').replace(/\s+/g, ' ').trim();
      
      return {
        origin,
        destination,
        date,
        preference
      };
    }
  }
  
  return null;
}

// API Routes
app.post('/api/chat', async (req, res) => {
  try {
    const { message, context } = req.body;
    
    // Parse user input for flight search parameters
    const lowerMessage = message.toLowerCase();
    
    // Check for single-line flight search patterns
    const singleLinePattern = parseSingleLineFlightRequest(message);
    console.log('Single-line pattern result:', singleLinePattern);
    if (singleLinePattern) {
      const { origin, destination, date, preference } = singleLinePattern;
      
      // Validate all inputs using backend API
      const validOrigin = await validateCityCode(origin);
      const validDestination = await validateCityCode(destination);
      const validDate = validateDate(date);
      const validPreference = preference || 'price'; // Default to price if not specified
      
      if (!validOrigin) {
        return res.json({
          response: "I didn't recognize the origin city. Please try a major Indian city like Delhi, Mumbai, Bangalore, etc.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null }
        });
      }
      
      if (!validDestination) {
        return res.json({
          response: "I didn't recognize the destination city. Please try a major Indian city like Delhi, Mumbai, Bangalore, etc.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null }
        });
      }
      
      if (!validDate) {
        return res.json({
          response: "I didn't understand that date. Please try something like 'tomorrow', 'next Monday', '25 Dec', or '2025-12-25'.",
          context: { step: 'collecting', origin: null, destination: null, date: null, preference: null }
        });
      }
      
      // Search flights using Amadeus API
      const flights = await searchFlightsWithAmadeus(validOrigin.code, validDestination.code, validDate);
      const topFlights = rankFlights(flights);
      
      // Format response
      const response = `Here are the top 3 flights from ${validOrigin.name} to ${validDestination.name} on ${moment(validDate).format('DD MMM YYYY')}:\n\n` +
        topFlights.map((flight, index) => 
          `${index + 1}. **${flight.airline}** - ₹${flight.price.toLocaleString()}\n` +
          `   ${flight.category}: ${flight.reason}\n` +
          `   Departure: ${flight.departureTime} | Arrival: ${flight.arrivalTime}\n` +
          `   Duration: ${Math.floor(flight.duration / 60)}h ${flight.duration % 60}m\n` +
          `   ${flight.stops > 0 ? `${flight.stops} stop(s)` : 'Direct flight'}`
        ).join('\n\n') +
        `\n\nWhich flight interests you most? I can provide more details or help you with the next steps!`;
      
      return res.json({
        response,
        context: { step: 'complete', flights: topFlights },
        flight_cards: topFlights.map(flight => ({
          id: flight.id,
          airline: flight.airline,
          price: flight.price,
          currency: flight.currency,
          departureTime: flight.departureTime,
          arrivalTime: flight.arrivalTime,
          duration: flight.duration,
          stops: flight.stops,
          category: flight.category,
          reason: flight.reason,
          flightNumber: flight.flightNumber || 'N/A',
          aircraft: flight.aircraft || 'N/A'
        }))
      });
      return; // Exit after single-line parsing
    }
    
    // Check if user is providing flight search information
    if (context && context.step === 'search') {
      const { origin, destination, date, preference } = context;
      
      // Validate all inputs using backend API
      const validOrigin = await validateCityCode(origin);
      const validDestination = await validateCityCode(destination);
      const validDate = validateDate(date);
      const validPreference = validatePreference(preference);
      
      if (!validOrigin) {
        return res.json({
          response: "I need a valid origin city. Please provide a city like Delhi, Mumbai, Bangalore, etc.",
          context: { ...context, step: 'search' }
        });
      }
      
      if (!validDestination) {
        return res.json({
          response: "I need a valid destination city. Please provide a city like Delhi, Mumbai, Bangalore, etc.",
          context: { ...context, step: 'search' }
        });
      }
      
      if (!validDate) {
        return res.json({
          response: "I didn't understand that date format. Please try one of these:\n• 25 Dec 2025\n• 25/12/2025\n• 2025-12-25\n• Tomorrow\n• Next Monday\n• December 25, 2025\n\nMake sure it's a future date!",
          context: { ...context, step: 'search' }
        });
      }
      
      if (!validPreference) {
        return res.json({
          response: "Please choose your preference: price, time, or convenience.",
          context: { ...context, step: 'search' }
        });
      }
      
      // Search flights using Amadeus API
      const flights = await searchFlightsWithAmadeus(validOrigin.code, validDestination.code, validDate);
      const topFlights = rankFlights(flights);
      
      // Format response
      const response = `Here are the top 3 flights from ${validOrigin.name} to ${validDestination.name} on ${moment(validDate).format('DD MMM YYYY')}:\n\n` +
        topFlights.map((flight, index) => 
          `${index + 1}. **${flight.airline}** - ₹${flight.price.toLocaleString()}\n` +
          `   ${flight.category}: ${flight.reason}\n` +
          `   Departure: ${flight.departureTime} | Arrival: ${flight.arrivalTime}\n` +
          `   Duration: ${Math.floor(flight.duration / 60)}h ${flight.duration % 60}m\n` +
          `   ${flight.stops > 0 ? `${flight.stops} stop(s)` : 'Direct flight'}`
        ).join('\n\n') +
        `\n\nWhich flight interests you most? I can provide more details or help you with the next steps!`;
      
      return res.json({
        response,
        context: { step: 'complete', flights: topFlights }
      });
    }
    
    // Initial conversation flow - if user hasn't started the flow yet, start it
    if (!context || context.step === 'initial') {
      return res.json({
        response: `✈️ Hi! I'm your flight booking assistant. I can help you find the best flights in India.

Try saying:
• "search flights"
• "Delhi to Mumbai tomorrow"  
• "book flight Bangalore to Chennai next week"
• "cheap flights from Delhi to Goa"

Or just tell me where you want to go!`,
        context: { step: 'collecting', origin: null, destination: null, date: null, preference: null },
        actions: ['Search flights', 'Delhi to Mumbai', 'Bangalore to Chennai', 'Mumbai to Goa']
      });
    }
    
    // Handle step-by-step input collection
    if (context && context.step === 'collecting') {
      if (!context.origin) {
        // Enhanced city matching with fuzzy search using backend API
        const originMatch = await findCityMatch(message);
        
        if (originMatch) {
          return res.json({
            response: `Great! Flying from ${originMatch.name} (${originMatch.airportName}). Where would you like to go?`,
            context: { ...context, origin: originMatch.code, step: 'collecting' }
          });
        } else {
          // Provide helpful suggestions
          const suggestions = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'];
          return res.json({
            response: `I didn't recognize that city. Please try one of these major cities:\n\n${suggestions.map(city => `• ${city}`).join('\n')}\n\nOr type the city name again.`,
            context: { ...context, step: 'collecting' },
            actions: suggestions
          });
        }
      }
      
      if (!context.destination) {
        // Enhanced destination matching with fuzzy search using backend API
        const destMatch = await findCityMatch(message);
        
        if (destMatch && destMatch.code !== context.origin) {
          return res.json({
            response: `Perfect! ${context.origin} to ${destMatch.name} (${destMatch.airportName}). When would you like to travel?`,
            context: { ...context, destination: destMatch.code, step: 'collecting' }
          });
        } else if (destMatch && destMatch.code === context.origin) {
          return res.json({
            response: "Please choose a different destination city. You can't fly from a city to itself!",
            context: { ...context, step: 'collecting' }
          });
        } else {
          // Provide helpful suggestions
          const suggestions = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'];
          
          return res.json({
            response: `I didn't recognize that city. Please try one of these destinations:\n\n${suggestions.map(city => `• ${city}`).join('\n')}\n\nOr type the city name again.`,
            context: { ...context, step: 'collecting' },
            actions: suggestions
          });
        }
      }
      
      if (!context.date) {
        // Try to validate the entire message as a date
        const validDate = validateDate(message);
        if (validDate) {
          // Check if this was an inferred date (partial date input)
          const isInferredDate = isPartialDateInput(message);
          if (isInferredDate) {
            // Show confirmation for inferred dates
            const formattedDate = moment(validDate).format('DD MMM YYYY');
            const alternatives = generateAlternativeDates(validDate);
            
            return res.json({
              response: `I understood "${message}" as ${formattedDate}. Is this correct?\n\n${alternatives}\n\nYou can tap an option below:`,
              context: { 
                ...context, 
                inferredDate: validDate,
                originalInput: message,
                step: 'date_confirmation',
                alternatives: alternatives
              },
              actions: generateAlternativeOptions(validDate)
            });
          } else {
            // Direct date match - no confirmation needed
            return res.json({
              response: `Got it! Travel date: ${moment(validDate).format('DD MMM YYYY')}. What's most important to you: price, time, or convenience?`,
              context: { ...context, date: validDate, step: 'collecting' }
            });
          }
        }
        return res.json({
          response: "I didn't understand that date. Please try something like 'tomorrow', 'next Monday', '25 Dec', '25' (for 25th of current/next month), or '2025-12-25'. Make sure it's a future date!",
          context: { ...context, step: 'collecting' }
        });
      }
      
      // Handle date confirmation step
      if (context.step === 'date_confirmation') {
        if (lowerMessage.includes('yes') || lowerMessage.includes('correct') || lowerMessage.includes('right') || lowerMessage.includes('confirm')) {
          // User confirmed the inferred date
          return res.json({
            response: `Perfect! Travel date confirmed: ${moment(context.inferredDate).format('DD MMM YYYY')}. What's most important to you: price, time, or convenience?`,
            context: { 
              ...context, 
              date: context.inferredDate, 
              step: 'collecting',
              inferredDate: undefined,
              originalInput: undefined,
              alternatives: undefined
            }
          });
        } else if (lowerMessage.includes('no') || lowerMessage.includes('wrong') || lowerMessage.includes('incorrect')) {
          // User rejected the inferred date
          return res.json({
            response: `No problem! Please specify the correct date. You can use formats like:\n• "25 Dec 2025"\n• "tomorrow"\n• "next Monday"\n• Or any other date format you prefer.`,
            context: { 
              ...context, 
              step: 'collecting',
              inferredDate: undefined,
              originalInput: undefined,
              alternatives: undefined
            }
          });
        } else {
          // User provided a different date
          const newDate = validateDate(message);
          if (newDate) {
            return res.json({
              response: `Got it! Travel date: ${moment(newDate).format('DD MMM YYYY')}. What's most important to you: price, time, or convenience?`,
              context: { 
                ...context, 
                date: newDate, 
                step: 'collecting',
                inferredDate: undefined,
                originalInput: undefined,
                alternatives: undefined
              }
            });
          } else {
            // Offer actions again to reduce typing
            const actions = context.inferredDate ? generateAlternativeOptions(context.inferredDate) : ['Tomorrow', 'Next Monday'];
            return res.json({
              response: `I didn't understand that date. Please choose one of the options below, or type a date in formats like 25 Dec 2025, tomorrow, next Monday.`,
              context: { ...context, step: 'date_confirmation' },
              actions
            });
          }
        }
      }
      
      if (!context.preference) {
        // More flexible preference matching
        const prefMatch = ['price', 'time', 'convenience'].find(p => 
          lowerMessage.includes(p) || 
          (p === 'price' && (lowerMessage.includes('cheap') || lowerMessage.includes('budget') || lowerMessage.includes('cost'))) ||
          (p === 'time' && (lowerMessage.includes('fast') || lowerMessage.includes('quick') || lowerMessage.includes('speed'))) ||
          (p === 'convenience' && (lowerMessage.includes('comfort') || lowerMessage.includes('easy') || lowerMessage.includes('direct')))
        );
        if (prefMatch) {
          // Automatically trigger the search when preference is set
          const { origin, destination, date, preference } = { ...context, preference: prefMatch };
          
          // Validate all inputs
          const validOrigin = validateCityCode(origin);
          const validDestination = validateCityCode(destination);
          const validDate = validateDate(date);
          const validPreference = validatePreference(preference);
          
          if (!validOrigin || !validDestination || !validDate || !validPreference) {
            return res.json({
              response: "I need all the information to search flights. Let me start over.",
              context: { step: 'collecting', origin: null, destination: null, date: null, preference: null }
            });
          }
          
          // Search flights using Amadeus API
          const flights = await searchFlightsWithAmadeus(validOrigin.code, validDestination.code, validDate);
          const topFlights = rankFlights(flights);
          
          // Format response with enhanced flight cards
          const response = `Here are the top 3 flights from ${validOrigin.name} to ${validDestination.name} on ${moment(validDate).format('DD MMM YYYY')}:\n\n` +
            topFlights.map((flight, index) => 
              `${index + 1}. **${flight.airline}** - ₹${flight.price.toLocaleString()}\n` +
              `   ${flight.category}: ${flight.reason}\n` +
              `   Departure: ${flight.departureTime} | Arrival: ${flight.arrivalTime}\n` +
              `   Duration: ${Math.floor(flight.duration / 60)}h ${flight.duration % 60}m\n` +
              `   ${flight.stops > 0 ? `${flight.stops} stop(s)` : 'Direct flight'}`
            ).join('\n\n') +
            `\n\nWhich flight interests you most? I can provide more details or help you with the next steps!`;
          
          return res.json({
            response,
            context: { step: 'complete', flights: topFlights },
            flight_cards: topFlights.map(flight => ({
              id: flight.id,
              airline: flight.airline,
              price: flight.price,
              currency: flight.currency,
              departureTime: flight.departureTime,
              arrivalTime: flight.arrivalTime,
              duration: flight.duration,
              stops: flight.stops,
              category: flight.category,
              reason: flight.reason,
              flightNumber: flight.flightNumber || 'N/A',
              aircraft: flight.aircraft || 'N/A',
              bookable: true
            })),
            actions: ['Book Flight 1', 'Book Flight 2', 'Book Flight 3', 'Search again', 'Change dates']
          });
        } else {
          return res.json({
            response: `What's most important to you when choosing a flight?

💰 **Cheapest** - Lowest price flights
⚡ **Fastest** - Shortest travel time  
🎯 **Best Schedule** - Optimal departure times, fewer stops

Choose your preference:`,
            context: { ...context, step: 'collecting' },
            actions: ['💰 Cheapest', '⚡ Fastest', '🎯 Best Schedule']
          });
        }
      }
    }
    
    // Default response
    return res.json({
      response: "Hello! I'm your flight search assistant. I can help you find the best domestic flights in India. Just say 'search flights' to get started!",
      context: { step: 'initial' }
    });
    
  } catch (error) {
    console.error('Error processing chat:', error);
    console.error('Error details:', {
      message: error.message,
      stack: error.stack,
      userInput: message,
      context: context
    });
    
    // Return more helpful error message
    res.status(500).json({ 
      response: "I encountered an error processing your request. Please try again with a different format, or contact support if the issue persists.",
      context: { step: 'error', error: error.message }
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Flight search API is running' });
});

app.listen(PORT, () => {
  console.log(`Flight search server running on port ${PORT}`);
});
