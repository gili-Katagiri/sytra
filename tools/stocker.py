import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union

STOCK_ROOT = './tests/stocks'
COLUMNS = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Compare')

class StockDataHolder():
    def __init__(self, stock_code: int, start_year: int, finish_year: int):
        self._stock_code = stock_code
        self._start_year, self._finish_year = start_year, finish_year
        self.read_stock_csv(stock_code, start_year, finish_year)

    def read_stock_csv(self, stock_code: int, start_year: int, finish_year: int)-> pd.DataFrame: 
        path: Path = Path(STOCK_ROOT, str(stock_code)).resolve()
        if not path.exists():
            raise FileNotFoundError('Error: directry {0}/{1} is not exists.'.format(STOCK_ROOT, stock_code))
        stock_data = pd.DataFrame()
        for i in range( start_year, finish_year+1 ):
            filename: Path = path / ( str(i)+'.csv' )
            stock_data = stock_data.append(
                pd.read_csv( filename, header=0, dtype=str, names=COLUMNS, index_col='Date', parse_dates=True, encoding='UTF-8')
            )

        for col in COLUMNS[1:]:
            stock_data[col] = stock_data[col].str.replace(',','').astype('float')

        self._dataframe = stock_data

    
    def get_open_values(self)-> np.ndarray:
        return self._dataframe.loc[:,'Open'].values
    def get_High_values(self)-> np.ndarray:
        return self._dataframe.loc[:,'High'].values
    def get_Low_values(self)-> np.ndarray:
        return self._dataframe.loc[:,'Low'].values
    def get_close_values(self)-> np.ndarray:
        return self._dataframe.loc[:,'Close'].values

    def get_part(self, start: Union[int, str, None]=None, end: Union[int, str, None]=None) -> pd.DataFrame:
        return self._dataframe[start:end]

    def __len__(self)-> int:
        return len(self._dataframe)
    def __str__(self)-> str:
        form: str = '%Y/%m/%d'
        start_day, finish_day = self._dataframe.index[0], self._dataframe.index[-1]
        s = 'stock code:{0}  ... {1}--{2}\n'.format(self._stock_code, start_day.strftime(form), finish_day.strftime(form))
        s +=str(self._dataframe)
        return s
