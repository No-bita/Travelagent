/**
 * Enhanced Date parsing and validation utilities
 * Combines comprehensive natural language processing with robust error handling
 */

const moment = require('moment');

/**
 * Enhanced date utilities with comprehensive natural language support
 */
class DateUtils {
  /**
   * Comprehensive date parsing with natural language support
   * @param {string} dateInput - Date string to parse
   * @returns {string|null} - Formatted date (YYYY-MM-DD) or null if invalid
   */
  static parseDate(dateInput) {
    if (!dateInput || typeof dateInput !== 'string') {
      return null;
    }

    const input = dateInput.trim().toLowerCase();
    
    // Handle relative dates with comprehensive patterns
    if (input === 'today') {
      return moment().format('YYYY-MM-DD');
    }
    
    if (input === 'tomorrow') {
      return moment().add(1, 'day').format('YYYY-MM-DD');
    }
    
    if (input === 'day after tomorrow') {
      return moment().add(2, 'days').format('YYYY-MM-DD');
    }
    
    if (input.includes('next week')) {
      return moment().add(1, 'week').format('YYYY-MM-DD');
    }
    
    if (input.includes('next month')) {
      return moment().add(1, 'month').format('YYYY-MM-DD');
    }
    
    if (input.includes('next year')) {
      return moment().add(1, 'year').format('YYYY-MM-DD');
    }

    // Handle day of week patterns
    const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    for (let i = 0; i < daysOfWeek.length; i++) {
      if (input.includes(`next ${daysOfWeek[i]}`)) {
        return moment().day(i + 7).format('YYYY-MM-DD');
      }
    }
    
    for (let i = 0; i < daysOfWeek.length; i++) {
      if (input.includes(`this ${daysOfWeek[i]}`)) {
        const thisWeekDay = moment().day(i);
        const nextWeekDay = moment().day(i + 7);
        const date = thisWeekDay.isAfter(moment()) ? thisWeekDay : nextWeekDay;
        return date.format('YYYY-MM-DD');
      }
    }

    // Handle "in X days/weeks/months" patterns
    const inDays = input.match(/in (\d+) days?/);
    if (inDays) {
      return moment().add(parseInt(inDays[1], 10), 'days').format('YYYY-MM-DD');
    }
    
    const inWeeks = input.match(/in (\d+) weeks?/);
    if (inWeeks) {
      return moment().add(parseInt(inWeeks[1], 10), 'weeks').format('YYYY-MM-DD');
    }
    
    const inMonths = input.match(/in (\d+) months?/);
    if (inMonths) {
      return moment().add(parseInt(inMonths[1], 10), 'months').format('YYYY-MM-DD');
    }

    // Handle partial dates (day only with ordinal suffixes)
    const dayOnly = input.match(/(\d{1,2})(?:st|nd|rd|th)?/);
    if (dayOnly) {
      const day = parseInt(dayOnly[1], 10);
      if (day >= 1 && day <= 31) {
        return this._handlePartialDate(day);
      }
    }
    
    // Handle month + day combinations
    if (/^[a-z]{3}\s+\d{1,2}$/.test(input) || /^\d{1,2}\s+[a-z]{3}$/.test(input)) {
      const parsed = moment(dateInput, ['MMM DD', 'DD MMM'], true);
      if (parsed.isValid()) {
        // If date is in the past, assume next year
        if (parsed.isBefore(moment(), 'day')) {
          parsed.add(1, 'year');
        }
        return parsed.format('YYYY-MM-DD');
      }
    }
    
    // Handle various date formats with strict parsing
    const formats = [
      'YYYY-MM-DD', 'DD-MM-YYYY', 'DD/MM/YYYY', 'MM/DD/YYYY',
      'DD MMM YYYY', 'DD MMMM YYYY', 'MMM DD, YYYY', 'MMMM DD, YYYY',
      'DD-MM-YY', 'DD/MM/YY', 'MM/DD/YY', 'YYYY/MM/DD',
      'DD.MM.YYYY', 'MM-DD-YYYY', 'DD-MMM-YYYY',
      'DD MMM', 'MMM DD', 'DD MMMM', 'MMMM DD'
    ];
    
    for (const format of formats) {
      const parsed = moment(dateInput, format, true);
      if (parsed.isValid()) {
        // Ensure date is not in the past
        if (parsed.isBefore(moment(), 'day')) {
          return null;
        }
        return parsed.format('YYYY-MM-DD');
      }
    }
    
    return null;
  }

