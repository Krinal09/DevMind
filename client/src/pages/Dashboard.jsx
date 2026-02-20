import { useState } from "react";
import RepoInput from "../components/RepoInput";
import ChatInterface from "../components/ChatInterface";
import CodeExplain from "../components/CodeExplain";
import { ai } from "../services/api";

export default function Dashboard() {
  const [currentRepoId, setCurrentRepoId] = useState("");
  const [docs, setDocs] = useState("");
  const [docsLoading, setDocsLoading] = useState(false);

  const handleRepoIngested = (repoId) => {
    setCurrentRepoId(repoId);
    setDocs("");
  };

  const handleGenerateDocs = async () => {
    if (!currentRepoId || docsLoading) return;
    setDocs("");
    setDocsLoading(true);
    try {
      const { data } = await ai.generateDocs(currentRepoId);
      setDocs(data.documentation || "No documentation returned.");
    } catch (err) {
      setDocs(`Error: ${err.response?.data?.error || err.message}`);
    } finally {
      setDocsLoading(false);
    }
  };

  const handleDownloadDocs = () => {
    if (!docs) return;
    const blob = new Blob([docs], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentRepoId || "devmind_docs"}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleLogout = () => {
    localStorage.removeItem("devmind_token");
    window.location.href = "/login";
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <span className="brand">DevMind</span>
          <span className="brand-subtitle">AI Personal Assistant for Developers</span>
        </div>
        <button className="header-logout" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-card">
          <div className="card-header">
            <h2>Connect your repository</h2>
          </div>
          <RepoInput onIngested={handleRepoIngested} currentRepoId={currentRepoId} />
          <div className="card-meta">
            <span className="meta-label">Active repo:</span>
            <span className="meta-value">{currentRepoId || "None selected"}</span>
          </div>
        </section>

        <section className="dashboard-card">
          <div className="card-header">
            <h2>Ask about your codebase</h2>
          </div>
          <ChatInterface repoId={currentRepoId} />
        </section>

        <section className="dashboard-card">
          <div className="card-header">
            <h2>Explain code</h2>
          </div>
          <CodeExplain />
        </section>

        <section className="dashboard-card">
          <div className="card-header">
            <h2>Generate & download documentation</h2>
          </div>
          <div className="docs-actions">
            <button onClick={handleGenerateDocs} disabled={!currentRepoId || docsLoading}>
              {docsLoading ? "Generating…" : "Generate Docs"}
            </button>
            <button onClick={handleDownloadDocs} disabled={!docs}>
              Download Docs
            </button>
          </div>
          {docs && (
            <div className="docs-output">
              <pre>{docs}</pre>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

