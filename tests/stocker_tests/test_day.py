import pytest
from lib.stocker.sytraday import SytraDay
from lib.stocker.errors import StockerError
from datetime import date

holi_2020 = ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-13', '2020-02-11', '2020-02-23', '2020-02-24', '2020-03-20', '2020-04-29', '2020-05-03', '2020-05-04', '2020-05-05', '2020-05-06', '2020-07-23', '2020-07-24', '2020-08-10', '2020-09-21', '2020-09-22', '2020-11-03', '2020-11-23', '2020-12-31'] 
holi_2021 = ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-11', '2021-02-11', '2021-02-23', '2021-03-20', '2021-04-29', '2021-05-03', '2021-05-04', '2021-05-05', '2021-07-19', '2021-08-11', '2021-09-20', '2021-09-23', '2021-10-11', '2021-11-03', '2021-11-23', '2021-12-31']

add_holi_2022 = ['2022-01-01', '2022-01-02', '2022-01-03', '2022-12-31']

@pytest.fixture
def holidays_fixture():
    SytraDay.add_holidays_list('2020', holi_2020)
    SytraDay.add_holidays_list('2021', holi_2020)

def test_keys_holidays(holidays_fixture):
    # you can get tuple if added already
    canget = SytraDay.get_holidays_tuple('2020')
    #print(canget)
    with pytest.raises(StockerError):
        SytraDay.get_holidays_tuple('2022')

def test_init(holidays_fixture):
    # you can create if the class doesn't have holidays
    sday = SytraDay('2010-10-10')
    # but could not step
    with pytest.raises(StockerError):
        sday.day_advance()

    # correct pattern
    sday = SytraDay('2020-07-22')
    assert str(sday) == date(2020, 7, 22).strftime(SytraDay.SFORM)

def test_add_holiday(holidays_fixture):
    
    # add 2022 holidays
    SytraDay.add_holidays_list('2022', add_holi_2022)
    assert '2022' in SytraDay.HOLIDAYS.keys()
    sday = SytraDay('2022-09-09')
    ns = sday.get_nextstr()
    assert ns=='2022-09-12'


def test_day_handling(holidays_fixture):
    sday = SytraDay('2020-07-22')
    nextdate = date(2020, 7, 27)
    prevdate = date(2020, 7, 21)
    
    # no modification sday
    tmp = sday.next_trading()
    assert str(tmp)==str(nextdate)
    tmp = sday.prev_trading()
    assert str(tmp)==str(prevdate)

    # set modification
    sday.day_advance()
    assert str(sday)==str(nextdate)
    sday.day_rewind()
    sday.day_rewind()
    assert str(sday)==str(prevdate)

    # HAPPY NEW YEAR!
    sday = SytraDay('2020-12-30')
    newyear = sday.day_advance()
    assert newyear
