from stocker import Stocker, StockerError
from util.paths import SytraPathError

import pytest

class TestStockerInit:
    def test_check_files(self, stocker_init_fixture):
        # Stocker.__init__() is in conftest.py 
        # stocker_init_fixture == root path for test

        # load with no error
        stck = Stocker(stocker_init_fixture[0])
        
        # pathes are exists
        assert stck.get_logpath().exists()
        assert stck.get_preparepath().exists()
        assert stck.get_holidayspath().exists()

        # these process would correct if stck is loaded
        # if these couse error by cahnging path/directory,
        # you might see conftest.py and tests/testocks/
        assert stck.get_confpath().exists()
        assert stocker_init_fixture[1][0].exists()
        assert stocker_init_fixture[1][1].exists()

        # these have nothing to do with Stocker init, but in conftes.py
        assert stocker_init_fixture[1][2].exists()
        assert stocker_init_fixture[1][3].exists()
        assert stck.get_summarypath().exists()

        with pytest.raises(SytraPathError): stck.get_sbasepath(noerror=False)
        with pytest.raises(SytraPathError): stck._get_filepath('log', '20200713')

    def test_serial_proc(self, stocker_init_fixture):
        stck = Stocker(stocker_init_fixture[0])
        
        # NO ERROR 
        # follow 4382, 6890 in prepare
        stck.follow_interface(codes=[], force=True)
        # allocate summary.csv
        stck.allocate_interface()
        # create and print sbase
        stck.create_sbase()
        # save to sytraconf.toml
        stck.dump()

    def test_unfollow(self, stocker_init_fixture):
        stck = Stocker(stocker_init_fixture[0])

        assert stck.get_follows_tuple() == (4382, 6890)
        stck.follow_interface(codes=[4382], defollow=True)
        assert stck.get_follows_tuple() == ( 6890, )
        stck.follow_interface(codes=[6890], defollow=True, renames='testrename')
        assert stck.get_follows_tuple() == tuple()

        stck.dump()
