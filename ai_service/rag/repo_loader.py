"""
DevMind - Repository cloning and source file loading.
Uses subprocess for git clone. Loads code files including Jupyter notebooks.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# Extensions to load (code + notebooks; no .json data files)
SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".ipynb"}

# Directories to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}


def clone_repo(repo_url: str, target_dir: str, branch: Optional[str] = None) -> str:
    """
    Clone a Git repository into target_dir.

    Args:
        repo_url: GitHub repo URL (https or git)
        target_dir: Local path to clone into
        branch: Optional branch to clone (e.g. from /tree/branch-name in URL)

    Returns:
        Absolute path to cloned repo root
    """
    os.makedirs(target_dir, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["-b", branch])
    cmd.extend([repo_url, target_dir])
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return os.path.abspath(target_dir)


def load_source_files(repo_root: str) -> List[Tuple[str, str]]:
    """
    Recursively load all relevant source files from repo.

    Args:
        repo_root: Path to repo root

    Returns:
        List of (relative_file_path, content) tuples
    """
    files: List[Tuple[str, str]] = []
    root_path = Path(repo_root)

    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        # Skip excluded directories
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        # Skip files > 500KB (datasets, minified bundles) - would create too many chunks
        if path.stat().st_size > 500 * 1024:
            continue
        try:
            rel_path = str(path.relative_to(root_path))
            if path.suffix.lower() == ".ipynb":
                content = _load_notebook(path)
            else:
                content = path.read_text(encoding="utf-8", errors="replace")
            if content:
                files.append((rel_path, content))
        except Exception:
            continue

    return files


def _load_notebook(path: Path) -> str:
    """Extract code from Jupyter notebook (.ipynb)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        cells = data.get("cells", [])
        code_parts = []
        for cell in cells:
            if cell.get("cell_type") == "code":
                source = cell.get("source", [])
                if isinstance(source, list):
                    code_parts.append("".join(source))
                else:
                    code_parts.append(str(source))
        return "\n\n# --- Next cell ---\n\n".join(code_parts) if code_parts else ""
    except Exception:
        return ""
