/**
 * Airline data and utilities
 */

const AIRLINES = {
  'AI': { name: 'Air India', color: '#FF6B35', logo: '🇮🇳' },
  '6E': { name: 'IndiGo', color: '#FF6B00', logo: '✈️' },
  'SG': { name: 'SpiceJet', color: '#FF1744', logo: '🌶️' },
  'G8': { name: 'GoAir', color: '#00BCD4', logo: '🚀' },
  'IX': { name: 'Air India Express', color: '#FF9800', logo: '✈️' },
  '9W': { name: 'Jet Airways', color: '#2196F3', logo: '✈️' },
  'UK': { name: 'Vistara', color: '#9C27B0', logo: '👑' },
  'SG': { name: 'SpiceJet', color: '#E91E63', logo: '🌶️' },
  'I5': { name: 'AirAsia India', color: '#FF5722', logo: '🔥' },
  'QP': { name: 'Alliance Air', color: '#607D8B', logo: '✈️' },
  'EM': { name: 'Emirates', color: '#FFC107', logo: '🛫' },
  'EK': { name: 'Emirates', color: '#FFC107', logo: '🛫' },
  'QR': { name: 'Qatar Airways', color: '#8BC34A', logo: '🌍' },
  'SQ': { name: 'Singapore Airlines', color: '#3F51B5', logo: '🇸🇬' },
  'BA': { name: 'British Airways', color: '#1976D2', logo: '🇬🇧' },
  'LH': { name: 'Lufthansa', color: '#FF9800', logo: '🇩🇪' },
  'AF': { name: 'Air France', color: '#2196F3', logo: '🇫🇷' },
  'KL': { name: 'KLM', color: '#4CAF50', logo: '🇳🇱' },
  'AA': { name: 'American Airlines', color: '#E91E63', logo: '🇺🇸' },
  'DL': { name: 'Delta', color: '#FF5722', logo: '🇺🇸' },
  'UA': { name: 'United Airlines', color: '#9C27B0', logo: '🇺🇸' }
};

class AirlineUtils {
  /**
   * Get airline information by IATA code
   * @param {string} code - IATA airline code
   * @returns {Object} - Airline information
   */
  static getAirlineInfo(code) {
    return AIRLINES[code] || {
      name: code,
      color: '#607D8B',
      logo: '✈️'
    };
  }

  /**
   * Get airline color for UI
   * @param {string} code - IATA airline code
   * @returns {string} - Hex color code
   */
  static getAirlineColor(code) {
    return this.getAirlineInfo(code).color;
  }

  /**
   * Get airline name
   * @param {string} code - IATA airline code
   * @returns {string} - Airline name
   */
  static getAirlineName(code) {
    return this.getAirlineInfo(code).name;
  }

  /**
   * Get airline logo/emoji
   * @param {string} code - IATA airline code
   * @returns {string} - Emoji or symbol
   */
  static getAirlineLogo(code) {
    return this.getAirlineInfo(code).logo;
  }

  /**
   * Check if airline is Indian carrier
   * @param {string} code - IATA airline code
   * @returns {boolean} - True if Indian carrier
   */
  static isIndianCarrier(code) {
    const indianCarriers = ['AI', '6E', 'SG', 'G8', 'IX', '9W', 'UK', 'I5', 'QP'];
    return indianCarriers.includes(code);
  }

  /**
   * Get all available airlines
   * @returns {Array} - Array of airline objects
   */
  static getAllAirlines() {
    return Object.entries(AIRLINES).map(([code, info]) => ({
      code,
      ...info
    }));
  }
}

module.exports = AirlineUtils;
