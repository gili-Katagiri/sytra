import sys
from pathlib import Path

# /root/project
src = Path().cwd()

sys.path.append( str(src) )
