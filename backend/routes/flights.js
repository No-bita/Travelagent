/**
 * Flights API routes
 * Clean, testable endpoint for flight search
 */

const express = require('express');
const moment = require('moment');
const router = express.Router();

const amadeusClient = require('../services/amadeusClient');
const mockFlights = require('../services/mockFlights');
const rankingService = require('../services/ranking');
const cityValidation = require('../services/cityValidation');
const logger = require('../utils/logger');

/**
 * POST /api/flights/search
 * Search for flights with comprehensive validation and ranking
 */
router.post('/search', async (req, res, next) => {
  try {
    const { origin, destination, date, adults = 1 } = req.body || {};

    if (!origin || !destination || !date) {
      return res.status(400).json({
        error: 'BadRequest',
        message: 'origin, destination, and date are required',
      });
    }

    logger.info(`Flight search request: ${origin} → ${destination} on ${date}`);

    // Validate cities in parallel for better performance
    const [validOrigin, validDestination] = await Promise.all([
      cityValidation.validateCity(origin),
      cityValidation.validateCity(destination),
    ]);

    if (!validOrigin) {
      return res.status(400).json({ 
        error: 'InvalidOrigin',
        message: `City "${origin}" not recognized. Please try a major Indian city.`,
        suggestions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']
      });
    }
    
    if (!validDestination) {
      return res.status(400).json({ 
        error: 'InvalidDestination',
        message: `City "${destination}" not recognized. Please try a major Indian city.`,
        suggestions: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']
      });
    }

    // Enhanced date parsing with comprehensive format support
    let d;
    
    // Handle relative dates first
    if (date.toLowerCase() === 'tomorrow') {
      d = moment().add(1, 'day');
    } else if (date.toLowerCase() === 'today') {
      d = moment();
    } else {
      // Parse various date formats
      d = moment(date, [
        'YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'MM/DD/YYYY',
        'DD MMM YYYY', 'DD MMMM YYYY', 'MMM DD, YYYY', 'MMMM DD, YYYY',
        'DD-MM-YY', 'DD/MM/YY', 'MM/DD/YY', 'YYYY/MM/DD',
        'DD.MM.YYYY', 'MM-DD-YYYY', 'DD-MMM-YYYY'
      ], true);
    }

    if (!d.isValid() || d.isBefore(moment(), 'day')) {
      return res.status(400).json({ 
        error: 'InvalidDate',
        message: 'Please provide a valid future date',
        examples: ['tomorrow', '25 Dec 2025', '2025-12-25', 'next Monday']
      });
    }

    const iso = d.format('YYYY-MM-DD');

    // Search flights with enhanced error handling
    let flights = [];
    let searchStartTime = Date.now();
    let fallbackUsed = false;
    let errorContext = null;
    
    try {
      if (amadeusClient.isAvailable()) {
        logger.info('Using Amadeus API for flight search');
        flights = await amadeusClient.searchFlights(
          validOrigin.code,
          validDestination.code,
          iso,
          { adults, max: 20 }
        );
      } else {
        logger.info('Amadeus API not available, using mock data');
        flights = mockFlights.generateMockFlights(
          validOrigin.code,
          validDestination.code,
          iso,
          15
        );
        fallbackUsed = true;
      }
    } catch (error) {
      logger.warn('Flight search failed, falling back to mock data:', error.message);
      errorContext = error.message;
      flights = mockFlights.generateMockFlights(
        validOrigin.code,
        validDestination.code,
        iso,
        15
      );
      fallbackUsed = true;
    }

    if (!flights || flights.length === 0) {
      return res.status(404).json({
        error: 'NoFlightsFound',
        message: `No flights available from ${validOrigin.name} to ${validDestination.name} on ${d.format('DD MMM YYYY')}`,
        suggestions: [
          'Try a different date',
          'Check alternative nearby airports',
          'Contact customer support for assistance'
        ]
      });
    }

    // Rank flights
    const topFlights = rankingService.rankFlights(flights);
    const processingTime = Date.now() - searchStartTime;

    // Enhanced response structure with metadata
    const response = {
      source: amadeusClient.isAvailable() && !fallbackUsed ? 'amadeus' : 'mock',
      query: {
        origin: validOrigin.code,
        destination: validDestination.code,
        date: iso,
        adults,
      },
      flights: topFlights.map(flight => ({
        ...flight,
        // Enhanced flight data
        layoverTime: flight.layoverTime || 0,
        aircraft: flight.aircraft || 'Unknown',
        confidence: flight.confidence || 0.8,
        badges: flight.badges || [],
        // Additional metadata
        searchTimestamp: new Date().toISOString(),
        dataSource: amadeusClient.isAvailable() && !fallbackUsed ? 'amadeus' : 'mock'
      })),
      meta: {
        originName: validOrigin.name,
        destinationName: validDestination.name,
        readableDate: d.format('DD MMM YYYY'),
        totalFlights: topFlights.length,
        processingTime: processingTime,
        fallbackUsed: fallbackUsed,
        errorContext: errorContext,
        searchTimestamp: new Date().toISOString()
      },
    };

    // Add error context header if fallback was used
    if (fallbackUsed) {
      res.set('X-Fallback-Reason', errorContext || 'API unavailable');
    }

    return res.json(response);

  } catch (err) {
    logger.error('Flight search error', { message: err.message, stack: err.stack });
    next(err);
  }
});

/**
 * GET /api/flights/mock?origin=DEL&destination=BOM&date=2025-12-25
 * Mock flights endpoint for testing
 */
router.get('/mock', (req, res) => {
  try {
    const { origin = 'DEL', destination = 'BOM', date } = req.query;
    const iso = date || moment().add(7, 'days').format('YYYY-MM-DD');
    const flights = mockFlights.generateMockFlights(origin, destination, iso);
    
    res.json({ 
      source: 'mock', 
      flights,
      query: { origin, destination, date: iso }
    });
  } catch (error) {
    logger.error('Mock flights error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to generate mock flights'
    });
  }
});

/**
 * GET /api/flights/airlines
 * Get available airlines
 */
router.get('/airlines', (req, res) => {
  try {
    const AirlineUtils = require('../utils/airlines');
    const airlines = AirlineUtils.getAllAirlines();
    
    res.json({
      success: true,
      airlines,
      total: airlines.length
    });
  } catch (error) {
    logger.error('Error fetching airlines:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch airline information'
    });
  }
});

/**
 * GET /api/flights/health
 * Health check for flights service
 */
router.get('/health', (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      amadeus: amadeusClient.isAvailable() ? 'available' : 'unavailable',
      mock: 'available',
      ranking: 'available',
      cityValidation: 'available'
    },
    cache: cityValidation.getCacheStats()
  };
  
  res.json(health);
});

module.exports = router;
