import { useState } from "react";
import { ai } from "../services/api";

export default function CodeExplain() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);

  const handleExplain = async (e) => {
    e.preventDefault();
    if (!code.trim() || loading) return;
    setExplanation("");
    setLoading(true);
    try {
      const { data } = await ai.explain(code.trim(), language);
      setExplanation(data.explanation);
    } catch (err) {
      setExplanation(`Error: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="code-explain">
      <h3>Explain code</h3>
      <form onSubmit={handleExplain}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option>
          <option value="html">HTML</option>
          <option value="css">CSS</option>
        </select>
        <textarea
          placeholder="Paste code to explain…"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={8}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Explaining…" : "Explain"}
        </button>
      </form>
      {explanation && (
        <div className="explanation-output">
          <h4>Explanation</h4>
          <pre>{explanation}</pre>
        </div>
      )}
    </div>
  );
}
