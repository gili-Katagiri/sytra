from analyzer import Analyzer, AnalyzerBase

from exceptions import AnalyzerError

import pytest

def test_planting_init(sytra_follow_fixture):
    # get stck instance
    # set analyconf.toml to 4382/ and 6890/
    stck = sytra_follow_fixture
    
    # none planting instance for planting batch process
    for code in stck.get_follows_tuple():
        dpath = stck.get_stockpath(code)
        anabase = AnalyzerBase(dpath)
        anabase.check_analyconf(withbatch=True)

    # save
    stck.dump()

def test_allocate(sytra_follow_fixture):
    # get stck instance
    stck = sytra_follow_fixture

    # allocate
    stck.allocate_interface()

    # create sbase.csv
    stck.create_sbase()

    # save
    stck.dump()

def test_add_follow(sytra_add_follow_fixture):
    # get stck instance: this instance is the same one at test_allocate
    # processed from follow to prepare for analyconf.toml and summary.csv
    stck = sytra_add_follow_fixture

    # 9005 heve not been prepared yet
    for code in stck.get_follows_tuple():
        dpath = stck.get_stockpath(code)
        anabase = AnalyzerBase(dpath)
        anabase.check_analyconf(withbatch=True)

    # allocate
    stck.allocate_interface()
    
    # post-process
    stck.create_sbase()
    stck.dump()

def test_modify_ac(sytra_modify_fixture):
    
    stck = sytra_modify_fixture

    # 4382 add 'SMA34', 9005 add 'pafclose' stem
    for code in stck.get_follows_tuple():
        dpath = stck.get_stockpath(code)
        anabase = AnalyzerBase(dpath)
        anabase.check_analyconf(withbatch=True)
