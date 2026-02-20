/**
 * DevMind API client.
 * All requests go through Node gateway (proxy /api).
 */

import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 300000, // 5 min - ingest can take several minutes
});

// Attach token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("devmind_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("devmind_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const auth = {
  register: (email, password, name) =>
    api.post("/auth/register", { email, password, name }),
  login: (email, password) =>
    api.post("/auth/login", { email, password }),
};

export const repo = {
  ingest: (repoUrl, repoId, branch) =>
    api.post("/repo/ingest", { repo_url: repoUrl, repo_id: repoId, branch: branch || undefined }),
};

export const ai = {
  ask: (question, repoId) =>
    api.post("/ai/ask", { question, repo_id: repoId }),
  explain: (code, language) =>
    api.post("/ai/explain", { code, language: language || "python" }),
  generateDocs: (repoId) =>
    api.post("/ai/generate-docs", { repo_id: repoId }),
};
