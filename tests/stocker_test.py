import pytest
from lib.stocker import StockManeger as SM
from lib.stocker import StockDataHolder
import os
import datetime

code = 1000
sm = SM()

print(sm.stock_filepath(1000))

@pytest.fixture
def params_fixture():

    yield
    path = SM.stock_filepath(code)
    os.rename(path / '.primitive.csv', path / 'primitive.csv')
    os.remove(path/'stock.csv')

    sm.unfollow_stock( code )
    sm.get_markeddays()._day_rewind()
    sm._dump()
    print(sm)

    path = SM.stock_filepath()
    os.rename(path / 'log' / '20200622', path / 'summary.csv')

def test_follow(params_fixture):
    
    # latest values NOT included
    with pytest.raises(IndexError): sm.follow_stock(1515)

    sm.follow_stock(code)
    sdh = StockDataHolder(code)

    print(sdh)
    
    with pytest.raises(KeyError): sm.follow_stock(code)

    sm.make_summarybase()
    
    print(sm)
    sm.allocate()
    print(sm)
