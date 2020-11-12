from analyzer import Analyzer, AnalyzerBase, AnalyzerError

import pytest

def test_planting_init(sytra_follow_fixture):
    # get stck instance
    stck = sytra_follow_fixture
    
    # none planting instance for planting batch process
    for code in stck.get_follows_tuple():
        dpath = stck.get_stockpath(code)
        anabase = AnalyzerBase(dpath)
        anabase.planting_init()

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
