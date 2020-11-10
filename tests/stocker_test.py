from stocker import Stocker, StockerError
from util.paths import SytraPathError

import pytest

def test_check_files(sytra_file_fixture):
    # Stocker.__init__() is in conftest.py 
    # sytra_file_fixture == root path for test

    # load with no error
    stck = Stocker(sytra_file_fixture)
    
    # pathes are exists
    assert stck.get_logpath().exists()
    assert stck.get_preparepath().exists()
    assert stck.get_holidayspath().exists()

    # these process would correct if stck is loaded
    # if these couse error by cahnging path/directory,
    # you might see conftest.py and tests/testocks/
    assert stck.get_confpath().exists()

    # these have nothing to do with Stocker init, but in conftes.py
    assert stck.get_summarypath().exists()
    
    # Not exist before process, (but exist after)
    with pytest.raises(SytraPathError): stck.get_sbasepath(noerror=False)
    with pytest.raises(SytraPathError): stck._get_filepath('log', '20200713')

def test_follow(sytra_file_fixture):
    stck = Stocker(sytra_file_fixture)
    
    # NO ERROR 
    # follow 4382, 6890 in prepare
    stck.follow_interface(codes=[], force=True)
    # create and print sbase
    stck.create_sbase()
    # save to sytraconf.toml
    stck.dump()

def test_defollow(sytra_file_fixture):
    stck = Stocker(sytra_file_fixture)

    assert stck.get_follows_tuple() == (4382, 6890)
    stck.follow_interface(codes=[4382], defollow=True, force=True)
    assert stck.get_follows_tuple() == ( 6890, )
    stck.follow_interface(codes=[6890], defollow=True, force=True)
    assert stck.get_follows_tuple() == tuple()

    stck.dump()
