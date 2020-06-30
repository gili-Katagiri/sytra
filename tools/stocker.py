import pandas as pd
import os
import linecache
import shutil
from pathlib import Path
from typing import Union, NamedTuple, List, Tuple
import pickle
import datetime

class StockDays():
    @classmethod
    def step_trading(cls, day: datetime.date, rewind=False)-> datetime.date:
        step = 1 if not rewind else -1
        target: datetime.date = day + datetime.timedelta(days=step)
        holidays: List[str] = cls.get_holidays(target.year)
        while target.weekday()>=5 or target.strftime('%Y-%m-%d') in holidays:
            target = target+datetime.timedelta( days=step )
        return target

    @classmethod
    def get_holidays(cls, year: int) -> List[str]:
        hddf: pd.DataFrame = pd.read_csv(\
                StockManeger.stock_filepath('holidays', str(year)+'.csv' ),\
                header=None\
            )
        holidays: List[str] = hddf.iloc[:,0].values.tolist()
        # As an Exception 12/31 - 01/03 certainly
        by,fy = str(year-1), str(year+1)
        holidays += [by+'-12-31', fy+'-01-01', fy+'-01-02', fy+'-01-03']
        return holidays

    def __init__( self, lastday: datetime.date ):
        self._last_update = lastday
        self._next_update = self._next_trading()

    def get_lastupdate(self)-> datetime.date: return self._last_update
    def get_nextupdate(self)-> datetime.date: return self._next_update

    def _next_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._last_update, rewind=False)
    def _pre_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._last_update, rewind=True)

    def _day_update(self):
        self._last_update = self._next_update
        self._next_update = self._next_trading()
    
    def _day_rewind(self):
        self._next_update = self._last_update
        self._last_update = self._pre_trading()

    def __str__(self)-> str:
        form = '%Y-%m-%d'
        s = 'last update: {0}, next update: {1}'.format(\
                self.get_lastupdate().strftime(form),\
                self.get_nextupdate().strftime(form)
            )
        return s

class StockManegerParams(NamedTuple):
    follows: List[int]
    marked_days: StockDays

