-- Initialize Travel Agent Database
-- This script runs when PostgreSQL container starts

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    from_city VARCHAR(100),
    to_city VARCHAR(100),
    date DATE,
    price NUMERIC(10,2),
    source VARCHAR(50),
    status VARCHAR(20) DEFAULT 'confirmed',
    booking_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sessions table for additional session storage
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    data JSONB,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- Additional performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_route_date ON bookings(from_city, to_city, date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_price ON bookings(price);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_active ON sessions(expires_at) WHERE expires_at > NOW();
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_metadata ON bookings USING GIN(booking_metadata);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional)
INSERT INTO users (name, phone, email) VALUES 
    ('Demo User', '+91-9876543210', 'demo@travelagent.com')
ON CONFLICT (phone) DO NOTHING;

-- Create a view for booking analytics
CREATE OR REPLACE VIEW booking_analytics AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_bookings,
    SUM(price) as total_revenue,
    AVG(price) as avg_price,
    COUNT(DISTINCT user_id) as unique_users
FROM bookings 
WHERE status = 'confirmed'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO travel_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO travel_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO travel_user;
