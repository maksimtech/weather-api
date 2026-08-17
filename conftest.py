# conftest.py
import sys
from pathlib import Path

# Make the top-level modules (main, config, schemas) importable from tests and
# benchmarks living in subdirectories.
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
