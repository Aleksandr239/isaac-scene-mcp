"""Load Isaac-side query scripts (sent over TCP to python_server)."""

from pathlib import Path

_DIR = Path(__file__).resolve().parent


def load(name: str, **replacements: str) -> str:
    """Load queries/<name>.py and replace __KEY__ placeholders with values."""
    path = _DIR / f"{name}.py"
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(f"__{key.upper()}__", value)
    return text
