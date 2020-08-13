import linecache
import toml
from pathlib import Path
import pandas as pd 

from typing import List, Tuple

from .sytraday import SytraDay
from .errors import StockerError, StockPathError

class SytraPath():
    @classmethod
    def sytra_path_init(cls, custom_path: str='')-> Path:
        # __file__ = ~/sytra/lib/stocker/sytrafiles.py
        default_root = Path(__file__ + '/../../../stocks')
        root_path = default_root if custom_path == '' else Path(custom_path)
        root_path = root_path.resolve()
        print('Make stock directory at {0}.'.format(root_path))
        
        root_path.mkdir()
        (root_path/'log').mkdir()
        (root_path/'prepare').mkdir()
        (root_path/'holidays').mkdir()

        # write in sytra/env
        return root_path

    # rootdir from sytra/env
    def __init__( self, rootdir: str):
        self._root = Path( rootdir )
        if not self._root.exists():
            raise StockPathError(self._root)

    # abstract path method
    def _get_filepath( self, *args, noerror=False)-> Path:
        path = Path( self._root )
        for arg in args:
            path = path / str(arg)
        if not noerror and not path.exists():
            raise StockPathError(path)
        return path.resolve()

    # return concrete path
    # get directory and path
    def get_stockpath( self, scode: int, target: str='stock.csv', noerror=False):
        filepath = self._get_filepath(scode, target, noerror=noerror)
        dirpath = filepath.parent
        return dirpath, filepath
    # get directory path
    def get_logpath(self): return self._get_filepath('log')
    def get_preparepath(self): return self._get_filepath('prepare')
    def get_holidayspath(self): return self._get_filepath('holidays')
    # get file path
    def get_confpath(self): return self._get_filepath('sytraconf.toml')
    def get_summarypath(self): return self._get_filepath('summary.csv')
    def get_sbasepath(self, noerror=True):
        return self._get_filepath('summary_base.csv', noerror=noerror)
    
    # candidate name to available name
    def get_available_path(self, fname: Path):
        candstem, candsuf = fname.stem, fname.suffix
        candname = fname
        while( fname.exists() ):
            cnt += 1
            candname = (fname.parent) / (candstem+str(cnt)+candsuf)
        return candname


