import numpy as np
import pandas as pd


class SMAGenerator():

    colname = 'SMA'
    @classmethod
    def _naming(cls, length_list):
        hexstr_list = [cls.colname+str(s).zfill(2) for s in length_list]
        return hexstr_list

    #udflag = 0b111
    #Branch = SimpleMovingAverage

    def __init__(self, params):
        self._pbranch = params
        self._names = self.__class__._naming(params)

    def apply(self, mainvalues):
        rowx = pd.Series(name=self.__class__.colname)
        # define row's name
        idxs = self._names
        vals = []
        for p in self._pbranch:
            # calcuration values
            val = self._sma(p, mainvalues)
            vals.append(val)
        for idx, val in zip( idxs, vals): rowx.loc[idx] = val
        return rowx
            

    def _sma(self, length, values):
        if len(values) < length: return np.nan
        else: return sum( [v for v in values[-length:]] )/length
