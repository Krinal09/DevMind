/**
 * DevMind Gateway - Express app.
 * Handles auth + routing. Forwards AI requests to Python.
 */

const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, "..", ".env") });
const express = require("express");
const cors = require("cors");

const authRoutes = require("./routes/authRoutes");
const repoRoutes = require("./routes/repoRoutes");
const aiRoutes = require("./routes/aiRoutes");

const app = express();

app.use(cors({ origin: true }));
app.use(express.json());

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "gateway" });
});

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/repo", repoRoutes);
app.use("/api/ai", aiRoutes);

// 404
app.use((req, res) => {
  res.status(404).json({ error: "Not found" });
});

// Error handler
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message });
});

module.exports = app;
