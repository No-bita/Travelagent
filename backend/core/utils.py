from __future__ import annotations
from datetime import datetime, timedelta
import re


def normalize_natural_date(text: str) -> str | None:
    """Convert natural language dates to ISO format with enhanced partial date handling"""
    if not text:
        return None
        
    low = text.lower().strip()
    today = datetime.today().date()
    
    if "today" in low:
        return today.isoformat()
    if "tomorrow" in low:
        return (today + timedelta(days=1)).isoformat()
    
    # Handle "next week", "next month" etc.
    if "next week" in low:
        return (today + timedelta(weeks=1)).isoformat()
    if "next month" in low:
        # Approximate next month
        next_month = today.replace(day=1) + timedelta(days=32)
        return next_month.replace(day=1).isoformat()
    
    # Handle specific dates like "25 Dec", "Dec 25", "25/12"
    date_patterns = [
        r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # 25 Dec
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})',  # Dec 25
        r'(\d{1,2})/(\d{1,2})',  # 25/12
    ]
    
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    for pattern in date_patterns:
        match = re.search(pattern, low)
        if match:
            try:
                if '/' in pattern:  # DD/MM format
                    day, month = match.groups()
                    target_date = today.replace(month=int(month), day=int(day))
                else:  # Month name format
                    if pattern.startswith(r'(\d{1,2})'):  # 25 Dec
                        day, month_name = match.groups()
                        month = month_map[month_name]
                    else:  # Dec 25
                        month_name, day = match.groups()
                        month = month_map[month_name]
                    target_date = today.replace(month=month, day=int(day))
                
                # If date is in the past, assume next year
                if target_date < today:
                    target_date = target_date.replace(year=today.year + 1)
                    
                return target_date.isoformat()
            except (ValueError, KeyError):
                continue
    
    # NEW: Handle partial dates - just day number
    day_only_pattern = r'^(\d{1,2})(?:st|nd|rd|th)?$'
    day_match = re.match(day_only_pattern, low)
    if day_match:
        day = int(day_match.group(1))
        if 1 <= day <= 31:
            return _handle_partial_date(day, today)
    
    # If already in ISO format or close to it, try to parse
    iso_pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
    match = re.search(iso_pattern, text)
    if match:
        try:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            pass
    
    return None


def _handle_partial_date(day: int, today: datetime.date) -> str | None:
    """Handle partial dates where only day is provided"""
    current_month = today.month
    current_year = today.year
    
    # Try current month first
    try:
        target_date = today.replace(day=day)
        if target_date >= today:
            return target_date.isoformat()
    except ValueError:
        pass  # Invalid day for current month
    
    # Try next month
    try:
        if current_month == 12:
            next_month_date = today.replace(year=current_year + 1, month=1, day=1)
        else:
            next_month_date = today.replace(month=current_month + 1, day=1)
        
        target_date = next_month_date.replace(day=day)
        return target_date.isoformat()
    except ValueError:
        pass  # Invalid day for next month
    
    # Try next year if day is valid
    try:
        target_date = today.replace(year=current_year + 1, day=day)
        return target_date.isoformat()
    except ValueError:
        pass
    
    return None


