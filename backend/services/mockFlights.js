/**
 * Mock flight data service
 * Provides fallback flight data when Amadeus API is unavailable
 */

const moment = require('moment');
const AirlineUtils = require('../utils/airlines');
const logger = require('../utils/logger');

class MockFlightsService {
  constructor() {
    // Indian airlines with readable names (best practice from provided code)
    this.airlines = [
      'IndiGo', 'Air India', 'SpiceJet', 'Vistara', 'GoAir', 'AirAsia India',
      'Jet Airways', 'Air India Express', 'Alliance Air', 'TruJet'
    ];
    
    // Airline codes for API compatibility
    this.airlineCodes = [
      '6E', 'AI', 'SG', 'UK', 'G8', 'I5', '9W', 'IX', '9I', '2T'
    ];
  }

  /**
   * Generate mock flight data with enhanced structure
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @param {number} count - Number of flights to generate
   * @returns {Array} - Array of mock flight offers
   */
  generateMockFlights(origin, destination, date, count = 15) {
    logger.info(`Generating ${count} mock flights for ${origin} → ${destination} on ${date}`);
    
    const flights = [];
    const basePrice = this._getBasePrice(origin, destination);
    
    for (let i = 0; i < count; i++) {
      const flight = this._createEnhancedMockFlight(origin, destination, date, basePrice, i);
      flights.push(flight);
    }
    
    return flights;
  }

  /**
   * Generate simple mock flights (best practice from provided code)
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @returns {Array} - Array of simple mock flights
   */
  generateSimpleMockFlights(origin, destination, date) {
    const flights = [];
    const numFlights = Math.floor(Math.random() * 6) + 10; // 10–15 flights

    for (let i = 0; i < numFlights; i++) {
      const airline = this.airlines[Math.floor(Math.random() * this.airlines.length)];
      const airlineCode = this.airlineCodes[Math.floor(Math.random() * this.airlineCodes.length)];
      const basePrice = Math.floor(Math.random() * 15000) + 3000; // ₹3000–₹18000
      const duration = Math.floor(Math.random() * 300) + 60; // 1–6 hours
      const departureHour = Math.floor(Math.random() * 24);
      const departureMinute = Math.floor(Math.random() * 60);

      const departureTime = moment(date).hour(departureHour).minute(departureMinute);
      const arrivalTime = moment(departureTime).add(duration, 'minutes');

      flights.push({
        id: `FL${i + 1}`,
        airline,
        airlineCode,
        price: basePrice,
        duration,
        departureTime: departureTime.format('HH:mm'),
        arrivalTime: arrivalTime.format('HH:mm'),
        departureDate: departureTime.format('YYYY-MM-DD'),
        arrivalDate: arrivalTime.format('YYYY-MM-DD'),
        origin,
        destination,
        stops: Math.random() > 0.7 ? 1 : 0,
        layoverTime: Math.random() > 0.7 ? Math.floor(Math.random() * 180) + 30 : 0,
        currency: 'INR',
        flightNumber: `${airlineCode}${Math.floor(Math.random() * 9999) + 1}`,
        source: 'mock'
      });
    }

    return flights;
  }

  /**
   * Create an enhanced mock flight with realistic data
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @param {number} basePrice - Base price for the route
   * @param {number} index - Flight index
   * @returns {Object} - Enhanced mock flight offer
   */
  _createEnhancedMockFlight(origin, destination, date, basePrice, index) {
    const airline = this.airlines[Math.floor(Math.random() * this.airlines.length)];
    const airlineInfo = AirlineUtils.getAirlineInfo(airline);
    
    const departureTime = this._generateDepartureTime(index);
    const duration = this._generateDuration(origin, destination);
    const price = this._generatePrice(basePrice, index);
    const stops = this._generateStops(index);
    
    // Calculate layover time for multi-segment flights
    let totalLayover = 0;
    if (stops > 0) {
      totalLayover = stops * 90; // 1.5 hours per stop
    }
    
    return {
      id: `mock_${Date.now()}_${index}`,
      airline: airlineInfo.name,
      airlineCode: airline,
      price: Math.round(price),
      duration: this._parseDurationToMinutes(duration),
      departureTime: departureTime,
      arrivalTime: this._calculateArrivalTime(departureTime, duration),
      departureDate: date,
      arrivalDate: date, // Simplified for mock
      origin,
      destination,
      stops,
      layoverTime: totalLayover,
      currency: 'INR',
      flightNumber: `${airline}${Math.floor(Math.random() * 9999) + 1}`,
      aircraft: '320',
      // Enhanced metadata
      badges: this._generateMockBadges(price, duration, stops, index),
      confidence: 0.85 + Math.random() * 0.15,
      source: 'mock',
      // Preserve original structure for compatibility
      type: 'flight-offer',
      instantTicketingRequired: false,
      nonHomogeneous: false,
      oneWay: true,
      lastTicketingDate: this._getLastTicketingDate(date),
      numberOfBookableSeats: Math.floor(Math.random() * 9) + 1,
      price: {
        currency: 'INR',
        total: Math.round(price).toString(),
        base: Math.floor(price * 0.8).toString(),
        fees: [
          {
            amount: Math.floor(price * 0.1).toString(),
            type: 'SUPPLIER'
          },
          {
            amount: Math.floor(price * 0.1).toString(),
            type: 'TICKETING'
          }
        ],
        grandTotal: Math.round(price).toString()
      },
      validatingAirlineCodes: [airline]
    };
  }