# handling files
class SytraFiles(SytraPath):

    COLUMNS: Tuple[str] = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS: Tuple[str] = ('Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    SBASE_COLUMNS: Tuple[str] = ('銘柄コード', '始値', '高値', '安値', '現在値', '出来高', '前日比', '残高貸株', '残高融資', '貸借倍率', '逆日歩')

    # file <=> dict
    def _load_conf( self )-> dict:
        with super().get_confpath().open() as f:
            tomldic = toml.load(f)
        return tomldic
    def _dump_conf( self, tomldic: dict):
        with super().get_confpath().open(mode='w') as f:
            toml.dump( tomldic, f)
    
    # prepare/*.csv -> */primitive.csv
    def _follow_deploy(self)-> List[int]:
        path = super().get_preparepath()
        stocks = []
        for f in path.glob('*.csv'):
            # /path/to/stocks/prepare/9999.csv -> 9999
            code = int( f.stem )
            dname, fname = super().get_stockpath(code,target='primitive.csv',
                    noerror=True)
            try: dname.mkdir()
            except FileExistsError:
                print('WARNING: Passing {0}, directory already exists.'\
                        .format(dname))
                continue
            f.rename(fname)
            stocks.append(code)
        return stocks
    
    # file->dataframe->dataframe->file
    def _follow_process(self, stock_code: int, latest_str: str):
        # get path
        dname, fname = super().get_stockpath(stock_code, target='primitive.csv')
        # read
        primitive_df = self._get_primitive_df(fname)

        # primitive has latest values
        datestr = primitive_df.iloc[-1]['Date'].replace('/','-')
        if datestr!=latest_str: raise StockerError('StockDayError')

        # compensation and to file
        self.__class__._compensation( primitive_df )
        primitive_df.to_csv( dname/'stock.csv' )
        
        # hide primitive.csv
        fname.replace(dname / '.primitive.csv')

    def _defollow_process(self, stock_code: int, candname: str):
        # get path
        dname, fname = super().get_stockpath(stock_code, target='stock.csv')
        # newname is not always available
        newname = dname / candname
        newname = super().get_available_path(newname)
        # rename stock.csv-> candname
        fname.rename(newname)
    
    # file -> dataframe
    def _get_primitive_df(self, stock_path: Path)-> pd.DataFrame:
        columns = self.__class__.COLUMNS
        # load csv
        primitive_df = pd.read_csv( stock_path, header=0, dtype=str,
                names=columns, encoding='UTF-8')
        return primitive_df

    # primitive dataframe -> available dataframe
    @classmethod
    def _compensation( cls, primitive: pd.DataFrame):
        openid, closeid = cls.COLUMNS.index('Open'), cls.COLUMNS.index('Close')
        # search index with Open=="-" and to List
        idxs = list( primitive.query('Open=="-"').index)
        if 0 in idxs: raise StockerError('StockValueError')
        # set the day before close value
        for idx in idxs:
            val = primitive.iat[idx-1, closeid]
            primitive.iloc[idx, openid: closeid+1] = [val for _ in range(4)]
            
        # Date to Timestamp and set index
        primitive['Date'] = pd.to_datetime( primitive['Date'] )
        primitive.set_index( 'Date', inplace=True)

        # '-' appear Compare and Backword -> 0, all values treated as float
        for col in cls.COLUMNS[1:]:
            primitive[col] = primitive[col].str\
                    .replace(',','').replace('-', '0').astype('float')

    # get file's bottom line
    @classmethod 
    def _filecount( cls, filepath: Path)-> int:
        return sum( 1 for _ in filepath.open() )
    @classmethod
    def _filetail( cls, filepath: Path)-> List[str]:
        size = cls._filecount(filepath)
        line = linecache.getline( str(filepath), size )
        data = [ s.strip() for s in line.split(',') ]
        return data
    
    def _create_sbase(self, daystr: str, follows: Tuple[int])-> pd.DataFrame:
        RCOL = self.__class__.RECEPTION_COLUMNS
        JCOL = self.__class__.SBASE_COLUMNS

        # create dataframe
        sbase = pd.DataFrame(
                [ ['=RSS|\'%d.T\'!%s' % (code, col) for col in JCOL]\
                        for code in follows],
                columns = RCOL
            )

        # get path
        sbase_path = super().get_sbasepath()
        # write
        with sbase_path.open(mode='w', encoding='cp932') as f:
            f.write( daystr+'\n' )
        sbase.to_csv( sbase_path, mode='a', index=False, encoding='cp932')
        return sbase

    # file -> date string, dataframe
    def _get_summary(self, summary_path: Path)-> Tuple[str, pd.DataFrame]:
        # load
        summary_day = linecache.getline( str(summary_path), 1) .strip()
        summary = pd.read_csv( summary_path, skiprows=1, header=0,
                index_col='Code', encoding='cp932')
        summary.insert( 0, 'Date', summary_day )

        return summary_day, summary

    # file -> List
    def _get_holidays_list(self, holipath: Path, year: int) -> List[str]:
        # load
        hddf = pd.read_csv(holipath, header=None)
        holidays = hddf.iloc[:,0].values.tolist()

        # Add as holiday prev 12/31 and next 01/01 to 01/03 certainly
        by, fy = str(year-1), str(year+1)
        holidays += [by+'-12-31',fy+'-01-01',fy+'-01-02',fy+'-01-03']
        return holidays
    # files -> list ->  data
    def _set_sytra_holidays(self)-> List[str]:
        holiroot = super().get_holidayspath()
        addlist = []
        for f in holiroot.glob('*.csv'):
            year = f.stem
            holist = self._get_holidays_list(f, int(year))
            SytraDay.add_holidays_list( year, holist)
            addlist.append(year)
        return addlist

class Stocker(SytraFiles):

    @classmethod
    def stocker_init(cls, rootdir: str='', daystr: str='', follows: List[int]=[], **kwds):
        '''Sytra's init process.
        You have to prepare files which include this and next year's holidays.
        '''
        # define doot directory
        rootpath = super().sytra_path_init(rootdir)
        # define sytra/env
        envpath = Path(__file__+'/../../../env').resolve()
        print('Make env file at %s' % str(envpath))
        with envpath.open(mode='w') as f: f.write(str(rootpath))

        # call sytra_days_init and get year
        daysdic = SytraDay.sytra_days_init(daystr)
        tomldic = { 'stocker':{ 'follows': follows ,'days': daysdic } }
        
        with (rootpath/'sytraconf.toml').open(mode='w') as f:
            toml.dump( tomldic, f)
        

    def __init__( self, rootdir: str):
        # SytraPath.__init__()
        super().__init__(rootdir)
        self._load()

    # save and load
    def _load(self):
        tomldic = super()._load_conf()
        addlist = super()._set_sytra_holidays()
        self._set_bytoml(tomldic)
    def dump(self):
        tomldic = self._to_tomldic()
        super()._dump_conf(tomldic)
    
    # toml <=> instance
    def _set_bytoml( self, tomldic: dict):
        # set follows list
        self._follows_list = tomldic['stocker']['follows']

        # protocol: add holidays before day init
        daystr = tomldic['stocker']['days']['latest']
        self._latest_update_day = SytraDay(daystr)
    def _to_tomldic(self)-> dict:
        return {'stocker':
                    {
                        'follows': self._follows_list,
                        'days': self._latest_update_day.to_tomldic()
                    }
                }
    
    # return str, Not as it is
    def get_follows_tuple(self)-> Tuple[int]:
        return tuple(self._follows_list)
    def get_lateststr(self)-> str:
        return self._latest_update_day.get_daystr()
    def get_nextdaystr(self)-> str:
        return self._latest_update_day.get_nextstr()

    # check
    def _code_in_follows(self, stock_code: int)-> bool:
        return stock_code in self.get_follows_tuple()
    # summary.csv must NOT exists when calls follow process
    def _check_follow_callable(self)-> bool:
        try: super().get_summarypath()
        except StockPathError: return True
        return False

    # follow
    def _follow_stock(self, stock_code: int, **kwds):
        # check stock_code has not been followed
        if self._code_in_follows(stock_code): raise StockerError('StockKeyError')

        super()._follow_process(stock_code, self.get_lateststr())
        
        # add stock_code to _follows_list
        self._follows_list.append( stock_code )
    # defollow
    def _defollow_stock(self, stock_code: int, **kwds):
        # check stock_code has been followed
        if not self._code_in_follows(stock_code): raise StockerError('StockKeyError')

        # 9999/stock.csv go to 9999/renames
        renames = kwds['renames']
        renames = 'rm'+str(stock_code)+'.csv' if renames == '' else renames
        super()._defollow_process(stock_code, renames)

        # remove stock_code by _follows_list
        self._follows_list.remove(stock_code)

    # allocate
    def _allocate_stock(self, stock_code: int, **kwds):
        # get row data from kwds dictionary and to DataFrame
        rowdata = pd.DataFrame( [kwds[str(stock_code)]] )
        # path
        dname, fname = super().get_stockpath(stock_code)

        # rowdata.Close - rowdata.Compare = day before Close
        daybefore = self.__class__._filetail(fname)
        if not rowdata.iat[0,4] - rowdata.iat[0,6] == float(daybefore[4]):
            raise StockerError('StockValueError')

        # write as csv
        rowdata.to_csv( fname, mode='a', header=False, index=False)


    def _iterate_process(self, proc, codes: List[int], options: dict):
        failure_list = []
        for code in codes:
            print('Processing %d...' % code, end='')
            try: proc(code, **options)
            except StockerError as e:
                failure_list.append(code)
                print(e)
            else: print('complete')

        return failure_list


    # interfaces
    def follow_interface( self, codes: List[int]=[], defollow: bool=False, deploy: bool=True, force: bool=False, sort: bool=True, renames: str='', **elsekwds):
        """
        The reason for preparing dictionary:options is to process functions _follow_stock and _defollow_stock as same arguments.
        Options included _follow_stock:
            None
        Options included _defollow_stock:
            str renames: new name string for stock.csv 

        Not included options:
            bool deploy: if true, call super()._follow_deploy() and ADD codes
            bool force: execute process regardless of _check_follow_callable()
            bool sort: Sort _follows_list at last.

        As default, call _follow_deploy and _follow_stock at codes.
        """

        proc = self._defollow_stock if defollow else self._follow_stock
        options = {'renames': renames}

        if not ( force or self._check_follow_callable() ):
            print('Already summary.csv has prepared!')
            print('If force process, please add -f/--force option.')
            return codes
        
        if not defollow and deploy:
            print('Deploy the prepare directory.')
            codes += super()._follow_deploy()
        
        flist = self._iterate_process( proc, codes, options )
        if flist: print('failuer: ', flist)

        if sort: self._follows_list.sort()

        return flist

    def allocate_interface(self, **kwds):
        # load
        spath = super().get_summarypath()
        daystr, summary = super()._get_summary(spath)
        codes = list(summary.index)
        # check 
        if daystr!=self.get_nextdaystr(): raise StockerError('StockDayError')
        if tuple(codes)!=self.get_follows_tuple():
            raise StockerError('StockKeyError')

        # dictionaly's key must be string!
        # summary_dic = { "code1": pd.Series(Open, High, ...),
        #                 "code2": pd.Series(Open, High, ...), ...}
        summary.index = summary.index.astype(str)
        summary_dic = summary.T.to_dict(orient='series')
        self._iterate_process( self._allocate_stock, codes, summary_dic)
        
        logpath = super().get_logpath() / (daystr.replace('-',''))
        spath.rename(logpath)

        self._latest_update_day.day_advance()
        
    # create sbase.csv
    def create_sbase(self, **kwds):
        daystr = self.get_nextdaystr()
        follows = self.get_follows_tuple()
        
        sbase = super()._create_sbase(daystr, follows)
        print(daystr)
        print(sbase.head(1).to_csv(None, index=False))
        print('...')
