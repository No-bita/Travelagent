// server.js
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const Amadeus = require('amadeus');
const logger = require('./utils/logger');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  req.requestId = requestId;
  
  logger.info(`${req.method} ${req.path} - ${req.ip} - ${requestId}`);
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`${req.method} ${req.path} - ${res.statusCode} - ${duration}ms - ${requestId}`);
  });
  
  next();
});

// Init Amadeus (nullable)
let amadeus = null;
if (process.env.AMADEUS_CLIENT_ID && process.env.AMADEUS_CLIENT_SECRET) {
  amadeus = new Amadeus({
    clientId: process.env.AMADEUS_CLIENT_ID,
    clientSecret: process.env.AMADEUS_CLIENT_SECRET,
  });
  logger.info('Amadeus API initialized with credentials');
} else {
  logger.warn('Amadeus API credentials not found — using mock data mode');
}

// Attach dependencies to request for DI-lite
app.use((req, _res, next) => {
  req.amadeus = amadeus; // may be null
  req.logger = logger;
  next();
});

// Health endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '2.0.0',
    services: {
      flights: 'available',
      chat: 'available',
      amadeus: amadeus ? 'available' : 'unavailable'
    },
    requestId: req.requestId
  });
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Flight search API is running',
    version: '2.0.0',
    requestId: req.requestId
  });
});

// API routes
app.use('/api/flights', require('./routes/flights'));
app.use('/api/chat', require('./routes/chat')); // legacy chat entrypoint preserved

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Travel Agent API',
    version: '2.0.0',
    status: 'running',
    requestId: req.requestId,
    endpoints: {
      flights: '/api/flights/search',
      chat: '/api/chat',
      health: '/health',
      apiHealth: '/api/health'
    },
    features: [
      'Clean, testable service architecture',
      'Amadeus API integration with mock fallback',
      'Intelligent flight ranking and scoring',
      'Comprehensive city validation',
      'Legacy chat endpoint compatibility',
      'Robust error handling and logging',
      'Dependency injection pattern',
      'Request ID tracking'
    ]
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.originalUrl} not found`,
    requestId: req.requestId,
    availableEndpoints: [
      'GET /',
      'GET /health',
      'GET /api/health',
      'POST /api/flights/search',
      'GET /api/flights/airlines',
      'GET /api/flights/health',
      'POST /api/chat'
    ]
  });
});

// Global error handler (last)
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, _next) => {
  logger.error('Unhandled error', { 
    message: err.message, 
    stack: err.stack,
    requestId: req.requestId,
    url: req.url,
    method: req.method
  });
  
  res.status(err.status || 500).json({
    error: 'Internal Server Error',
    message: err.expose ? err.message : 'Something went kaput. Try again.',
    requestId: req.requestId,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  logger.info(`🚀 Travel Agent Server running on port ${PORT}`);
  logger.info(`📊 Health check: http://localhost:${PORT}/health`);
  logger.info(`🔍 Flight search: POST http://localhost:${PORT}/api/flights/search`);
  logger.info(`💬 Chat endpoint: POST http://localhost:${PORT}/api/chat`);
  logger.info(`📋 Available airlines: GET http://localhost:${PORT}/api/flights/airlines`);
});

module.exports = app;
