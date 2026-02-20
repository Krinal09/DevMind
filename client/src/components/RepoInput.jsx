import { useState } from "react";
import { repo } from "../services/api";

export default function RepoInput({ onIngested, currentRepoId }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const parseRepo = (u) => {
    try {
      const s = (u || "").trim();
      const m = s.match(/github\.com[/:]([^/]+)\/([^/#?]+?)(?:\.git)?(?=[/#?]|$)/i);
      if (!m) return null;
      const name = m[2].replace(/\.git$/, "");
      const repoId = name ? `${m[1]}/${name}` : null;
      if (!repoId) return null;
      // Extract branch from /tree/branch-name
      const branchMatch = s.match(/\/tree\/([^/#?]+)/i);
      const branch = branchMatch ? branchMatch[1] : null;
      return { repoId, branch };
    } catch {
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    const parsed = parseRepo(url);
    if (!parsed) {
      setError("Enter a valid GitHub repo URL (e.g. https://github.com/owner/repo)");
      return;
    }
    const { repoId, branch } = parsed;
    const cloneUrl = `https://github.com/${repoId}.git`;
    setLoading(true);
    try {
      const { data } = await repo.ingest(cloneUrl, repoId, branch);
      setMessage(`Ingested ${data.files_processed} files, ${data.chunks_added} chunks`);
      onIngested?.(repoId);
    } catch (err) {
      setError(err.response?.data?.error || err.message || "Ingest failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="repo-input">
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Ingesting…" : "Ingest Repo"}
        </button>
      </form>
      {currentRepoId && <p className="repo-current">Active repo: {currentRepoId}</p>}
      {message && <p className="repo-message">{message}</p>}
      {error && <p className="repo-error">{error}</p>}
    </div>
  );
}