class StockManeger():
    STOCK_ROOT: str = './tests/stocks'
    PARAMS_FILEPATH: str = '.params'
    STANDARD_COLUMNS: Tuple[str] = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS: Tuple[str] = ('Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS_JA: Tuple[str] = ('銘柄コード', '始値', '高値', '安値', '終値', '出来高', '前日比', '貸株残高', '融資残高', '貸株倍率', '逆日歩')

    @classmethod
    def stock_filepath(cls, *args)-> Path:
        path: Path = Path( cls.STOCK_ROOT )
        for arg in args:
            path = path / str(arg)
        return path.resolve()
    
    def __init__(self):
        cls = self.__class__
        filepath = cls.stock_filepath( cls.PARAMS_FILEPATH )
        if not filepath.exists():
            print('WARNING: {0} is NOT exists.'.format(filepath), flush=True)
            days = StockDays( datetime.date.today() )
            self._smp = StockManegerParams( [], days)
        else:
            with open( filepath, mode='rb' ) as f:
                self._smp = pickle.load(f)

    def _dump(self):
        cls = self.__class__
        filepath = cls.stock_filepath( cls.PARAMS_FILEPATH )
        with open( filepath, mode='wb') as f:
            pickle.dump( self._smp, f)

    def get_follows(self)-> List[int]: return self._smp.follows
    def get_markeddays(self)-> StockDays: return self._smp.marked_days

    def follow_stock( self, stock_code: int):
        cls = self.__class__
        follows = self.get_follows()

        if stock_code in follows:
            raise KeyError('{0} is already followed.'.format(stock_code))

        dirname = cls.stock_filepath(stock_code)
        path = dirname / 'primitive.csv'
        if not path.exists():
            raise FileNotFoundError('Error: You have to prepare {0}.'.format(str(path)))
        primitive_df = pd.read_csv( path, header=0, dtype=str,\
                names=cls.STANDARD_COLUMNS, index_col=cls.STANDARD_COLUMNS[0],\
                parse_dates=True, encoding='UTF-8' )

        lastidx = self.get_markeddays().get_lastupdate()
        dfidx = primitive_df.index[-1]
        if not lastidx == dfidx:
            raise IndexError('this primitive file has not latest values.\n\tlast" {0}, primitive: {1}'.format(lastidx, dfidx))

        for col in cls.STANDARD_COLUMNS[1:]:
            primitive_df[col] = primitive_df[col].str\
                    .replace(',','').replace('-','0').astype('float')
        
        follows.append( stock_code )
        os.rename( path, dirname/'.primitive.csv' )
        primitive_df.to_csv( dirname / 'stock.csv' )
    
    def unfollow_stock( self, stock_code: int):
        follows = self.get_follows()

        if not stock_code in follows:
            raise KeyError('follows is not having code: {0}.'.format(stock_code))

        # stock.csv -> primitive.csv ?
        follows.remove(stock_code)
        self._dump()

    def make_summarybase(self):
        cls = self.__class__
        update = self.get_markeddays().get_nextupdate()
        follows = self.get_follows()

        summary_base = pd.DataFrame(
                [
                    ['=RSS|\'{0}.T\'!{1}'.format( code, value) \
                        for value in cls.RECEPTION_COLUMNS_JA ] \
                    for code in follows
                ],\
                columns = cls.RECEPTION_COLUMNS
            )
        summary_base_path = cls.stock_filepath( 'summary_base.csv' )
        with open( summary_base_path, mode='w') as f:
            f.write( update.strftime('%Y-%m-%d') + '\n' )
        summary_base.to_csv( summary_base_path, mode='a', index=False )

    def allocate(self):
        cls = self.__class__
        summary_path = cls.stock_filepath( 'summary.csv' )
        date_str = linecache.getline( str(summary_path), 1 ).strip()
        nextday = self.get_markeddays().get_nextupdate()

        if date_str != nextday.strftime('%Y-%m-%d'):
            raise RuntimeError('summary.csv has un-scheduled day\'s data.')
        
        summary = pd.read_csv( summary_path, skiprows=1, header=0,\
                index_col=cls.RECEPTION_COLUMNS[0], encoding='UTF-8')
        summary.insert(0, cls.STANDARD_COLUMNS[0], date_str)
        follows = self.get_follows()

        if len( summary.columns ) != len( cls.STANDARD_COLUMNS ):
            raise KeyError(
                    'columns are irregal. {0} =? {1}'.format(
                        summary.columns, cls.STANDARD_COLUMNS
                    )
                )
        
        if len( summary.index ) != len( follows ):
            raise IndexError(
                    'stock-code not complete.\ngive:{0}, needs:{1}.'.format(
                        summary.index, follows
                    )
                )

        for code in follows:
            summary.loc[[code]].to_csv( cls.stock_filepath( code, 'stock.csv'),\
                    mode='a', header=False, index=False)
        logpath = cls.stock_filepath( 'log', date_str.replace('-','') )
        shutil.move( summary_path, logpath )
        
        self.get_markeddays()._day_update()
        self._dump()

    def __str__(self)-> str:
        follows = self.get_follows()
        days = self.get_markeddays()
        s = 'follows: {0}\nmarked days: ({1})'.format( follows, days)
        return s

STOCK_MANEGER = StockManeger()

class StockDataHolder():
    def __init__(self, stock_code: int):
        # may be NamedTuple
        self._stock_code = stock_code
        self.read_stock_csv(stock_code)

    def read_stock_csv(self, stock_code: int)-> pd.DataFrame: 
        sm = STOCK_MANEGER
        path: Path = sm.stock_filepath(stock_code, 'stock.csv')
        if not path.exists():
            raise FileNotFoundError('Error: directry {0}/{1} is not exists.'.format(STOCK_ROOT, stock_code))

        stock_data = pd.read_csv(path,\
                    header=0, names=sm.STANDARD_COLUMNS,\
                    index_col='Date', parse_dates=True,\
                    dtype='float', encoding='UTF-8'
            )

        self._dataframe = stock_data

    def get_dataframe(self)-> pd.DataFrame: 
        return self._dataframe

    def get_part(self, start: Union[int, str, None]=None, end: Union[int, str, None]=None) -> pd.DataFrame:
        return self._dataframe[start:end]

    def __len__(self)-> int:
        return len(self._dataframe)
    def __str__(self)-> str:
        s = 'stock code:{0}\n'.format(self._stock_code)
        s +=str(self._dataframe)
        return s
