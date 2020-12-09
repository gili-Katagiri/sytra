import datetime
from typing import Tuple, List

from .errors import StockerError

class SytraDay():
    SFORM = '%Y-%m-%d'
    HOLIDAYS: dict = {}
    
    # proc in sytra init
    @classmethod
    def sytra_days_init( cls, day: str)-> dict:
        # initial date
        latest = datetime.date.today()
        if day != '': 
            latest = datetime.date.fromisoformat(day)
        latest_str = latest.isoformat()
        
        return {'latest': latest_str}
    
    # SytraDay expect to have this year's holidays list until call init.
    @classmethod
    def add_holidays_list( cls, year: str, holidays: List[str]):
        cls.HOLIDAYS[year] = tuple(holidays)
    @classmethod
    def get_holidays_tuple( cls, year: int):
        keyyear = str(year)
        if not keyyear in cls.HOLIDAYS: raise StockerError('StockDayError')
        return cls.HOLIDAYS[str(year)]

    @classmethod
    def step_trading( cls, day: datetime.date, rewind=False)-> datetime.date:

        step = 1 if not rewind else -1
        cand = day+datetime.timedelta(days=step)

        holidays = cls.get_holidays_tuple(day.year)

        while cand.weekday()>=5 or cand.strftime(cls.SFORM) in holidays:
            cand = cand+datetime.timedelta(days=step)

        return cand

    def __init__( self, day: str):
        self._set_fromstr(day, check=False)

    # Any other class couldn't change date
    def _set_fromstr( self, day: str, check=True)-> bool: 
        day = datetime.date.fromisoformat(day)
        return self._set_fromdate(day, check)
    def _set_fromdate( self, day: datetime.date, check=True)-> bool:
        newyear = False
        if check and day.year == self._day.year+1:
            newyear = True
        self._day = day
        return newyear
    # And Don't allow to give value as date
    def get_daystr(self)-> str:
        str_form = self.__class__.SFORM
        return self._day.strftime(str_form)
    def get_nextstr(self)-> str:
        str_form = self.__class__.SFORM
        return self.next_trading().strftime(str_form)
    
    # day handling
    def next_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._day, rewind=False)
    def prev_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._day, rewind=True)
    def day_advance(self)-> bool:
        nextday = self.next_trading()
        return self._set_fromdate(nextday)
    def day_rewind(self)-> bool:
        prevday = self.prev_trading()
        return self._set_fromdate(prevday)

    def to_tomldic(self)-> dict:
        return {'latest': self.get_daystr(), 'next': self.get_nextstr()}
    def __str__(self):
        return self.get_daystr()
