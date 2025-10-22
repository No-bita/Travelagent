"""
Enhanced City Mappings for Offbeat Locations
Supports smaller cities, tourist destinations, and international locations
"""

# Comprehensive city mappings for offbeat locations
ENHANCED_CITY_MAPPINGS = {
    # Major Indian Cities (existing)
    'mumbai': ['mumbai', 'bombay', 'bom', 'mumbai city'],
    'delhi': ['delhi', 'new delhi', 'del', 'ncr', 'national capital region'],
    'bangalore': ['bangalore', 'bengaluru', 'blr', 'silicon valley of india'],
    'chennai': ['chennai', 'madras', 'maa', 'tamil nadu capital'],
    'hyderabad': ['hyderabad', 'hyd', 'hbd', 'cyberabad', 'pearl city'],
    'kolkata': ['kolkata', 'calcutta', 'ccu', 'city of joy'],
    'ahmedabad': ['ahmedabad', 'amd', 'gujarat capital'],
    'pune': ['pune', 'pnq', 'oxford of east'],
    'kochi': ['kochi', 'cochin', 'cok', 'queen of arabian sea'],
    'goa': ['goa', 'goi', 'panaji', 'beach capital'],
    'jaipur': ['jaipur', 'jai', 'pink city', 'rajasthan capital'],
    'lucknow': ['lucknow', 'lko', 'city of nawabs'],
    'guwahati': ['guwahati', 'gau', 'guwati', 'gateway to northeast'],
    'chandigarh': ['chandigarh', 'ixc', 'city beautiful'],
    
    # Tier-2 Indian Cities
    'indore': ['indore', 'idr', 'indore city', 'commercial capital'],
    'bhopal': ['bhopal', 'bho', 'city of lakes', 'madhya pradesh capital'],
    'coimbatore': ['coimbatore', 'cjb', 'covai', 'manchester of south'],
    'mysore': ['mysore', 'myq', 'mysuru', 'city of palaces'],
    'visakhapatnam': ['visakhapatnam', 'vtz', 'vizag', 'vishakapatnam'],
    'nagpur': ['nagpur', 'nag', 'orange city', 'winter capital'],
    'vadodara': ['vadodara', 'bdq', 'baroda', 'cultural capital'],
    'rajkot': ['rajkot', 'raj', 'rajkot city'],
    'amritsar': ['amritsar', 'atq', 'golden city', 'spiritual capital'],
    'tirupati': ['tirupati', 'tir', 'tirumala', 'temple city'],
    'bhubaneswar': ['bhubaneswar', 'bbi', 'temple city', 'odisha capital'],
    
    # Tourist Destinations
    'shimla': ['shimla', 'sim', 'queen of hills', 'hill station'],
    'manali': ['manali', 'kullu manali', 'adventure capital'],
    'udaipur': ['udaipur', 'uda', 'city of lakes', 'venice of east'],
    'jodhpur': ['jodhpur', 'jdh', 'blue city', 'sun city'],
    'agra': ['agra', 'agr', 'taj city', 'city of taj'],
    'varanasi': ['varanasi', 'vns', 'banaras', 'kashi', 'spiritual capital'],
    'kashmir': ['kashmir', 'srinagar', 'sri', 'paradise on earth'],
    'darjeeling': ['darjeeling', 'darj', 'queen of hills', 'tea capital'],
    'ooty': ['ooty', 'udagamandalam', 'queen of hills', 'hill station'],
    'alleppey': ['alleppey', 'alpy', 'alappuzha', 'venice of east'],
    'munnar': ['munnar', 'tea gardens', 'hill station'],
    'kodaikanal': ['kodaikanal', 'koda', 'princess of hills'],
    'mahabalipuram': ['mahabalipuram', 'mamallapuram', 'stone city'],
    'hampi': ['hampi', 'vijayanagara', 'ruins city'],
    'kerala': ['kerala', 'god\'s own country', 'backwaters'],
    
    # Business Hubs & NCR
    'gurgaon': ['gurgaon', 'gurugram', 'gur', 'millennium city'],
    'noida': ['noida', 'noida city', 'tech hub'],
    'faridabad': ['faridabad', 'faridabad city', 'industrial city'],
    'ghaziabad': ['ghaziabad', 'ghaziabad city'],
    
    # International Cities (Major)
    'dubai': ['dubai', 'dxb', 'uae', 'emirates'],
    'singapore': ['singapore', 'sin', 'sg', 'lion city'],
    'bangkok': ['bangkok', 'bkk', 'thailand', 'land of smiles'],
    'london': ['london', 'lhr', 'uk', 'united kingdom'],
    'new york': ['new york', 'nyc', 'jfk', 'usa', 'america'],
    'dubai': ['dubai', 'dxb', 'uae', 'emirates'],
    'singapore': ['singapore', 'sin', 'sg', 'lion city'],
    'bangkok': ['bangkok', 'bkk', 'thailand', 'land of smiles'],
    'london': ['london', 'lhr', 'uk', 'united kingdom'],
    'new york': ['new york', 'nyc', 'jfk', 'usa', 'america'],
    'paris': ['paris', 'cdg', 'france', 'city of light'],
    'tokyo': ['tokyo', 'nrt', 'japan', 'land of rising sun'],
    'sydney': ['sydney', 'syd', 'australia', 'harbour city'],
    'toronto': ['toronto', 'yyz', 'canada', 'maple leaf'],
    'frankfurt': ['frankfurt', 'fra', 'germany', 'financial hub'],
    'amsterdam': ['amsterdam', 'ams', 'netherlands', 'venice of north'],
    'zurich': ['zurich', 'zrh', 'switzerland', 'banking capital'],
    'moscow': ['moscow', 'svo', 'russia', 'red square'],
    'istanbul': ['istanbul', 'ist', 'turkey', 'bridge between continents'],
    'cairo': ['cairo', 'cai', 'egypt', 'land of pharaohs'],
    'johannesburg': ['johannesburg', 'jhb', 'south africa', 'city of gold'],
    'nairobi': ['nairobi', 'nbo', 'kenya', 'green city'],
    'riyadh': ['riyadh', 'ruh', 'saudi arabia', 'desert capital'],
    'doha': ['doha', 'doh', 'qatar', 'pearl of gulf'],
    'kuwait': ['kuwait', 'kwi', 'kuwait city'],
    'manama': ['manama', 'bahrain', 'bhr'],
    'muscat': ['muscat', 'mct', 'oman', 'pearl of arabia'],
    'tehran': ['tehran', 'thr', 'iran', 'persian capital'],
    'karachi': ['karachi', 'khi', 'pakistan', 'city of lights'],
    'dhaka': ['dhaka', 'dac', 'bangladesh', 'city of mosques'],
    'kathmandu': ['kathmandu', 'ktm', 'nepal', 'himalayan capital'],
    'colombo': ['colombo', 'cmb', 'sri lanka', 'pearl of indian ocean'],
    'male': ['male', 'mle', 'maldives', 'paradise islands'],
    'yangon': ['yangon', 'rgn', 'myanmar', 'golden land'],
    'phnom penh': ['phnom penh', 'pnh', 'cambodia', 'pearl of asia'],
    'vientiane': ['vientiane', 'vte', 'laos', 'land of million elephants'],
    'hanoi': ['hanoi', 'han', 'vietnam', 'city of lakes'],
    'ho chi minh': ['ho chi minh', 'sgn', 'saigon', 'vietnam'],
    'jakarta': ['jakarta', 'cgk', 'indonesia', 'big durian'],
    'kuala lumpur': ['kuala lumpur', 'kul', 'malaysia', 'garden city'],
    'manila': ['manila', 'mnl', 'philippines', 'pearl of orient'],
    'seoul': ['seoul', 'icn', 'south korea', 'soul of asia'],
    'hong kong': ['hong kong', 'hkg', 'hk', 'pearl of orient'],
    'taipei': ['taipei', 'tpe', 'taiwan', 'formosa'],
    'mumbai': ['mumbai', 'bombay', 'bom', 'mumbai city'],
    'delhi': ['delhi', 'new delhi', 'del', 'ncr', 'national capital region'],
    'bangalore': ['bangalore', 'bengaluru', 'blr', 'silicon valley of india'],
    'chennai': ['chennai', 'madras', 'maa', 'tamil nadu capital'],
    'hyderabad': ['hyderabad', 'hyd', 'hbd', 'cyberabad', 'pearl city'],
    'kolkata': ['kolkata', 'calcutta', 'ccu', 'city of joy'],
    'ahmedabad': ['ahmedabad', 'amd', 'gujarat capital'],
    'pune': ['pune', 'pnq', 'oxford of east'],
    'kochi': ['kochi', 'cochin', 'cok', 'queen of arabian sea'],
    'goa': ['goa', 'goi', 'panaji', 'beach capital'],
    'jaipur': ['jaipur', 'jai', 'pink city', 'rajasthan capital'],
    'lucknow': ['lucknow', 'lko', 'city of nawabs'],
    'guwahati': ['guwahati', 'gau', 'guwati', 'gateway to northeast'],
    'chandigarh': ['chandigarh', 'ixc', 'city beautiful'],
    
    # Tier-2 Indian Cities
    'indore': ['indore', 'idr', 'indore city', 'commercial capital'],
    'bhopal': ['bhopal', 'bho', 'city of lakes', 'madhya pradesh capital'],
    'coimbatore': ['coimbatore', 'cjb', 'covai', 'manchester of south'],
    'mysore': ['mysore', 'myq', 'mysuru', 'city of palaces'],
    'visakhapatnam': ['visakhapatnam', 'vtz', 'vizag', 'vishakapatnam'],
    'nagpur': ['nagpur', 'nag', 'orange city', 'winter capital'],
    'vadodara': ['vadodara', 'bdq', 'baroda', 'cultural capital'],
    'rajkot': ['rajkot', 'raj', 'rajkot city'],
    'amritsar': ['amritsar', 'atq', 'golden city', 'spiritual capital'],
    'tirupati': ['tirupati', 'tir', 'tirumala', 'temple city'],
    'bhubaneswar': ['bhubaneswar', 'bbi', 'temple city', 'odisha capital'],
    
    # Tourist Destinations
    'shimla': ['shimla', 'sim', 'queen of hills', 'hill station'],
    'manali': ['manali', 'kullu manali', 'adventure capital'],
    'udaipur': ['udaipur', 'uda', 'city of lakes', 'venice of east'],
    'jodhpur': ['jodhpur', 'jdh', 'blue city', 'sun city'],
    'agra': ['agra', 'agr', 'taj city', 'city of taj'],
    'varanasi': ['varanasi', 'vns', 'banaras', 'kashi', 'spiritual capital'],
    'kashmir': ['kashmir', 'srinagar', 'sri', 'paradise on earth'],
    'darjeeling': ['darjeeling', 'darj', 'queen of hills', 'tea capital'],
    'ooty': ['ooty', 'udagamandalam', 'queen of hills', 'hill station'],
    'alleppey': ['alleppey', 'alpy', 'alappuzha', 'venice of east'],
    'munnar': ['munnar', 'tea gardens', 'hill station'],
    'kodaikanal': ['kodaikanal', 'koda', 'princess of hills'],
    'mahabalipuram': ['mahabalipuram', 'mamallapuram', 'stone city'],
    'hampi': ['hampi', 'vijayanagara', 'ruins city'],
    'kerala': ['kerala', 'god\'s own country', 'backwaters'],
    
    # Business Hubs & NCR
    'gurgaon': ['gurgaon', 'gurugram', 'gur', 'millennium city'],
    'noida': ['noida', 'noida city', 'tech hub'],
    'faridabad': ['faridabad', 'faridabad city', 'industrial city'],
    'ghaziabad': ['ghaziabad', 'ghaziabad city'],
    
    # International Cities (Major)
    'dubai': ['dubai', 'dxb', 'uae', 'emirates'],
    'singapore': ['singapore', 'sin', 'sg', 'lion city'],
    'bangkok': ['bangkok', 'bkk', 'thailand', 'land of smiles'],
    'london': ['london', 'lhr', 'uk', 'united kingdom'],
    'new york': ['new york', 'nyc', 'jfk', 'usa', 'america'],
    'paris': ['paris', 'cdg', 'france', 'city of light'],
    'tokyo': ['tokyo', 'nrt', 'japan', 'land of rising sun'],
    'sydney': ['sydney', 'syd', 'australia', 'harbour city'],
    'toronto': ['toronto', 'yyz', 'canada', 'maple leaf'],
    'frankfurt': ['frankfurt', 'fra', 'germany', 'financial hub'],
    'amsterdam': ['amsterdam', 'ams', 'netherlands', 'venice of north'],
    'zurich': ['zurich', 'zrh', 'switzerland', 'banking capital'],
    'moscow': ['moscow', 'svo', 'russia', 'red square'],
    'istanbul': ['istanbul', 'ist', 'turkey', 'bridge between continents'],
    'cairo': ['cairo', 'cai', 'egypt', 'land of pharaohs'],
    'johannesburg': ['johannesburg', 'jhb', 'south africa', 'city of gold'],
    'nairobi': ['nairobi', 'nbo', 'kenya', 'green city'],
    'riyadh': ['riyadh', 'ruh', 'saudi arabia', 'desert capital'],
    'doha': ['doha', 'doh', 'qatar', 'pearl of gulf'],
    'kuwait': ['kuwait', 'kwi', 'kuwait city'],
    'manama': ['manama', 'bahrain', 'bhr'],
    'muscat': ['muscat', 'mct', 'oman', 'pearl of arabia'],
    'tehran': ['tehran', 'thr', 'iran', 'persian capital'],
    'karachi': ['karachi', 'khi', 'pakistan', 'city of lights'],
    'dhaka': ['dhaka', 'dac', 'bangladesh', 'city of mosques'],
    'kathmandu': ['kathmandu', 'ktm', 'nepal', 'himalayan capital'],
    'colombo': ['colombo', 'cmb', 'sri lanka', 'pearl of indian ocean'],
    'male': ['male', 'mle', 'maldives', 'paradise islands'],
    'yangon': ['yangon', 'rgn', 'myanmar', 'golden land'],
    'phnom penh': ['phnom penh', 'pnh', 'cambodia', 'pearl of asia'],
    'vientiane': ['vientiane', 'vte', 'laos', 'land of million elephants'],
    'hanoi': ['hanoi', 'han', 'vietnam', 'city of lakes'],
    'ho chi minh': ['ho chi minh', 'sgn', 'saigon', 'vietnam'],
    'jakarta': ['jakarta', 'cgk', 'indonesia', 'big durian'],
    'kuala lumpur': ['kuala lumpur', 'kul', 'malaysia', 'garden city'],
    'manila': ['manila', 'mnl', 'philippines', 'pearl of orient'],
    'seoul': ['seoul', 'icn', 'south korea', 'soul of asia'],
    'hong kong': ['hong kong', 'hkg', 'hk', 'pearl of orient'],
    'taipei': ['taipei', 'tpe', 'taiwan', 'formosa']
}

