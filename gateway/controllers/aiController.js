/**
 * AI controller: forward ask, explain, generate-docs to Python.
 */

const aiClient = require("../config/aiService");

exports.ask = async (req, res) => {
  try {
    const { question, repo_id } = req.body;
    if (!question) {
      return res.status(400).json({ error: "question required" });
    }
    const { data } = await aiClient.post("/api/ask", { question, repo_id });
    res.json(data);
  } catch (err) {
    const status = err.response?.status || 500;
    const msg = err.response?.data?.detail || err.message;
    res.status(status).json({ error: msg });
  }
};

exports.explain = async (req, res) => {
  try {
    const { code, language } = req.body;
    if (!code) {
      return res.status(400).json({ error: "code required" });
    }
    const { data } = await aiClient.post("/api/explain", { code, language: language || "python" });
    res.json(data);
  } catch (err) {
    const status = err.response?.status || 500;
    const msg = err.response?.data?.detail || err.message;
    res.status(status).json({ error: msg });
  }
};

exports.generateDocs = async (req, res) => {
  try {
    const { repo_id } = req.body;
    const { data } = await aiClient.post("/api/generate-docs", { repo_id });
    res.json(data);
  } catch (err) {
    const status = err.response?.status || 500;
    const msg = err.response?.data?.detail || err.message;
    res.status(status).json({ error: msg });
  }
};
