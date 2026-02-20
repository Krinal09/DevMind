/**
 * Repo controller: forward ingest to Python AI service.
 */

const aiClient = require("../config/aiService");

exports.ingest = async (req, res) => {
  try {
    const { repo_url, repo_id, branch } = req.body;
    if (!repo_url || !repo_id) {
      return res.status(400).json({ error: "repo_url and repo_id required" });
    }
    const { data } = await aiClient.post("/api/ingest", { repo_url, repo_id, branch }, { timeout: 300000 });
    res.json(data);
  } catch (err) {
    const status = err.response?.status || 500;
    const msg = err.response?.data?.detail || err.message;
    res.status(status).json({ error: msg });
  }
};
