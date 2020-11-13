import toml
import math
from pathlib import Path
import pandas as pd 

from typing import List, Tuple

from exceptions import StockerError
from util.paths import *
from util.sytraday import *
from analyzer import Analyzer


class StockerFilePath(SytraPath):
    @classmethod
    def sytra_path_init(cls, custom_path: str='')-> Path:
        # __file__ = ~/sytra/lib/stocker/sytrafiles.py
        default_root = Path(__file__ + '/../../../stocks')
        root_path = default_root if custom_path == '' else Path(custom_path)
        root_path = root_path.resolve()
        print('Make stock directory at {0}.'.format(root_path))
        
        root_path.mkdir()
        (root_path/'log').mkdir()
        (root_path/'log'/'trash').mkdir()
        (root_path/'prepare').mkdir()
        (root_path/'holidays').mkdir()

        # write in sytra/env
        return root_path
    # return concrete path
    # get directory and path
    def get_stockpath( self, scode: int, noerror=False):
        return self._get_filepath(scode, noerror=noerror)
    # get directory path
    def get_logpath(self): return self._get_filepath('log')
    def get_trashpath(self): return self.get_logpath()/'trash'
    def get_preparepath(self): return self._get_filepath('prepare')
    def get_holidayspath(self): return self._get_filepath('holidays')
    # get file path
    def get_confpath(self): return self._get_filepath('sytraconf.toml')
    def get_summarypath(self): return self._get_filepath('summary.csv')
    def get_sbasepath(self, noerror=True):
        return self._get_filepath('summary_base.csv', noerror=noerror)
    