  /**
   * Handle partial date input (day only)
   * @private
   * @param {number} day - Day of month
   * @returns {string|null} - Formatted date or null if invalid
   */
  static _handlePartialDate(day) {
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

  /**
   * Validate if date is in the future
   * @param {string} dateString - Date in YYYY-MM-DD format
   * @returns {boolean} - True if date is valid and in future
   */
  static isValidFutureDate(dateString) {
    if (!dateString) return false;
    
    const date = moment(dateString, 'YYYY-MM-DD', true);
    if (!date.isValid()) return false;
    
    const today = moment().startOf('day');
    return date.isAfter(today);
  }

  /**
   * Check if input is a partial date that needs confirmation
   * @param {string} dateInput - Date string to check
   * @returns {boolean} - True if partial date
   */
  static isPartialDateInput(dateInput) {
    if (!dateInput || typeof dateInput !== 'string') return false;
    
    const input = dateInput.trim().toLowerCase();
    
    // Check for partial patterns
    return /^(\d{1,2})(?:st|nd|rd|th)?$/.test(input) || // Just day number with ordinal
           /^[a-z]{3}\s+\d{1,2}$/.test(input) || // Month + day
           /^\d{1,2}\s+[a-z]{3}$/.test(input) || // Day + month
           input.includes('next ') || // Next week/day
           input.includes('this '); // This week/day
  }

  /**
   * Get human-readable date format
   * @param {string} dateString - Date in YYYY-MM-DD format
   * @returns {string} - Human readable date
   */
  static formatHumanReadable(dateString) {
    if (!dateString) return '';
    
    const date = moment(dateString, 'YYYY-MM-DD');
    if (!date.isValid()) return dateString;
    
    return date.format('MMMM DD, YYYY');
  }

  /**
   * Get relative date description
   * @param {string} dateString - Date in YYYY-MM-DD format
   * @returns {string} - Relative description
   */
  static getRelativeDate(dateString) {
    if (!dateString) return '';
    
    const date = moment(dateString, 'YYYY-MM-DD');
    if (!date.isValid()) return dateString;
    
    const today = moment().startOf('day');
    const diffDays = date.diff(today, 'days');
    
    if (diffDays === 0) return 'today';
    if (diffDays === 1) return 'tomorrow';
    if (diffDays === -1) return 'yesterday';
    if (diffDays > 1 && diffDays <= 7) return `in ${diffDays} days`;
    if (diffDays < -1 && diffDays >= -7) return `${Math.abs(diffDays)} days ago`;
    
    return date.format('MMM DD, YYYY');
  }

  /**
   * Generate alternative date suggestions with enhanced options
   * @param {string} dateString - Base date in YYYY-MM-DD format
   * @returns {string} - Formatted alternative dates
   */
  static generateAlternativeDates(dateString) {
    if (!dateString) return 'No alternative dates available.';
    
    const baseDate = moment(dateString, 'YYYY-MM-DD');
    if (!baseDate.isValid()) return 'No alternative dates available.';
    
    const alternatives = [];
    
    // Add next month option
    const nextMonth = baseDate.clone().add(1, 'month');
    if (nextMonth.isValid()) {
      alternatives.push(`• ${nextMonth.format('DD MMM YYYY')} (next month)`);
    }
    
    // Add next year option
    const nextYear = baseDate.clone().add(1, 'year');
    if (nextYear.isValid()) {
      alternatives.push(`• ${nextYear.format('DD MMM YYYY')} (next year)`);
    }
    
    // Add day before and after options
    const dayBefore = baseDate.clone().subtract(1, 'day');
    const dayAfter = baseDate.clone().add(1, 'day');
    
    if (dayBefore.isValid() && dayBefore.isAfter(moment(), 'day')) {
      alternatives.push(`• ${dayBefore.format('DD MMM YYYY')} (day before)`);
    }
    
    if (dayAfter.isValid()) {
      alternatives.push(`• ${dayAfter.format('DD MMM YYYY')} (day after)`);
    }
    
    return alternatives.length > 0 
      ? `Alternative dates:\n${alternatives.join('\n')}` 
      : 'No alternative dates available.';
  }

  /**
   * Generate alternative date options for UI with enhanced variety
   * @param {string} dateString - Base date in YYYY-MM-DD format
   * @returns {Array} - Array of alternative date options
   */
  static generateAlternativeOptions(dateString) {
    if (!dateString) return [];
    
    const baseDate = moment(dateString, 'YYYY-MM-DD');
    if (!baseDate.isValid()) return [];
    
    const options = ['Yes', 'No'];
    
    // Add next month
    const nextMonth = baseDate.clone().add(1, 'month');
    if (nextMonth.isValid()) {
      options.push(nextMonth.format('DD MMM YYYY'));
    }
    
    // Add next year
    const nextYear = baseDate.clone().add(1, 'year');
    if (nextYear.isValid()) {
      options.push(nextYear.format('DD MMM YYYY'));
    }
    
    // Add day before and after
    const dayBefore = baseDate.clone().subtract(1, 'day');
    const dayAfter = baseDate.clone().add(1, 'day');
    
    if (dayBefore.isValid() && dayBefore.isAfter(moment(), 'day')) {
      options.push(dayBefore.format('DD MMM YYYY'));
    }
    
    if (dayAfter.isValid()) {
      options.push(dayAfter.format('DD MMM YYYY'));
    }
    
    // Remove duplicates and limit to 6 options
    return Array.from(new Set(options)).slice(0, 6);
  }

  /**
   * Legacy function for backward compatibility
   * @param {string} dateString - Date string to validate
   * @returns {string|null} - Formatted date or null
   */
  static validateDate(dateString) {
    return this.parseDate(dateString);
  }
}

module.exports = DateUtils;
