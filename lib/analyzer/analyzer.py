import pandas as pd
import toml

from pathlib import Path

from exceptions import SytraException
from util.paths import SytraPath, SytraPathError
from util.sytraday import SytraDay

from .stems.paf import PaFClosePlanter

class AnalyzerError(SytraException):
    pass

class AnalyzerFilePath(SytraPath):
    
    '''
    # override to raise AnalyzerError
    def _get_filepath(self, *args, noerror=False):
        try: filepath = super()._get_filepath(*args, noerror=noerror)
        except SytraException(): raise AnalyzerError()

        return filepath
    '''

    # provide 9999/* paths
    def get_stockpath(self): return self._get_filepath('stock.csv')
    def get_confpath(self, noerror=False):
        return self._get_filepath('analyconf.toml', noerror=noerror)


    # unique file path
    # lib/analyzer/.defaultconf.toml
    def _hideget_default_confpath(self):
        return Path(__file__ + '/../.defaultconf.toml').resolve(strict=True)

class AnalyzerFile(AnalyzerFilePath):
    
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
            print('-----Start-up Analyzer for the first time-----')
            tomlpath = self._hideget_default_confpath()

        # toml load
        with tomlpath.open() as f: tomldic = toml.load(f)
        return tomldic

    def _dump_conf(self, tomldic):
        with super().get_confpath(noerror=True).open(mode='w') as f:
            toml.dump(tomldic,f)


class Analyzer(AnalyzerFile):

    MSG_dict: dict = {
        'pafclose': PaFClosePlanter
    }

    def __init__(self, rootdir: Path):
        # define directory structure
        super().__init__(rootdir)
        # load analy.conf
        self._msg_classid = []
        self._msg_config = []
        # fill these
        self._load()

        self._msg_list = self.plant()

    # rowdata from summary.csv 
    def daily_update(self, rowname, rowdata):
        
        for msg in self._msg_list:
            msg.stems_update(rowname, rowdata)
        

    def plant(self):
        # Multi-Stem Generator instance list
        msglst = []
        # make instances from MSG
        for idx, classid in enumerate(self._msg_classid):
            # idetify the class, extends Multiple-Stem Genrator
            MSG = self.__class__.MSG_dict[classid]
            # stem root directory
            msg_path = self._get_filepath(classid)

            # stem data file
            conf = self._msg_config[idx]['planting']
            datafiles = conf['datafiles']
            p_planting = conf.get('p-planting', [])
            # make instance
            msg = MSG(msg_path, datafiles, *p_planting)

            # append
            msglst.append(msg)
        return msglst
        

    def _load(self):
        self._stock_data = super().get_stock_data()
        tomldic = super()._load_conf()
        self._set_by_dict(tomldic)

    def dump(self):
        tomldic = self._to_tomldic()
        super()._dump_conf(tomldic)

    def _set_by_dict(self, tomldic):
        # keys: dic_keys include classid. ex) ['buffer', 'pafclose', ... ]
        for msgkey in tomldic.keys():
            if tomldic[msgkey]['validity']:
                # add classid which class should be updated
                self._msg_classid.append(msgkey)
                self._msg_config.append(tomldic[msgkey])

    def _to_tomldic(self):
        pass


