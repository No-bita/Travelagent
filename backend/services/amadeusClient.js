/**
 * Amadeus API client service
 * Enhanced with better error handling and data processing
 */

const Amadeus = require('amadeus');
const moment = require('moment');
const logger = require('../utils/logger');
const AirlineUtils = require('../utils/airlines');

class AmadeusClient {
  constructor() {
    this.client = null;
    this.isInitialized = false;
    this.initialize();
  }

  /**
   * Initialize Amadeus client
   */
  initialize() {
    try {
      if (process.env.AMADEUS_CLIENT_ID && process.env.AMADEUS_CLIENT_SECRET) {
        this.client = new Amadeus({
          clientId: process.env.AMADEUS_CLIENT_ID,
          clientSecret: process.env.AMADEUS_CLIENT_SECRET
        });
        this.isInitialized = true;
        logger.info('Amadeus API client initialized successfully');
      } else {
        logger.warn('Amadeus API credentials not found - using mock data mode');
      }
    } catch (error) {
      logger.error('Failed to initialize Amadeus client:', error);
    }
  }

  /**
   * Check if Amadeus client is available
   * @returns {boolean} - True if client is initialized
   */
  isAvailable() {
    return this.isInitialized && this.client !== null;
  }

  /**
   * Search flights using Amadeus API with enhanced error handling
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date (YYYY-MM-DD)
   * @param {Object} options - Additional search options
   * @returns {Array} - Array of processed flight offers
   */
  async searchFlights(origin, destination, date, options = {}) {
    if (!this.isAvailable()) {
      logger.warn('Amadeus client not available, using mock data');
      return this._getMockFlights(origin, destination, date, options);
    }

    try {
      logger.info(`Searching Amadeus flights: ${origin} → ${destination} on ${date}`);
      
      const searchParams = {
        originLocationCode: origin,
        destinationLocationCode: destination,
        departureDate: date,
        adults: options.adults || 1,
        max: options.max || 20,
        ...options
      };

      const response = await this.client.shopping.flightOffersSearch.get(searchParams);
      
      if (!response.data || !Array.isArray(response.data)) {
        logger.warn('No flight data received from Amadeus API');
        return this._getMockFlights(origin, destination, date, options);
      }

      // Enhanced data processing with layover calculation
      const processedFlights = this._processFlightData(response.data, origin, destination);
      logger.info(`Found ${processedFlights.length} flights from Amadeus API`);
      return processedFlights;

    } catch (error) {
      logger.error('Amadeus API search failed:', error);
      
      // Handle specific error types
      if (error.code === 429) {
        logger.warn('Rate limit hit, waiting before fallback');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      
      return this._getMockFlights(origin, destination, date, options);
    }
  }

  /**
   * Get flight offer details
   * @param {string} offerId - Flight offer ID
   * @returns {Object} - Flight offer details
   */
  async getFlightOffer(offerId) {
    if (!this.isAvailable()) {
      throw new Error('Amadeus client not initialized');
    }

    try {
      const response = await this.client.shopping.flightOffers.get({
        id: offerId
      });

      return response.data;
    } catch (error) {
      logger.error('Failed to get flight offer details:', error);
      throw error;
    }
  }

  /**
   * Get airport information
   * @param {string} airportCode - Airport IATA code
   * @returns {Object} - Airport information
   */
  async getAirportInfo(airportCode) {
    if (!this.isAvailable()) {
      throw new Error('Amadeus client not initialized');
    }

    try {
      const response = await this.client.referenceData.locations.get({
        keyword: airportCode,
        subType: 'AIRPORT'
      });

      return response.data;
    } catch (error) {
      logger.error('Failed to get airport info:', error);
      throw error;
    }
  }

  /**
   * Get airline information
   * @param {string} airlineCode - Airline IATA code
   * @returns {Object} - Airline information
   */
  async getAirlineInfo(airlineCode) {
    if (!this.isAvailable()) {
      throw new Error('Amadeus client not initialized');
    }

    try {
      const response = await this.client.referenceData.airlines.get({
        airlineCodes: airlineCode
      });

      return response.data;
    } catch (error) {
      logger.error('Failed to get airline info:', error);
      throw error;
    }
  }

  /**
   * Process raw Amadeus flight data into standardized format
   * @param {Array} rawFlights - Raw flight data from Amadeus
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @returns {Array} - Processed flight data
   */
  _processFlightData(rawFlights, origin, destination) {
    return rawFlights.map((offer, index) => {
      const itinerary = offer.itineraries[0];
      const segments = itinerary.segments;
      const price = parseFloat(offer.price.total);
      const currency = offer.price.currency;

      const departureTime = moment(segments[0].departure.at);
      const arrivalTime = moment(segments[segments.length - 1].arrival.at);
      const duration = arrivalTime.diff(departureTime, 'minutes');
      const stops = segments.length - 1;

      const airlineCode = segments[0].carrierCode;
      const airlineName = AirlineUtils.getAirlineName(airlineCode);

      // Calculate layover time
      let totalLayover = 0;
      for (let i = 0; i < segments.length - 1; i++) {
        const arrival = moment(segments[i].arrival.at);
        const departure = moment(segments[i + 1].departure.at);
        totalLayover += departure.diff(arrival, 'minutes');
      }

      return {
        id: `AM${index + 1}`,
        airline: airlineName,
        airlineCode,
        price: Math.round(price),
        duration,
        departureTime: departureTime.format('HH:mm'),
        arrivalTime: arrivalTime.format('HH:mm'),
        departureDate: departureTime.format('YYYY-MM-DD'),
        arrivalDate: arrivalTime.format('YYYY-MM-DD'),
        origin,
        destination,
        stops,
        layoverTime: totalLayover,
        currency,
        flightNumber: segments[0].number,
        aircraft: segments[0].aircraft?.code || 'Unknown',
        // Preserve original Amadeus structure for compatibility
        originalData: offer,
        // Enhanced metadata
        badges: this._generateFlightBadges(price, duration, stops, index),
        confidence: 0.9 + Math.random() * 0.1,
        source: 'amadeus'
      };
    });
  }

  /**
   * Generate mock flights as fallback
   * @param {string} origin - Origin airport code
   * @param {string} destination - Destination airport code
   * @param {string} date - Departure date
   * @param {Object} options - Search options
   * @returns {Array} - Mock flight data
   */
  _getMockFlights(origin, destination, date, options = {}) {
    const mockFlights = require('./mockFlights');
    return mockFlights.generateMockFlights(origin, destination, date, options.max || 15);
  }

  /**
   * Generate flight badges based on characteristics
   * @param {number} price - Flight price
   * @param {number} duration - Flight duration in minutes
   * @param {number} stops - Number of stops
   * @param {number} index - Flight index
   * @returns {Array} - Array of badge objects
   */
  _generateFlightBadges(price, duration, stops, index) {
    const badges = [];
    
    if (stops === 0) {
      badges.push({ type: 'direct', label: 'Direct', color: '#4CAF50' });
    }
    
    if (index < 3) {
      badges.push({ type: 'top', label: 'Top Choice', color: '#2196F3' });
    }
    
    if (duration < 180) { // Less than 3 hours
      badges.push({ type: 'fast', label: 'Quick', color: '#FF9800' });
    }
    
    return badges;
  }

  /**
   * Check API rate limits and usage
   * @returns {Object} - Rate limit information
   */
  getRateLimitInfo() {
    // This would need to be implemented based on Amadeus API documentation
    // For now, return a placeholder
    return {
      remaining: 'unknown',
      resetTime: 'unknown'
    };
  }
}

module.exports = new AmadeusClient();
