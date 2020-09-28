import pandas as pd
import toml

from pathlib import Path


from exceptions import SytraException
from util.paths import SytraPath
from util.sytraday import SytraDay


class AnalyzerError(SytraException):
    pass

class AnalyzerFilePath(SytraPath):

    # override to raise AnalyzerError
    def _get_filepath(self, *args, noerror=False):
        try: filepath = super()._get_filepath(*args, noerror=noerror)
        except SytraPathError(): raise AnalyzerError

        return filepath
    

    # provide 9999/* paths
    def get_stockpath(self): return self._get_filepath('stock.csv')
    def get_confpath(self, noerror=False):
        return self._get_filepath('analyconf.toml', noerror=noerror)


    # unique file path
    # lib/analyzer/.defaultconf.toml
    def _hideget_default_confpath(self):
        return Path(__file__ + '../.defaultconf.toml').resolve(strict=True)

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
        except AnalyzerError():
            print('-----Start-up Analyzer for the first time-----')
            tomlpath = self._hideget_default_confpath()

        # toml load
        with tomlpath.open() as f: tomldic = toml.load(f)
        return tomldic

    def _dump_conf(self, tomldic):
        with super().get_confpath(noerror=True).open(mode='w') as f:
            toml.dump(tomldic,f)


class Analyzer(AnalyzerFile):

    def __init__(self, rootdir: Path):

        super().__init__(rootdir)
        self._load()

        self._stock_df = self.get_stock_data()

    def _load(self):
        tomldic = super()._load_conf()
        self._set_by_dict(tomldic)

    def dump(self):
        tomldic = self._to_tomldic()
        super()._dump_conf(tomldic)

    def _set_by_dict(self, tomldic):
        pass
    def _to_tomldic(self):
        pass


