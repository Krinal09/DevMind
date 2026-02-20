/**
 * AI Service proxy config.
 * Node forwards AI requests to Python FastAPI.
 */

const axios = require("axios");

const AI_BASE = process.env.AI_SERVICE_URL || "http://localhost:8000";

const aiClient = axios.create({
  baseURL: AI_BASE,
  timeout: 300000, // 5 min - ingest can take several minutes
  headers: { "Content-Type": "application/json" },
});

module.exports = aiClient;
