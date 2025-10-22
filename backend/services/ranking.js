/**
 * Flight ranking and scoring service
 */

const logger = require('../utils/logger');

class RankingService {
  constructor() {
    this.weights = {
      price: 0.4,
      duration: 0.3,
      convenience: 0.2,
      reliability: 0.1
    };
  }

  /**
   * Rank flights based on preference
   * @param {Array} flights - Array of flight offers
   * @param {string} preference - User preference (price, time, convenience)
   * @returns {Array} - Ranked flights
   */
  rankFlights(flights, preference = 'price') {
    if (!Array.isArray(flights) || flights.length === 0) {
      return [];
    }

    logger.info(`Ranking ${flights.length} flights by ${preference} preference`);

    // Calculate scores for each flight
    const scoredFlights = flights.map(flight => ({
      ...flight,
      score: this._calculateScore(flight, preference),
      ranking: this._calculateRanking(flight, flights, preference)
    }));

    // Sort by score (higher is better)
    const rankedFlights = scoredFlights.sort((a, b) => b.score - a.score);

    // Add ranking metadata
    return rankedFlights.map((flight, index) => ({
      ...flight,
      rank: index + 1,
      isTopChoice: index < 3,
      badges: this._generateBadges(flight, rankedFlights)
    }));
  }

  /**
   * Calculate overall score for a flight
   * @param {Object} flight - Flight offer
   * @param {string} preference - User preference
   * @returns {number} - Score (0-100)
   */
  _calculateScore(flight, preference) {
    const priceScore = this._calculatePriceScore(flight);
    const durationScore = this._calculateDurationScore(flight);
    const convenienceScore = this._calculateConvenienceScore(flight);
    const reliabilityScore = this._calculateReliabilityScore(flight);

    // Adjust weights based on preference
    const adjustedWeights = this._getAdjustedWeights(preference);

    const score = (
      priceScore * adjustedWeights.price +
      durationScore * adjustedWeights.duration +
      convenienceScore * adjustedWeights.convenience +
      reliabilityScore * adjustedWeights.reliability
    );

    return Math.round(score * 100) / 100;
  }

  /**
   * Calculate price score (lower price = higher score)
   * @param {Object} flight - Flight offer
   * @returns {number} - Price score (0-1)
   */
  _calculatePriceScore(flight) {
    const price = parseFloat(flight.price.total);
    if (!price || price <= 0) return 0;

    // Normalize price score (inverse relationship)
    // Assuming price range of ₹2000-₹50000
    const normalizedPrice = Math.max(0, Math.min(1, (50000 - price) / 48000));
    return normalizedPrice;
  }

  /**
   * Calculate duration score (shorter duration = higher score)
   * @param {Object} flight - Flight offer
   * @returns {number} - Duration score (0-1)
   */
  _calculateDurationScore(flight) {
    const duration = flight.itineraries[0]?.duration;
    if (!duration) return 0;

    const durationMinutes = this._parseDurationToMinutes(duration);
    if (durationMinutes <= 0) return 0;

    // Normalize duration score (inverse relationship)
    // Assuming duration range of 1-8 hours
    const normalizedDuration = Math.max(0, Math.min(1, (480 - durationMinutes) / 420));
    return normalizedDuration;
  }

  /**
   * Calculate convenience score
   * @param {Object} flight - Flight offer
   * @returns {number} - Convenience score (0-1)
   */
  _calculateConvenienceScore(flight) {
    let score = 0.5; // Base score

    // Direct flights are more convenient
    const segments = flight.itineraries[0]?.segments || [];
    if (segments.length === 1) {
      score += 0.3; // Direct flight bonus
    } else if (segments.length === 2) {
      score += 0.1; // One stop is acceptable
    }

    // Morning/evening flights are more convenient
    const departureTime = this._getDepartureTime(flight);
    if (departureTime) {
      const hour = departureTime.getHours();
      if (hour >= 6 && hour <= 10) {
        score += 0.2; // Morning flights
      } else if (hour >= 17 && hour <= 21) {
        score += 0.1; // Evening flights
      }
    }

    return Math.min(1, score);
  }

  /**
   * Calculate reliability score
   * @param {Object} flight - Flight offer
   * @returns {number} - Reliability score (0-1)
   */
  _calculateReliabilityScore(flight) {
    let score = 0.5; // Base score

    // Major airlines are more reliable
    const carrierCode = flight.validatingAirlineCodes?.[0];
    if (carrierCode) {
      const majorAirlines = ['AI', '6E', 'SG', '9W', 'UK'];
      if (majorAirlines.includes(carrierCode)) {
        score += 0.3;
      }
    }

    // Direct flights are more reliable
    const segments = flight.itineraries[0]?.segments || [];
    if (segments.length === 1) {
      score += 0.2;
    }

    return Math.min(1, score);
  }