  /**
   * Create a single mock flight (legacy method for compatibility)
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @param {number} basePrice - Base price for the route
   * @param {number} index - Flight index
   * @returns {Object} - Mock flight offer
   */
  _createMockFlight(origin, destination, date, basePrice, index) {
    const airline = this.airlines[Math.floor(Math.random() * this.airlines.length)];
    const airlineInfo = AirlineUtils.getAirlineInfo(airline);
    
    const departureTime = this._generateDepartureTime(index);
    const duration = this._generateDuration(origin, destination);
    const price = this._generatePrice(basePrice, index);
    const stops = this._generateStops(index);
    
    return {
      id: `mock_${Date.now()}_${index}`,
      type: 'flight-offer',
      source: 'MOCK',
      instantTicketingRequired: false,
      nonHomogeneous: false,
      oneWay: true,
      lastTicketingDate: this._getLastTicketingDate(date),
      numberOfBookableSeats: Math.floor(Math.random() * 9) + 1,
      itineraries: [{
        duration: duration,
        segments: this._generateSegments(origin, destination, date, departureTime, stops)
      }],
      price: {
        currency: 'INR',
        total: price.toString(),
        base: Math.floor(price * 0.8).toString(),
        fees: [
          {
            amount: Math.floor(price * 0.1).toString(),
            type: 'SUPPLIER'
          },
          {
            amount: Math.floor(price * 0.1).toString(),
            type: 'TICKETING'
          }
        ],
        grandTotal: price.toString()
      },
      pricingOptions: {
        fareType: ['PUBLISHED'],
        includedCheckedBagsOnly: true
      },
      validatingAirlineCodes: [airline],
      travelerPricings: [{
        travelerId: '1',
        fareOption: 'STANDARD',
        travelerType: 'ADULT',
        price: {
          currency: 'INR',
          total: price.toString(),
          base: Math.floor(price * 0.8).toString()
        },
        fareDetailsBySegment: [{
          segmentId: '1',
          cabin: 'ECONOMY',
          fareBasis: 'Y',
          class: 'Y',
          includedCheckedBags: {
            weight: 15,
            weightUnit: 'KG'
          }
        }]
      }]
    };
  }

  /**
   * Generate departure time based on index (improved with moment.js)
   * @param {number} index - Flight index
   * @param {string} date - Departure date
   * @returns {string} - Departure time
   */
  _generateDepartureTime(index, date) {
    const baseHour = 6 + (index * 1.5) % 18; // Spread flights throughout the day
    const hour = Math.floor(baseHour);
    const minute = Math.floor((baseHour - hour) * 60);
    
    // Use moment.js for better date handling (best practice from provided code)
    const departureTime = moment(date).hour(hour).minute(minute);
    return departureTime.format('HH:mm');
  }

  /**
   * Generate flight duration based on route (improved with minutes)
   * @param {string} origin - Origin airport
   * @param {string} destination - Destination airport
   * @returns {number} - Flight duration in minutes
   */
  _generateDuration(origin, destination) {
    // Generate duration in minutes (best practice from provided code)
    const duration = Math.floor(Math.random() * 300) + 60; // 1–6 hours
    return duration;
  }

