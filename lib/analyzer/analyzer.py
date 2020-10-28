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
    def get_stockpath(self): return self._get_filepath('stock.csv')
    def get_confpath(self, noerror=False):
        return self._get_filepath('analyconf.toml', noerror=noerror)



class AnalyzerFile(AnalyzerFilePath):
    
    @classmethod
    def _analy_path_init(cls, rootpath: Path):
        # prepare analyconf.toml
        defconf = cls._hideget_default_confpath().read_text()
        (rootpath/'analyconf.toml').write_text(defconf)

        # Buffering directorys
        bufpath = rootpath/'buffer'
        bufpath.mkdir()
        (bufpath/'daily.csv').symlink_to(rootpath/'stock.csv')
        (bufpath/'weekly.csv').touch()
        (bufpath/'monthly.csv').touch()


    # read 9999/stock.csv
    def get_stock_data(self)-> pd.DataFrame:

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

    def __init__(self, rootdir: Path):
        # define directory structure
        super().__init__(rootdir)

        # read stock.csv
        self._stock_data = super().get_stock_data()
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
        # rowname-> dmode?: dmode made in Stocker
        #dmode = 0b111
        for msg, conf in zip(self._msglist, self._config.values()):
            # branching 
            #bglist = msg.branching(dmode, conf['branching'])
            # update stems main data
            msg.stems_update(rowname, dmode, rowdata)
            #msg.stems_update(rowname, rowdata, [])


        
