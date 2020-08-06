import datetime
from typing import Tuple, List

class SytraDay():
    SFORM = '%Y-%m-%d'
    _HOLIDAYS: dict = {}
    
    # proc in sytra init
    @classmethod
    def sytra_days_init( cls, choli: List[str], nholi: List[str],
            day=None)-> Tuple[str]:
        
        # initial date
        latest = datetime.date.today()
        if day is not None: 
            latest = datetime.date.fromisoformat(day)
        latest_str = latest.isoformat()
    
        # add holidays for this and next year
        cls.add_holiday_list( latest.year, choli)
        cls.add_holiday_list( latest.year+1, nholi)
        
        # make instance to call to_tomldic function
        inst = cls(latest_str)

        return inst.to_tomldic()
    
    # SytraDay constructor need existance of _HOLIDAYS
    @classmethod
    def set_holidays_dict( cls, dholi: dict):
        cls._HOLIDAYS = dholi

    @classmethod
    def add_holiday_list( cls, year: int, holidays: List[str]):
        cls._HOLIDAYS[str(year)] = tuple(holidays)

    @classmethod
    def _is_holiday( cls, day: datetime.date, holidays: List[str])-> bool:
        return day.weekday()>=5 or day.strftime(cls.SFORM) in holidays

    @classmethod
    def step_trading( cls, day: datetime.date, rewind=False)-> datetime.date:

        step = 1 if not rewind else -1
        cand = day+datetime.timedelta(days=step)

        holidays = cls._HOLIDAYS[str(day.year)]

        while cls._is_holiday(cand, holidays):
            cand = cand+datetime.timedelta(days=step)

        return cand

    def __init__( self, day: str):
        year = day.split('-')[0]
        if not year in self.__class__._HOLIDAYS: raise KeyError
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
        return {'latest': self.get_daystr(), 
                'holidays': self.__class__._HOLIDAYS} 
    def __str__(self):
        return self.get_daystr()