# Enhanced airport codes for offbeat locations
ENHANCED_AIRPORT_CODES = {
    # Major Indian Cities
    'mumbai': 'BOM', 'delhi': 'DEL', 'bangalore': 'BLR', 'chennai': 'MAA',
    'hyderabad': 'HYD', 'kolkata': 'CCU', 'ahmedabad': 'AMD', 'pune': 'PNQ',
    'kochi': 'COK', 'goa': 'GOI', 'jaipur': 'JAI', 'lucknow': 'LKO',
    'guwahati': 'GAU', 'chandigarh': 'IXC',
    
    # Tier-2 Indian Cities
    'indore': 'IDR', 'bhopal': 'BHO', 'coimbatore': 'CJB', 'mysore': 'MYQ',
    'visakhapatnam': 'VTZ', 'nagpur': 'NAG', 'vadodara': 'BDQ', 'rajkot': 'RAJ',
    'amritsar': 'ATQ', 'tirupati': 'TIR', 'bhubaneswar': 'BBI',
    
    # Tourist Destinations
    'shimla': 'SLV', 'manali': 'KUU', 'udaipur': 'UDR', 'jodhpur': 'JDH',
    'agra': 'AGR', 'varanasi': 'VNS', 'kashmir': 'SXR', 'darjeeling': 'IXB',
    'ooty': 'COK', 'alleppey': 'COK', 'munnar': 'COK', 'kodaikanal': 'COK',
    'mahabalipuram': 'MAA', 'hampi': 'BLR', 'kerala': 'COK',
    
    # Business Hubs
    'gurgaon': 'DEL', 'noida': 'DEL', 'faridabad': 'DEL', 'ghaziabad': 'DEL',
    
    # International Cities
    'dubai': 'DXB', 'singapore': 'SIN', 'bangkok': 'BKK', 'london': 'LHR',
    'new york': 'JFK', 'paris': 'CDG', 'tokyo': 'NRT', 'sydney': 'SYD',
    'toronto': 'YYZ', 'frankfurt': 'FRA', 'amsterdam': 'AMS', 'zurich': 'ZRH',
    'moscow': 'SVO', 'istanbul': 'IST', 'cairo': 'CAI', 'johannesburg': 'JNB',
    'nairobi': 'NBO', 'riyadh': 'RUH', 'doha': 'DOH', 'kuwait': 'KWI',
    'manama': 'BAH', 'muscat': 'MCT', 'tehran': 'THR', 'karachi': 'KHI',
    'dhaka': 'DAC', 'kathmandu': 'KTM', 'colombo': 'CMB', 'male': 'MLE',
    'yangon': 'RGN', 'phnom penh': 'PNH', 'vientiane': 'VTE', 'hanoi': 'HAN',
    'ho chi minh': 'SGN', 'jakarta': 'CGK', 'kuala lumpur': 'KUL', 'manila': 'MNL',
    'seoul': 'ICN', 'hong kong': 'HKG', 'taipei': 'TPE'
}

