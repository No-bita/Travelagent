/**
 * City validation and mapping service
 */

const axios = require('axios');
const logger = require('../utils/logger');

class CityValidationService {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Validate and get city information
   * @param {string} cityName - City name to validate
   * @returns {Object|null} - City info or null if invalid
   */
  async validateCity(cityName) {
    if (!cityName || typeof cityName !== 'string') {
      return null;
    }

    const normalizedName = cityName.trim().toLowerCase();
    
    // Check cache first
    if (this.cache.has(normalizedName)) {
      const cached = this.cache.get(normalizedName);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
      this.cache.delete(normalizedName);
    }

    try {
      // Try backend API first
      const cityInfo = await this._validateViaBackendAPI(normalizedName);
      if (cityInfo) {
        this._cacheResult(normalizedName, cityInfo);
        return cityInfo;
      }

      // Fallback to local mapping
      const localInfo = this._validateViaLocalMapping(normalizedName);
      if (localInfo) {
        this._cacheResult(normalizedName, localInfo);
        return localInfo;
      }

      return null;
    } catch (error) {
      logger.error('City validation error:', error);
      return null;
    }
  }

  /**
   * Validate city via backend API
   * @param {string} cityName - City name
   * @returns {Object|null} - City info or null
   */
  async _validateViaBackendAPI(cityName) {
    try {
      const response = await axios.get(`http://localhost:8000/api/cities/search`, {
        params: { q: cityName },
        timeout: 5000
      });

      if (response.data && response.data.length > 0) {
        const city = response.data[0];
        return {
          code: city.code,
          name: city.name,
          country: city.country,
          region: city.region
        };
      }
    } catch (error) {
      logger.debug('Backend API validation failed:', error.message);
    }
    return null;
  }

  /**
   * Validate city via local mapping
   * @param {string} cityName - City name
   * @returns {Object|null} - City info or null
   */
  _validateViaLocalMapping(cityName) {
    const cityMappings = {
      'delhi': { code: 'DEL', name: 'Delhi', country: 'India', region: 'North' },
      'mumbai': { code: 'BOM', name: 'Mumbai', country: 'India', region: 'West' },
      'bangalore': { code: 'BLR', name: 'Bangalore', country: 'India', region: 'South' },
      'chennai': { code: 'MAA', name: 'Chennai', country: 'India', region: 'South' },
      'kolkata': { code: 'CCU', name: 'Kolkata', country: 'India', region: 'East' },
      'hyderabad': { code: 'HYD', name: 'Hyderabad', country: 'India', region: 'South' },
      'pune': { code: 'PNQ', name: 'Pune', country: 'India', region: 'West' },
      'ahmedabad': { code: 'AMD', name: 'Ahmedabad', country: 'India', region: 'West' },
      'jaipur': { code: 'JAI', name: 'Jaipur', country: 'India', region: 'North' },
      'kochi': { code: 'COK', name: 'Kochi', country: 'India', region: 'South' },
      'goa': { code: 'GOI', name: 'Goa', country: 'India', region: 'West' },
      'chandigarh': { code: 'IXC', name: 'Chandigarh', country: 'India', region: 'North' },
      'lucknow': { code: 'LKO', name: 'Lucknow', country: 'India', region: 'North' },
      'bhubaneswar': { code: 'BBI', name: 'Bhubaneswar', country: 'India', region: 'East' },
      'indore': { code: 'IDR', name: 'Indore', country: 'India', region: 'Central' },
      'coimbatore': { code: 'CJB', name: 'Coimbatore', country: 'India', region: 'South' },
      'vadodara': { code: 'BDQ', name: 'Vadodara', country: 'India', region: 'West' },
      'nagpur': { code: 'NAG', name: 'Nagpur', country: 'India', region: 'Central' },
      'visakhapatnam': { code: 'VTZ', name: 'Visakhapatnam', country: 'India', region: 'South' },
      'madurai': { code: 'IXM', name: 'Madurai', country: 'India', region: 'South' }
    };

    // Direct match
    if (cityMappings[cityName]) {
      return cityMappings[cityName];
    }

    // Partial match
    for (const [key, value] of Object.entries(cityMappings)) {
      if (key.includes(cityName) || cityName.includes(key)) {
        return value;
      }
    }

    return null;
  }

  /**
   * Cache validation result
   * @param {string} cityName - City name
   * @param {Object} result - Validation result
   */
  _cacheResult(cityName, result) {
    this.cache.set(cityName, {
      data: result,
      timestamp: Date.now()
    });
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Get cache stats
   * @returns {Object} - Cache statistics
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }
}

module.exports = new CityValidationService();
