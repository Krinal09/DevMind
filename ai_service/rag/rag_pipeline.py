"""
DevMind - RAG pipeline. Uses Groq (free API) or Ollama for LLM.
Get a free API key: https://console.groq.com
"""

import os
import re
from pathlib import Path
from typing import List, Optional

import httpx

# Ensure .env is loaded (in case this module is imported before main loads it)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


def _call_llm(prompt: str, max_tokens: int = 1024) -> Optional[str]:
    """Call LLM: Groq first (free), then Ollama if no key."""
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
    if api_key and len(api_key) > 20:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            r = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content.strip()
        except Exception as e:
            print(f"[DevMind] Groq API error: {type(e).__name__}: {e}", flush=True)
    # 2. Try Ollama (local)
    try:
        t = httpx.Timeout(connect=5.0, read=120.0)
        with httpx.Client(timeout=t) as client:
            r = client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
    except Exception:
        pass
    return None


def _format_context(chunks: List[dict]) -> str:
    """Format retrieved chunks for prompt context."""
    parts = []
    for i, c in enumerate(chunks, 1):
        meta = c.get("metadata", {})
        path = meta.get("file_path", "unknown")
        start = meta.get("start_line", "?")
        end = meta.get("end_line", "?")
        parts.append(f"--- Chunk {i} ({path}, lines {start}-{end}) ---\n{c.get('content', '')}")
    return "\n\n".join(parts)


def answer_question(
    question: str,
    context_chunks: List[dict],
    repo_id: Optional[str] = None,
) -> str:
    """RAG question answering over codebase."""
    if not context_chunks:
        return (
            "No codebase has been ingested yet. Please ingest a GitHub repository first, then ask questions.\n\n"
            "**To enable AI answers:** Add a free Groq API key to your .env file. Get one at https://console.groq.com"
        )
    context = _format_context(context_chunks)
    prompt = f"""You are DevMind, an AI assistant for developers. Answer the question based ONLY on the provided code. Be concise and helpful.

CODE:
{context}

QUESTION: {question}

Answer in 2-4 short paragraphs. If the code doesn't contain relevant info, say so clearly."""

    response = _call_llm(prompt)
    if response:
        return response

    # Fallback: structured summary from chunks
    return _fallback_overview(context_chunks, question)


def _fallback_overview(chunks: List[dict], question: str) -> str:
    """Generate a structured overview from chunks when no LLM."""
    files = {}
    for c in chunks:
        meta = c.get("metadata", {})
        path = meta.get("file_path", "unknown")
        content = c.get("content", "")
        if path not in files:
            files[path] = []
        files[path].append(content)

    lines = ["**Codebase overview** (AI not configured — add GROQ_API_KEY for full answers):\n"]
    for path in sorted(files.keys())[:15]:
        parts = path.replace("\\", "/").split("/")
        name = parts[-1] if parts else path
        snip = files[path][0][:200].replace("\n", " ").strip()
        lines.append(f"• **{path}** — {snip}...")
    lines.append("\n*Add GROQ_API_KEY to .env for AI-generated answers. Free at https://console.groq.com*")
    return "\n".join(lines)


def explain_code(code: str, language: str = "python") -> str:
    """Explain code using LLM or structured fallback."""
    prompt = f"""Explain this {language} code in 2-3 short paragraphs. What does it do? Key logic? Any important patterns?

```{language}
{code}
```"""

    response = _call_llm(prompt)
    if response:
        return response
    return _fallback_explain(code, language)


def _fallback_explain(code: str, language: str) -> str:
    """Structured code explanation when no LLM."""
    lines = [l.strip() for l in code.strip().split("\n") if l.strip()]
    parts = ["**Code analysis** (add GROQ_API_KEY for full AI explanations):\n"]
    for line in lines[:25]:
        if line.startswith("def ") and "(" in line:
            name = line.split("(")[0].replace("def ", "").strip()
            args = line[line.find("(") + 1:line.rfind(")")].strip()
            parts.append(f"• **Function** `{name}({args})` — user-defined function")
        elif line.startswith("class ") and ":" in line:
            name = line.split("(")[0].replace("class ", "").split(":")[0].strip()
            parts.append(f"• **Class** `{name}` — class definition")
        elif line.startswith("import ") or line.startswith("from "):
            parts.append(f"• **Import** — {line[:60]}")
        elif re.match(r"^\w+\s*=\s*", line) and "def " not in line:
            var = line.split("=")[0].strip()
            parts.append(f"• **Variable** `{var}` — assignment")
        elif "for " in line and " in " in line:
            parts.append(f"• **Loop** — iteration")
        elif "if " in line and ":" in line:
            parts.append(f"• **Condition** — branch")
        elif "return " in line:
            parts.append(f"• **Return** — returns a value")
    if len(parts) == 1:
        parts.append("• General code snippet")
    parts.append("\n*Get a free API key at https://console.groq.com and add GROQ_API_KEY to .env*")
    return "\n".join(parts)


def generate_docs(
    chunks: List[dict],
    repo_id: Optional[str] = None,
) -> str:
    """Generate documentation from codebase chunks."""
    if not chunks:
        return (
            "No codebase ingested. Ingest a GitHub repository first.\n\n"
            "**To enable AI docs:** Add GROQ_API_KEY to .env (free at https://console.groq.com)"
        )
    context = _format_context(chunks)
    prompt = f"""Generate documentation for this codebase. Use this structure:

1. **Overview** — What the project does (2-3 sentences)
2. **Main components** — List files/modules and their roles
3. **Key functions** — Important functions and what they do
4. **Usage** — How to run or use it (if apparent)

CODE:
{context}

Write clear, structured documentation."""

    response = _call_llm(prompt, max_tokens=1500)
    if response:
        return response

    # Fallback
    return _fallback_docs(chunks)


def _fallback_docs(chunks: List[dict]) -> str:
    """Structured doc from chunks when no LLM."""
    files = {}
    for c in chunks:
        path = c.get("metadata", {}).get("file_path", "unknown")
        content = c.get("content", "")
        if path not in files:
            files[path] = content[:500]

    lines = [
        "# Codebase documentation",
        "(Add GROQ_API_KEY for full AI-generated docs)\n",
        "## Files",
    ]
    for path in sorted(files.keys())[:20]:
        lines.append(f"\n### {path}")
        lines.append("```")
        lines.append(files[path][:400] + ("..." if len(files[path]) > 400 else ""))
        lines.append("```")
    lines.append("\n*Get free API key: https://console.groq.com*")
    return "\n".join(lines)
