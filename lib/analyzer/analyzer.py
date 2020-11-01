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
    def get_confpath(self, noerror=False):
        return self._get_filepath('analyconf.toml', noerror=noerror)



class AnalyzerFile(AnalyzerFilePath):
    ROOT_COLUMNS = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 
                    'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    # read 9999/primitive.csv
    @classmethod
    def get_primitivedata(cls, prpath):
        cols = cls.ROOT_COLUMNS
        prim_df = pd.read_csv(
            prpath, header=0, dtype=str, names=cols, encoding='UTF-8'
        )
        return prim_df
    
    # read 9999/stock.csv
    def get_stockdata(self)-> pd.DataFrame:
        stock_path = self.get_stockpath()
        stock_df = pd.read_csv(
            stock_path, header=0, index_col='Date', parse_dates=True, dtype=float
        )
        return stock_df

    def _load_conf(self):
        # readpath
        tomlpath = self.get_confpath()
        # toml load
        with tomlpath.open() as f: tomldic = toml.load(f)
        return tomldic

class AnalyzerBase(AnalyzerFile):

    MSG_dict: dict = {
        'buffer' : BufStemPlanter, 
        'pafclose': PaFClosePlanter
    }

    @classmethod
    def _analy_init(cls, rootpath: Path, ltdate: str):
        # primitive.csv -> .primitive.csv, stock.csv
        cls.follow_process(rootpath, ltdate)

        # prepare analyconf.toml
        defconf = super()._hideget_default_confpath().read_text()
        (rootpath/'analyconf.toml').write_text(defconf)

    @classmethod
    def follow_process(cls, rootpath: Path, ltdate: str):
        # read primitive and hide file
        prpath = rootpath/'primitive.csv'
        prdf = super().get_primitivedata(prpath)
        # date check ltdate: latest trade date string
        # primitive's date: YYYY/mm/dd
        datestr = prdf.iat[-1, 0].replace('/', '-')
        if datestr!=ltdate: raise AnalyzerError('irregal date error.')
        # drop missing row and values, set index, dtype='float'
        stckdf = cls.compensate(prdf)
        # save as 9999/stocks.csv
        stckdf.to_csv( rootpath/'stock.csv' )
        prpath.rename(rootpath/'.primitive.csv')

    @classmethod
    def compensate(cls, prdf):
        # return copy, default deep=True
        stckdf = prdf.copy()
        # Open, High, Low, Close, ...
        cols = cls.ROOT_COLUMNS
        openid, closeid = cols.index('Open'), cols.index('Close')
        # search index with Open=='-', into list
        idxs = list( stckdf.query('Open=="-"').index )
        if 0 in idxs: raise AnalyzerError('NaN at df.loc[0]')
        # set the day before close value
        for idx in idxs:
            val = stckdf.iat[idx-1, closeid]
            # fill values from Open to Close with Close value at the day before
            stckdf.iloc[idx, openid: closeid+1] = [ val for _ in range(4) ]
        
        # date to timestamp and set index
        stckdf['Date'] = pd.to_datetime( stckdf['Date'] )
        stckdf.set_index( 'Date', inplace=True )

        # values treated as float
        for col in cols[1:]:
            stckdf[col] = \
                stckdf[col].str.replace(',','').replace('-', '0').astype('float')
        return stckdf


    # AnalyzerFile instance used for checking the settings are correct or not,
    # or preparing directory for stem whose validity is True.
    def __init__(self, rootdir: Path):
        super().__init__(rootdir)
        # config load
        tomldic = self._load_conf()
        # keys: dic_keys include classid. ex) ['buffer', 'pafclose', ... ]
        self._config, self._useless = dict(), dict()
        for msgkey, stemconf in tomldic.items():
            if stemconf['validity']:
                self._config[msgkey] = stemconf
            else:
                self._useless[msgkey] = stemconf
        # read stock.csv
        self._stockdata = super().get_stockdata()


    # make MSG directory and datafiles by p-planting, EXCLUDE branch columns
    def _planting_init(self):
        # create MSG's directory 9999/buffer/ 9999/pafclose/
        for classid, msgconf in self._config.items():
            # get class extended Multi-Stem Generator class
            MSG = self.__class__.MSG_dict[classid]
            # decide stem root directory
            msg_path = super()._get_filepath(classid, noerror=True)
            pconf = msgconf['planting']
            # call MSG init
            # stockdata from stock.csv, parsed_date index
            msg_path.mkdir()
            MSG._plant_file_init(msg_path, pconf, self._stockdata)


class Analyzer(AnalyzerBase):

    @classmethod
    def analyzer_init(cls, rootpath: Path, ltdate: str):
        # 9999/stock.csv, 9999/analyconf.toml
        super()._analy_init(rootpath, ltdate)


    def __init__(self, rootdir: Path):
        # define directory structure
        super().__init__(rootdir)
        # planting need to read _X_df from datafiles
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

