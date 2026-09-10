"""Pytest path shim: the dashboard runs as a flat directory (Streamlit
convention — `streamlit run analytics/app.py` puts `analytics/` on
sys.path). For pytest invoked from the repo root, prepend it ourselves
so the same `import constants` / `import metrics` statements resolve."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
