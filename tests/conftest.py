import sys
from pathlib import Path

lib = Path(__file__, '../../lib').resolve()
sys.path.insert(0, str(lib))