  /**
   * Get adjusted weights based on preference
   * @param {string} preference - User preference
   * @returns {Object} - Adjusted weights
   */
  _getAdjustedWeights(preference) {
    const baseWeights = { ...this.weights };
    
    switch (preference.toLowerCase()) {
      case 'price':
        return {
          price: 0.7,
          duration: 0.2,
          convenience: 0.05,
          reliability: 0.05
        };
      case 'time':
        return {
          price: 0.2,
          duration: 0.6,
          convenience: 0.15,
          reliability: 0.05
        };
      case 'convenience':
        return {
          price: 0.2,
          duration: 0.2,
          convenience: 0.5,
          reliability: 0.1
        };
      default:
        return baseWeights;
    }
  }

  /**
   * Calculate ranking position
   * @param {Object} flight - Flight offer
   * @param {Array} allFlights - All flights
   * @param {string} preference - User preference
   * @returns {Object} - Ranking information
   */
  _calculateRanking(flight, allFlights, preference) {
    const price = parseFloat(flight.price.total);
    const duration = this._parseDurationToMinutes(flight.itineraries[0]?.duration);
    const segments = flight.itineraries[0]?.segments || [];

    const rankings = {
      price: this._getPriceRanking(price, allFlights),
      duration: this._getDurationRanking(duration, allFlights),
      direct: segments.length === 1,
      cheapest: false,
      fastest: false,
      mostConvenient: false
    };

    // Determine special rankings
    rankings.cheapest = rankings.price === 1;
    rankings.fastest = rankings.duration === 1;
    rankings.mostConvenient = this._isMostConvenient(flight, allFlights);

    return rankings;
  }

  /**
   * Get price ranking
   * @param {number} price - Flight price
   * @param {Array} allFlights - All flights
   * @returns {number} - Price rank (1 = cheapest)
   */
  _getPriceRanking(price, allFlights) {
    const prices = allFlights
      .map(f => parseFloat(f.price.total))
      .filter(p => p > 0)
      .sort((a, b) => a - b);
    
    return prices.indexOf(price) + 1;
  }

  /**
   * Get duration ranking
   * @param {number} duration - Flight duration in minutes
   * @param {Array} allFlights - All flights
   * @returns {number} - Duration rank (1 = fastest)
   */
  _getDurationRanking(duration, allFlights) {
    const durations = allFlights
      .map(f => this._parseDurationToMinutes(f.itineraries[0]?.duration))
      .filter(d => d > 0)
      .sort((a, b) => a - b);
    
    return durations.indexOf(duration) + 1;
  }

  /**
   * Check if flight is most convenient
   * @param {Object} flight - Flight offer
   * @param {Array} allFlights - All flights
   * @returns {boolean} - True if most convenient
   */
  _isMostConvenient(flight, allFlights) {
    const segments = flight.itineraries[0]?.segments || [];
    const departureTime = this._getDepartureTime(flight);
    
    // Direct flights with good timing are most convenient
    if (segments.length === 1 && departureTime) {
      const hour = departureTime.getHours();
      return hour >= 6 && hour <= 10; // Morning flights
    }
    
    return false;
  }

  /**
   * Generate badges for flight
   * @param {Object} flight - Flight offer
   * @param {Array} allFlights - All flights
   * @returns {Array} - Array of badge objects
   */
  _generateBadges(flight, allFlights) {
    const badges = [];
    const rankings = flight.ranking;

    if (rankings.cheapest) {
      badges.push({ type: 'cheapest', label: 'Cheapest', color: '#4CAF50' });
    }
    
    if (rankings.fastest) {
      badges.push({ type: 'fastest', label: 'Fastest', color: '#2196F3' });
    }
    
    if (rankings.direct) {
      badges.push({ type: 'direct', label: 'Direct', color: '#FF9800' });
    }
    
    if (rankings.mostConvenient) {
      badges.push({ type: 'convenient', label: 'Most Convenient', color: '#9C27B0' });
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
   * Get departure time from flight
   * @param {Object} flight - Flight offer
   * @returns {Date|null} - Departure time
   */
  _getDepartureTime(flight) {
    const segment = flight.itineraries[0]?.segments?.[0];
    if (!segment?.departure?.at) return null;
    
    return new Date(segment.departure.at);
  }
}

module.exports = new RankingService();