# handling files
class StockerFile(StockerFilePath):

    COLUMNS: Tuple[str] = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    RECEPTION_COLUMNS: Tuple[str] = ('Code', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    SBASE_COLUMNS: Tuple[str] = ('銘柄コード', '始値', '高値', '安値', '現在値', '出来高', '前日比', '残高貸株', '残高融資', '貸借倍率', '逆日歩')

    # file <=> dict
    def _load_conf( self )-> dict:
        tomlstr = super().get_confpath().read_text()
        tomldic = toml.loads(tomlstr)
        return tomldic
    def _dump_conf( self, tomldic: dict):
        tomlstr = toml.dumps(tomldic)
        super().get_confpath().write_text(tomlstr)
    
    def _defollow_process(self, stock_code: int):
        # get path
        dname = super().get_stockpath(stock_code)
        # 9999/ -> log/trash/9999
        trashpath = super().get_trashpath()
        newname = trashpath / str(stock_code)
        # rename
        dname.rename(newname)
    
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
        sbase_path.write_text( daystr+'\n', encoding='cp932')
        sbase.to_csv( sbase_path, mode='a', index=False, encoding='cp932')
        return sbase

    # file -> date string, dataframe
    def _get_summary(self, summary_path: Path)-> Tuple[str, pd.DataFrame]:
        # load
        summary_day = summary_path.read_text().split('\n', 1)[0]
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
        for f in holiroot.glob('*.csv'):
            year = f.stem
            holist = self._get_holidays_list(f, int(year))
            SytraDay.add_holidays_list( year, holist)

class Stocker(StockerFile):

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
        envpath.write_text(str(rootpath))

        # call sytra_days_init and get year
        daysdic = SytraDay.sytra_days_init(daystr)
        tomldic = { 'stocker':{ 'follows': follows ,'days': daysdic } }
        tomlstr = toml.dumps(tomldic)

        (rootpath/'sytraconf.toml').write_text(tomlstr)
        

    def __init__( self, rootdir: str):
        # Path.__init__()
        super().__init__(rootdir)
        self._load()

    # utility
    def get_follows_tuple(self)-> Tuple[int]:
        return tuple(self._follows_list)
    def get_lateststr(self)-> str:
        return self._latest_update_day.get_daystr()
    def get_nextdaystr(self)-> str:
        return self._latest_update_day.get_nextstr()
    def _code_in_follows(self, stock_code: int)-> bool:
        return stock_code in self.get_follows_tuple()
    def _check_follow_callable(self)-> bool:
        try: super().get_summarypath()
        except SytraPathError: return True
        return False
    # follow
    def _follow_stock(self, stock_code: int):
        # create 9999/
        dname = super().get_stockpath(stock_code)
        Analyzer.analyzer_init(dname, self.get_lateststr())
        # add stock_code to _follows_list
        self._follows_list.append( stock_code )

    # defollow
    def _defollow_stock(self, stock_code: int):
        # 9999/ -> log/trash/9999/
        self._defollow_process(stock_code)
        # remove stock_code from _follows_list
        self._follows_list.remove(stock_code)

    # prepare/*.csv -> */primitive.csv
    def _follow_deploy(self)-> List[int]:
        path = super().get_preparepath()
        stocks = []
        for f in path.glob('*.csv'):
            # /path/to/stocks/prepare/9999.csv -> 9999
            code = int( f.stem )
            if self._code_in_follows(code):
                print('WARNING: Ignore %d process, which is already followed.'\
                        % (code))
            else:
                # mkdir 9999/ and mv 9999.csv 9999/primitive.csv
                dname = super().get_stockpath(code, noerror=True)
                dname.mkdir()
                f.rename(dname/'primitive.csv')
                stocks.append(code)
        return stocks

    def _iterate_process(self, proc, codes: List[int]):
        failure_list = []
        for code in codes:
            print('Processing %d...' % code, end='')
            try: proc(code)
            except StockerError as e:
                failure_list.append(code)
                print(e)
            else: print('complete')

        return failure_list


    # interfaces
    def follow_interface( self, codes: List[int]=[], defollow: bool=False, deploy: bool=True, force: bool=False, sort: bool=True, **elsekwds):
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
        
        # proc: _follow_stock or _defollow_stock
        proc = self._defollow_stock if defollow else self._follow_stock
        # summary.csv have to be not exits
        if not ( force or self._check_follow_callable() ):
            print('[Warning]: Already summary.csv has prepared!')
            print('If force process, please add -f/--force option.')
            return codes

        # callable check
        for code in codes:
            # follow process need not exists the code in follows: False
            # defollow process need to exists the code in follows: True
            if self._code_in_follows is defollow:
                print('[WARNING]: %d is irregal position.'%(code))
                return codes
        
        # deploy prepare/ with check callable
        if not defollow and deploy:
            print('Deploy the prepare directory ...')
            codes += self._follow_deploy()
        
        # processing
        flist = self._iterate_process( proc, codes )
        if flist: print('[WARNING]: Failuer codes: ', flist)

        # post-process
        if sort: self._follows_list.sort()
        return flist

    def allocate_interface(self):

        # load
        spath = super().get_summarypath()
        daystr, summary = super()._get_summary(spath)
        codes = list(summary.index)

        # check 
        if daystr!=self.get_nextdaystr(): raise StockerError('StockDayError')
        if tuple(codes)!=self.get_follows_tuple():
            raise StockerError('StockKeyError')
        
        # get dmode 
        cdate = SytraDay(daystr)
        dmode = cdate.get_dmode()

        # allocate
        for code, rowx in summary.iterrows():
            # create Analyzer interface
            dpath = super().get_stockpath(code)
            analy = Analyzer(dpath)
            analy.daily_update(cdate.get_daystr(), dmode, rowx)
        
        # post-process
        logpath = super().get_logpath() / (daystr.replace('-',''))
        spath.rename(logpath)
        self._latest_update_day.day_advance()
        
    # create sbase.csv
    def create_sbase(self):
        daystr = self.get_nextdaystr()
        follows = self.get_follows_tuple()
        
        sbase = super()._create_sbase(daystr, follows)
        print(daystr)
        print(sbase.head(1).to_csv(None, index=False))
        print('...')

    # save and load
    def _load(self):
        tomldic = super()._load_conf()
        super()._set_sytra_holidays()
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