def get_enhanced_city_mappings():
    """Get enhanced city mappings for offbeat locations"""
    return ENHANCED_CITY_MAPPINGS

def get_enhanced_airport_codes():
    """Get enhanced airport codes for offbeat locations"""
    return ENHANCED_AIRPORT_CODES

def is_offbeat_location(city: str) -> bool:
    """Check if a city is an offbeat location"""
    offbeat_cities = [
        'indore', 'bhopal', 'coimbatore', 'mysore', 'visakhapatnam',
        'shimla', 'manali', 'udaipur', 'jodhpur', 'agra', 'varanasi',
        'kashmir', 'darjeeling', 'ooty', 'alleppey', 'munnar',
        'kodaikanal', 'mahabalipuram', 'hampi', 'kerala',
        'gurgaon', 'noida', 'faridabad', 'ghaziabad'
    ]
    return city.lower() in offbeat_cities

def is_international_location(city: str) -> bool:
    """Check if a city is an international location"""
    international_cities = [
        'dubai', 'singapore', 'bangkok', 'london', 'new york', 'paris',
        'tokyo', 'sydney', 'toronto', 'frankfurt', 'amsterdam', 'zurich',
        'moscow', 'istanbul', 'cairo', 'johannesburg', 'nairobi',
        'riyadh', 'doha', 'kuwait', 'manama', 'muscat', 'tehran',
        'karachi', 'dhaka', 'kathmandu', 'colombo', 'male', 'yangon',
        'phnom penh', 'vientiane', 'hanoi', 'ho chi minh', 'jakarta',
        'kuala lumpur', 'manila', 'seoul', 'hong kong', 'taipei'
    ]
    return city.lower() in international_cities