  /**
   * Generate price with variation (improved with realistic ranges)
   * @param {number} basePrice - Base price
   * @param {number} index - Flight index
   * @returns {number} - Generated price
   */
  _generatePrice(basePrice, index) {
    // Use realistic price range from provided code (₹3000–₹18000)
    const price = Math.floor(Math.random() * 15000) + 3000;
    return Math.max(price, 3000); // Minimum price of ₹3000
  }

  /**
   * Generate number of stops
   * @param {number} index - Flight index
   * @returns {number} - Number of stops
   */
  _generateStops(index) {
    // 70% direct flights, 30% with stops
    return Math.random() < 0.7 ? 0 : Math.floor(Math.random() * 2) + 1;
  }

  /**
   * Generate flight segments
   * @param {string} origin - Origin airport
   * @param {string} destination - Destination airport
   * @param {string} date - Departure date
   * @param {string} departureTime - Departure time
   * @param {number} stops - Number of stops
   * @returns {Array} - Flight segments
   */
  _generateSegments(origin, destination, date, departureTime, stops) {
    const segments = [];
    const departureDateTime = `${date}T${departureTime}:00`;
    
    if (stops === 0) {
      // Direct flight
      const arrivalDateTime = this._calculateArrivalTime(departureDateTime, this._generateDuration(origin, destination));
      segments.push({
        departure: {
          iataCode: origin,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: departureDateTime
        },
        arrival: {
          iataCode: destination,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: arrivalDateTime
        },
        carrierCode: this.airlines[Math.floor(Math.random() * this.airlines.length)],
        number: Math.floor(Math.random() * 9999) + 1,
        aircraft: {
          code: '320'
        },
        operating: {
          carrierCode: this.airlines[Math.floor(Math.random() * this.airlines.length)]
        },
        duration: this._generateDuration(origin, destination),
        id: '1'
      });
    } else {
      // Multi-segment flight
      const intermediateAirports = ['BOM', 'DEL', 'BLR', 'MAA', 'CCU', 'HYD'];
      const intermediate = intermediateAirports[Math.floor(Math.random() * intermediateAirports.length)];
      
      // First segment
      const firstArrival = this._calculateArrivalTime(departureDateTime, 'PT2H30M');
      segments.push({
        departure: {
          iataCode: origin,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: departureDateTime
        },
        arrival: {
          iataCode: intermediate,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: firstArrival
        },
        carrierCode: this.airlines[Math.floor(Math.random() * this.airlines.length)],
        number: Math.floor(Math.random() * 9999) + 1,
        aircraft: {
          code: '320'
        },
        duration: 'PT2H30M',
        id: '1'
      });
      
      // Second segment
      const secondDeparture = this._calculateArrivalTime(firstArrival, 'PT1H30M'); // 1.5 hour layover
      const secondArrival = this._calculateArrivalTime(secondDeparture, 'PT2H30M');
      segments.push({
        departure: {
          iataCode: intermediate,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: secondDeparture
        },
        arrival: {
          iataCode: destination,
          terminal: Math.floor(Math.random() * 3) + 1,
          at: secondArrival
        },
        carrierCode: this.airlines[Math.floor(Math.random() * this.airlines.length)],
        number: Math.floor(Math.random() * 9999) + 1,
        aircraft: {
          code: '320'
        },
        duration: 'PT2H30M',
        id: '2'
      });
    }
    
    return segments;
  }

  /**
   * Calculate arrival time
   * @param {string} departureTime - Departure time
   * @param {string} duration - Flight duration
   * @returns {string} - Arrival time
   */
  _calculateArrivalTime(departureTime, duration) {
    const departure = new Date(departureTime);
    const durationMatch = duration.match(/PT(\d+)H(\d+)M/);
    if (durationMatch) {
      const hours = parseInt(durationMatch[1]);
      const minutes = parseInt(durationMatch[2]);
      departure.setHours(departure.getHours() + hours);
      departure.setMinutes(departure.getMinutes() + minutes);
    }
    return departure.toISOString();
  }

  /**
   * Get base price for route
   * @param {string} origin - Origin airport
   * @param {string} destination - Destination airport
   * @returns {number} - Base price
   */
  _getBasePrice(origin, destination) {
    // Mock base prices for common Indian routes
    const routePrices = {
      'DEL-BOM': 8000, 'BOM-DEL': 8000,
      'DEL-BLR': 6000, 'BLR-DEL': 6000,
      'BOM-BLR': 5000, 'BLR-BOM': 5000,
      'DEL-MAA': 7000, 'MAA-DEL': 7000,
      'BOM-MAA': 4000, 'MAA-BOM': 4000
    };
    
    const route = `${origin}-${destination}`;
    return routePrices[route] || 5000; // Default price
  }

