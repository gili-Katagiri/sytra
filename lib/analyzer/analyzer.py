import pandas as pd
import toml

from pathlib import Path

from exceptions import SytraException
from util.paths import SytraPath, SytraPathError
from util.sytraday import SytraDay

from .stems.bufstem import BufStemPlanter
from .stems.paf import PaFClosePlanter

class AnalyzerError(SytraException):
    pass

class AnalyzerFilePath(SytraPath):
        
    # unique file path
    # lib/analyzer/.defaultconf.toml
    @classmethod
    def _hideget_default_confpath(self):
        return Path(__file__ + '/../.defaultconf.toml').resolve(strict=True)


    # provide 9999/* paths
    def get_stockpath(self, noerror=False):
        return self._get_filepath('stock.csv')
    def get_primitivepath(self, noerror=False):
        return self._get_filepath('primitive.csv')
    def get_confpath(self, noerror=False):
        return self._get_filepath('analyconf.toml', noerror=noerror)



class AnalyzerFile(AnalyzerFilePath):
    ROOT_COLUMNS = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 
                    'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    @classmethod
    def _analy_file_init(cls, rootpath: Path, ltdate: str):
        # primitive.csv -> .primitive.csv, stock.csv
        cls.follow_process(rootpath, ltdate)

        # prepare analyconf.toml
        defconf = super()._hideget_default_confpath().read_text()
        (rootpath/'analyconf.toml').write_text(defconf)

    @classmethod
    def follow_process(cls, rootpath: Path, ltdate: str):
        # read primitive and hide file
        prpath = rootpath/'primitive.csv'
        prdf = cls.get_primitivedata(prpath)
        # date check ltdate: latest trade date string
        # primitive's date: YYYY/mm/dd
        datestr = prdf.iat[-1, 0].replace('/', '-')
        if datestr!=ltdate: raise AnalyzerError('irregal date error.')
        # drop missing row and values, set index, dtype='float'
        cls.compensate(prdf)
        # save as 9999/stocks.csv
        prdf.to_csv( rootpath/'stock.csv' )
        prpath.rename(rootpath/'.primitive.csv')

    # read 9999/primitive.csv
    @classmethod
    def get_primitivedata(cls, prpath):
        cols = cls.ROOT_COLUMNS
        prim_df = pd.read_csv(
            prpath, header=0, dtype=str, names=cols, encoding='UTF-8'
        )
        return prim_df
    
    @classmethod
    def compensate(cls, prdf):
        # Open, High, Low, Close, ...
        cols = cls.ROOT_COLUMNS
        openid, closeid = cols.index('Open'), cols.index('Close')
        # search index with Open=='-', into list
        idxs = list( prdf.query('Open=="-"').index )
        if 0 in idxs: raise AnalyzerError('NaN at df.loc[0]')
        # set the day before close value
        for idx in idxs:
            val = prdf.iat[idx-1, closeid]
            # fill values from Open to Close with Close value at the day before
            prdf.iloc[idx, openid: closeid+1] = [ val for _ in range(4) ]
        
        # date to timestamp and set index
        prdf['Date'] = pd.to_datetime( prdf['Date'] )
        prdf.set_index( 'Date', inplace=True )

        # values treated as float
        for col in cols[1:]:
            prdf[col] = \
                prdf[col].str.replace(',','').replace('-', '0').astype('float')


    # read 9999/stock.csv
    def get_stockdata(self)-> pd.DataFrame:

        stock_path = self.get_stockpath()
        stock_df = pd.read_csv(
            stock_path, header=0, index_col='Date', parse_dates=True, dtype=float
        )

        return stock_df

    def _load_conf(self):
        # readpath
        try: tomlpath = self.get_confpath()
        # case: config file is not exists
        except SytraPathError:
            #print('-----Start-up Analyzer for the first time-----')
            raise SytraPathError
            #tomlpath = self._hideget_default_confpath()

        # toml load
        with tomlpath.open() as f: tomldic = toml.load(f)
        return tomldic


class Analyzer(AnalyzerFile):

    MSG_dict: dict = {
        'buffer' : BufStemPlanter, 
        'pafclose': PaFClosePlanter
    }

    @classmethod
    def analyzer_init(cls, rootpath: Path, ltdate: str):
        super()._analy_file_init(rootpath, ltdate)


    def __init__(self, rootdir: Path):
        # define directory structure
        super().__init__(rootdir)

        # read stock.csv
        #self._stockdata = super().get_stockdata()
        # config load
        tomldic = super()._load_conf()
        # keys: dic_keys include classid. ex) ['buffer', 'pafclose', ... ]
        self._config, self._useless = dict(), dict()
        for msgkey, stemconf in tomldic.items():
            if stemconf['validity']:
                self._config[msgkey] = stemconf
            else:
                self._useless[msgkey] = stemconf

        # planting Multi-Stem Generator
        self._msglist = self.planting()


    def planting(self):
        # Multi-Stem Generator instance list
        msglst = []
        # make instances from MSG
        for classid, conf in self._config.items():
            # idetify the class, extends Multiple-Stem Genrator
            MSG = self.__class__.MSG_dict[classid]
            # stem root directory
            msg_path = self._get_filepath(classid)
            # make instance
            msg = MSG(msg_path, conf['planting'], conf['branching'])
            # append
            msglst.append(msg)

        return msglst

    # rowdata from summary.csv 
    def daily_update(self, rowname, dmode, rowdata):
        for msg in self._msglist:
            msg.stems_update(rowname, dmode, rowdata)



