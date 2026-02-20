import { useState, useRef, useEffect } from "react";
import { ai } from "../services/api";

export default function ChatInterface({ repoId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo(0, listRef.current.scrollHeight);
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setLoading(true);
    try {
      const { data } = await ai.ask(q, repoId);
      setMessages((m) => [...m, { role: "assistant", content: data.answer }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${err.response?.data?.error || err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages" ref={listRef}>
        {messages.length === 0 && !loading && (
          <div className="chat-empty">
            <p className="chat-placeholder">
              Ask about architecture, behavior, or specific files in your active repo.
            </p>
            <ul className="chat-suggestions">
              <li>“Give me a high-level overview of this project.”</li>
              <li>“How does authentication work in this codebase?”</li>
              <li>“Explain the responsibilities of the `User` model.”</li>
            </ul>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            <div className="chat-bubble">
              <span className="chat-role">{m.role === "user" ? "You" : "DevMind"}</span>
              <pre>{m.content}</pre>
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-msg assistant">
            <div className="chat-bubble">
              <span className="chat-role">DevMind</span>
              <div className="typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}
      </div>
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          placeholder={repoId ? "Ask a question about this repo…" : "Connect a repo to start chatting…"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading || !repoId}
        />
        <button type="submit" disabled={loading || !repoId}>
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </div>
  );
}