  /**
   * Generate mock badges for flights
   * @param {number} price - Flight price
   * @param {string} duration - Flight duration
   * @param {number} stops - Number of stops
   * @param {number} index - Flight index
   * @returns {Array} - Array of badge objects
   */
  _generateMockBadges(price, duration, stops, index) {
    const badges = [];
    const durationMinutes = this._parseDurationToMinutes(duration);
    
    if (stops === 0) {
      badges.push({ type: 'direct', label: 'Direct', color: '#4CAF50' });
    }
    
    if (index < 3) {
      badges.push({ type: 'top', label: 'Top Choice', color: '#2196F3' });
    }
    
    if (durationMinutes < 180) { // Less than 3 hours
      badges.push({ type: 'fast', label: 'Quick', color: '#FF9800' });
    }
    
    if (price < 5000) {
      badges.push({ type: 'cheap', label: 'Great Value', color: '#4CAF50' });
    }
    
    return badges;
  }

  /**
   * Parse duration string to minutes
   * @param {string} duration - Duration string (e.g., "PT2H30M")
   * @returns {number} - Duration in minutes
   */
  _parseDurationToMinutes(duration) {
    if (!duration) return 0;
    
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
    if (!match) return 0;
    
    const hours = parseInt(match[1] || 0);
    const minutes = parseInt(match[2] || 0);
    
    return hours * 60 + minutes;
  }

  /**
   * Calculate arrival time from departure time and duration
   * @param {string} departureTime - Departure time (HH:mm)
   * @param {string} duration - Flight duration
   * @returns {string} - Arrival time (HH:mm)
   */
  _calculateArrivalTime(departureTime, duration) {
    const [hours, minutes] = departureTime.split(':').map(Number);
    const durationMinutes = this._parseDurationToMinutes(duration);
    
    const totalMinutes = hours * 60 + minutes + durationMinutes;
    const arrivalHours = Math.floor(totalMinutes / 60) % 24;
    const arrivalMinutes = totalMinutes % 60;
    
    return `${arrivalHours.toString().padStart(2, '0')}:${arrivalMinutes.toString().padStart(2, '0')}`;
  }

  /**
   * Get last ticketing date
   * @param {string} date - Departure date
   * @returns {string} - Last ticketing date
   */
  _getLastTicketingDate(date) {
    const departureDate = new Date(date);
    departureDate.setDate(departureDate.getDate() - 1); // Day before departure
    return departureDate.toISOString().split('T')[0];
  }

  /**
   * Generate mock flights using best practices from provided code
   * This is a standalone function that can be used independently
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @returns {Array} - Array of mock flights
   */
  static generateMockFlights(origin, destination, date) {
    const airlines = ['IndiGo', 'Air India', 'SpiceJet', 'Vistara', 'GoAir', 'AirAsia India'];
    const flights = [];
    const numFlights = Math.floor(Math.random() * 6) + 10; // 10–15

    for (let i = 0; i < numFlights; i++) {
      const airline = airlines[Math.floor(Math.random() * airlines.length)];
      const basePrice = Math.floor(Math.random() * 15000) + 3000; // ₹3000–₹18000
      const duration = Math.floor(Math.random() * 300) + 60; // 1–6 hours
      const departureHour = Math.floor(Math.random() * 24);
      const departureMinute = Math.floor(Math.random() * 60);

      const departureTime = moment(date).hour(departureHour).minute(departureMinute);
      const arrivalTime = moment(departureTime).add(duration, 'minutes');

      flights.push({
        id: `FL${i + 1}`,
        airline,
        price: basePrice,
        duration,
        departureTime: departureTime.format('HH:mm'),
        arrivalTime: arrivalTime.format('HH:mm'),
        departureDate: departureTime.format('YYYY-MM-DD'),
        arrivalDate: arrivalTime.format('YYYY-MM-DD'),
        origin,
        destination,
        stops: Math.random() > 0.7 ? 1 : 0,
        layoverTime: Math.random() > 0.7 ? Math.floor(Math.random() * 180) + 30 : 0,
        currency: 'INR',
      });
    }

    return flights;
  }
}

module.exports = new MockFlightsService();
