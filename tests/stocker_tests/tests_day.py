import pytest
from lib.stocker.sytraday import SytraDay
import toml
from datetime import date

holi_2020 = ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-13', '2020-02-11', '2020-02-23', '2020-02-24', '2020-03-20', '2020-04-29', '2020-05-03', '2020-05-04', '2020-05-05', '2020-05-06', '2020-07-23', '2020-07-24', '2020-08-10', '2020-09-21', '2020-09-22', '2020-11-03', '2020-11-23', '2020-12-31'] 
holi_2021 = ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-11', '2021-02-11', '2021-02-23', '2021-03-20', '2021-04-29', '2021-05-03', '2021-05-04', '2021-05-05', '2021-07-19', '2021-08-11', '2021-09-20', '2021-09-23', '2021-10-11', '2021-11-03', '2021-11-23', '2021-12-31']

add_holi_2022 = ['2022-01-01', '2022-01-02', '2022-01-03', '2022-12-31']

# toml_dic['holidays'] is dict! So any modification refrected!
# but toml_dic['lates'] is string!
@pytest.fixture
def toml_fixture():
    toml_dic = SytraDay.sytra_days_init(holi_2020, holi_2021)
    print('\n', toml_dic['latest'])
    print('years: ', toml_dic['holidays'].keys())
    yield toml_dic

def test_keys_toml(toml_fixture):
    toml_dic = toml_fixture
    assert 'latest' in toml_dic
    assert '2020' in toml_dic['holidays']
    assert '2021' in toml_dic['holidays']
    assert not '2022' in toml_dic['holidays']

def test_init(toml_fixture):
    dholi = toml_fixture['holidays']
    
    # HOLIDAY is EMPTY pattern
    SytraDay._HOLIDAY = {}
    with pytest.raises(KeyError):
        dsday = SytraDay('2010-11-11')

    # construct day out of range
    SytraDay.set_holidays_dict(dholi)
    with pytest.raises(KeyError):
        dsday = SytraDay('2010-11-11')
    
    # correct pattern
    sday = SytraDay(toml_fixture['latest'])
    today = date.today()
    assert str(sday) == str(today)

def test_add_holiday(toml_fixture):
    # failer construction until add 2022's holidays
    with pytest.raises(KeyError):
        dsday = SytraDay('2022-09-09')
    
    # add 2022 holidays
    SytraDay.add_holiday_list(2022, add_holi_2022)
    assert '2022' in toml_fixture['holidays'].keys()
    sday = SytraDay('2022-09-09')

def test_day_handling(toml_fixture):
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
