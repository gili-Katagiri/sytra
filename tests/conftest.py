import sys
from pathlib import Path

lib = Path(__file__,'../../sytra/lib').resolve(strict=True)
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
s9005 = (presets/'s9005').read_text()

sum0713 = (presets/'sum0713').read_text()
sum0714 = (presets/'sum0714').read_text()

ac4382 = (presets/'ac4382').read_text()
ac6890 = (presets/'ac6890').read_text()
ac9005 = (presets/'ac9005').read_text()

ac4382re = (presets/'ac4382re').read_text()
ac9005re = (presets/'ac9005re').read_text()

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

    # set analyconf.toml
    (testroot/'4382'/'analyconf.toml').write_text(ac4382)
    (testroot/'6890'/'analyconf.toml').write_text(ac6890)
    
    # given style
    yield stck

@pytest.fixture(scope='module')
def sytra_add_follow_fixture(sytra_follow_fixture):
    # 2020-07-14 follow
    (testroot/'9005').mkdir()
    (testroot/'9005'/'primitive.csv').write_text(s9005)

    # follow
    stck = sytra_follow_fixture
    stck.follow_interface(codes=[9005], force=True)

    # analyconf update
    (testroot/'9005'/'analyconf.toml').write_text(ac9005)

    # update summary.csv
    (testroot/'summary.csv').write_text(sum0714)
    
    yield stck

@pytest.fixture(scope='module')
def sytra_modify_fixture(sytra_add_follow_fixture):
    
    # 4382 add 'SMA34'
    (testroot/'4382'/'analyconf.toml').write_text(ac4382re)
    # 9005 add 'pafclose'
    (testroot/'9005'/'analyconf.toml').write_text(ac9005re)
    
    yield sytra_add_follow_fixture
