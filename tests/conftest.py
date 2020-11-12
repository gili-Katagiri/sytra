import sys
from pathlib import Path

lib = Path(__file__,'../../lib').resolve()
sys.path.insert(0, str(lib))

from stocker import Stocker
import shutil
import pytest

testroot = Path(__file__+'/../testocks/').resolve()
presets = Path(__file__+'/../.presetdata').resolve()

h2020 = (presets/'h2020').read_text()
h2021 = (presets/'h2021').read_text()
s4382 = (presets/'s4382').read_text()
s6890 = (presets/'s6890').read_text()
sum0713 = (presets/'sum0713').read_text()

@pytest.fixture(scope='module')
def sytra_file_fixture():
    if testroot.exists():
        shutil.rmtree(str(testroot))

    # create directory and sytraconf.toml
    Stocker.stocker_init(rootdir=str(testroot), daystr='2020-07-10')
        
    # directory for holidays
    (testroot/'holidays'/'2020.csv').write_text(h2020)
    (testroot/'holidays'/'2021.csv').write_text(h2021)

    # directory for prepare
    (testroot/'prepare'/'4382.csv').write_text(s4382)
    (testroot/'prepare'/'6890.csv').write_text(s6890)
    
    # sbase.csv
    (testroot/'summary.csv').write_text(sum0713)
    
    # load style
    yield str(testroot)

@pytest.fixture(scope='module')
def sytra_follow_fixture(sytra_file_fixture):

    # prepare Stocker as stck
    stck = Stocker(sytra_file_fixture)
    # follow, force: already exists summary.csv
    stck.follow_interface(codes=[], force=True)
    
    # given style
    return stck
