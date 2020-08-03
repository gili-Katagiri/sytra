import pandas as pd
import os
import linecache
from pathlib import Path
from typing import Union, NamedTuple, List, Tuple
import toml
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

    def __init__( self, candday: datetime.date ):
        # if cancdday is not Trading Day, next process works well
        cls = self.__class__
        self._next_update = cls.step_trading(candday, rewind=False)
        self._last_update = cls.step_trading(self._next_update, rewind=True)

    def get_lastupdate(self)-> datetime.date: return self._last_update
    def get_nextupdate(self)-> datetime.date: return self._next_update

    def _next_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._last_update, rewind=False)
    def _pre_trading(self)-> datetime.date:
        return self.__class__.step_trading(self._last_update, rewind=True)

    def _day_advance(self):
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
    STOCK_ROOT: str = '../../stocks'
    PARAMS_FILEPATH: str = '.params'
    PRIMITIVE_INITPATH: str = '.prinit'
    STANDARD_COLUMNS: Tuple[str] = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS: Tuple[str] = ('Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS_JA: Tuple[str] = ('銘柄コード', '始値', '高値', '安値', '現在値', '出来高', '前日比', '残高貸株', '残高融資', '貸借倍率', '逆日歩')

    @classmethod
    def stock_filepath(cls, *args)-> Path:
        path: Path = Path( __file__, cls.STOCK_ROOT )
        for arg in args:
            path = path / str(arg)
        return path.resolve()
    @classmethod
    def filerows(cls, filepath):
        return sum( 1 for _ in open(str(filepath)) )
    @classmethod
    def file_tail( cls, filepath):
        size = cls.filerows(filepath)
        line = linecache.getline( str(filepath), size )
        data = [ s.strip() for s in line.split(',') ]
        return data
    @classmethod
    def follow_init(cls)-> List[int]:
        path=cls.stock_filepath(cls.PRIMITIVE_INITPATH)
        if not path.exists():
            raise FileNotFoundError('Error: {0} is not found.'.format(path))

        stocks = []
        for prifile in path.glob('*.csv'):
            # /path/to/stockroot/flinit/9999.csv -> 9999
            fname = str(prifile).split('/')[-1][0:4]
            # /path/to/stockroot/9999
            codepath = cls.stock_filepath(fname)
            if codepath.exists():
                print('WARNING: Passing {0}, directory is exists.'.format(codepath))
                continue
            os.mkdir(codepath)
            os.rename(str(prifile), str(codepath/'primitive.csv'))
            stocks.append(int(fname))
        return stocks
    
    def __init__(self):
        cls = self.__class__
        filepath = cls.stock_filepath( cls.PARAMS_FILEPATH )
        if not filepath.exists():
            print('WARNING: {0} is NOT exists.'.format(filepath), flush=True)
            days = StockDays( datetime.date.today() )
            self._smp = StockManegerParams( [], days)
        else:
            with open( filepath, mode='r' ) as f:
                tomldic = toml.load(f)
                days = StockDays(datetime.date.fromisoformat(tomldic['stocker']['days']['update']['latest']))
                self._smp = StockManegerParams(tomldic['stocker']['follows'], days)

    def _dump(self):
        cls = self.__class__
        filepath = cls.stock_filepath( cls.PARAMS_FILEPATH )

        days = self.get_markeddays()
        lday, nday = days.get_lastupdate(), days.get_nextupdate()
        
        tomldic = {'stocker': {
                    'follows': self.get_follows(), 
                    'days': {'update':{'latest': str(lday), 'next':str(nday)}}
                }}

        with open( filepath, mode='w') as f:
            toml.dump( tomldic, f)

    def get_follows(self)-> List[int]: return self._smp.follows
    def get_markeddays(self)-> StockDays: return self._smp.marked_days

    def follow_stock( self, stock_code: int):
        cls = self.__class__
        follows = self.get_follows()
        # paths
        dirname = cls.stock_filepath(stock_code)
        filepath = dirname / 'primitive.csv'

        if stock_code in follows:
            raise KeyError('Error: {0} is already followed.'.format(stock_code))
        if not filepath.exists():
            raise FileNotFoundError('Error: You have to prepare {0}.'.format(str(filepath)))

        # read csv
        primitive_df = pd.read_csv( filepath, header=0, dtype=str,\
                names=cls.STANDARD_COLUMNS, encoding='UTF-8' )
        
        lastidx = self.get_markeddays().get_lastupdate().strftime('%Y/%m/%d')
        dfidx = primitive_df.iat[-1, 0]
        if not lastidx == dfidx:
            raise IndexError('Error: this primitive file has not latest values.\n\tlast: {0}, primitive: {1}'.format(lastidx, dfidx))
        
        # compensate missing values
        self.compensation( primitive_df )
        
        # add code 
        follows.append( stock_code )
        
        # mv primitive.csv .primitive.csv & make stock.csv
        os.rename( filepath, dirname/'.primitive.csv' )
        primitive_df.to_csv( dirname / 'stock.csv' )

    def compensation( self, df):
        cls = self.__class__
        col_open = df.columns.get_loc('Open')
        col_close = df.columns.get_loc('Close')

        # get index needed to compensate
        idxs = list( df.query('Open=="-"').index )
        if 0 in idxs:
            raise ValueError('Error: primitive LEAD value is not available!')
        # set the day before close value 
        for idx in idxs:
            val = df.iat[idx-1, col_close]
            df.iloc[idx, col_open:col_close+1] = [ val for _ in range(4) ]

        # datetime index
        df['Date'] = pd.to_datetime( df['Date'] )
        df.set_index( 'Date', inplace=True )
        
        # '-' -> 0 and as float
        for col in cls.STANDARD_COLUMNS[1:]:
            df[col] = df[col].str.replace(',','').replace('-','0').astype('float')

    
    def unfollow_stock( self, stock_code: int):
        cls = self.__class__
        follows = self.get_follows()

        if not stock_code in follows:
            raise KeyError('Error: follows is not having code: {0}.'.format(stock_code))
        
        # paths
        dirname = cls.stock_filepath(stock_code)
        filepath = dirname / 'stock.csv'
        
        # search noname and rename stocks
        cnt = 1
        noname = dirname/'removed1'
        while( noname.exists() ):
            cnt += 1
            noname = dirname/('removed{0}'.format(cnt))
        os.rename( filepath, noname)

        # remove code
        follows.remove(stock_code)

    def itr_follow( self, codes: List[int], defollow=False):
        # define follow or defollow
        proc = self.follow_stock if not defollow else self.unfollow_stock
        failure = []
        for code in codes:
            print('Processing {0}...'.format(code), end='')
            try: proc(code)
            except Exception as e:
                failure.append(code)
                print(e)
            else: print('complete')

        # sort
        self.get_follows().sort()

        return failure

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
        with open( summary_base_path, mode='w', encoding='cp932') as f:
            f.write( update.strftime('%Y-%m-%d') + '\n' )
        summary_base.to_csv( summary_base_path, mode='a',\
                                index=False , encoding='cp932')

    def allocate_init(self) :
        cls = self.__class__
        summary_path = cls.stock_filepath( 'summary.csv' )
        date_str = linecache.getline( str(summary_path), 1 ).strip()
        nextday = self.get_markeddays().get_nextupdate()

        if date_str != nextday.strftime('%Y-%m-%d'):
            raise RuntimeError('Error: summary.csv has un-scheduled day\'s data.')
        
        summary = pd.read_csv( summary_path, skiprows=1, header=0,\
                index_col=cls.RECEPTION_COLUMNS[0], encoding='cp932')
        summary.insert(0, cls.STANDARD_COLUMNS[0], date_str)
        follows = self.get_follows()

        if len( summary.columns ) != len( cls.STANDARD_COLUMNS ):
            raise KeyError('Error: columns are irregal. {0}'.format(summary.columns) )
        
        if len( summary.index ) != len( follows ):
            raise IndexError('Error: stock-code not complete.\ngive:{0}, needs:{1}.'.format(summary.index, follows) )

        return summary, summary_path, date_str

    def allocate( self, summary: pd.DataFrame ):
        cls = self.__class__
        follows = self.get_follows()
        failure = []
        for code in follows:
            
            print('proc: {0}...'.format(code), end='')

            data = summary.loc[[code]]
            last_line = cls.file_tail( cls.stock_filepath( code, 'stock.csv') )

            if not data.iat[0,4] - data.iat[0,6] == float(last_line[4]):
                print('Close Value Error.')
                failure.append(code)
                continue

            data.to_csv( cls.stock_filepath( code, 'stock.csv'),\
                    mode='a', header=False, index=False)
            print('Complete!')

        return failure

    def __str__(self)-> str:
        follows = self.get_follows()
        days = self.get_markeddays()
        s = 'follows: {0}\nmarked days: ({1})'.format( follows, days)
        return s

class StockDataHolder():
    def __init__(self, stock_code: int):
        # may be NamedTuple
        self._stock_code = stock_code
        self.read_stock_csv(stock_code)

    def read_stock_csv(self, stock_code: int)-> pd.DataFrame: 
        path: Path = StockManeger.stock_filepath(stock_code, 'stock.csv')
        if not path.exists():
            raise FileNotFoundError('Error: directry {0}/{1} is not exists.'.format(STOCK_ROOT, stock_code))

        stock_data = pd.read_csv(path,\
                    header=0, names=StockManeger.STANDARD_COLUMNS,\
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
