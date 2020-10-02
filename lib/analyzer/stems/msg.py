from typing import Tuple

import pandas as pd

# Planter
class MultiStemGenerator():

    # class for planting: Multi-Stem ex) Buffer, PaF_close
    PlantStem: type
    # identification: this may config file name
    classid: str
    # t-planting byte string and branching flag
    udflag: int
    # tuple: dependent root parameters
    depend_rootcol: Tuple[str]
    @classmethod
    def get_dependent(cls): return cls.depend_rootcol

    # args example PaF: ( (p1, r1), (p2, r2), ... )
    def __init__(self, msgpath, datafiles, *args):
        
        # create T-planting
        self._stemlist = []
        Stem = self.__class__.PlantStem

        # get directory
        for i in range(len(datafiles)):
            stem = Stem( msgpath/datafiles[i], *(args[i]) )
            self._stemlist.append(stem)

    def stems_update(self, rowname, rowdata):
        # get list
        desired_lst = list(self.__class__.get_dependent())
        # pd.Series.loc[ arg ]: available arg is list or str
        # str-> numpy.'~', list-> pd.Series
        provide_val = rowdata.loc[ desired_lst ]

        for stem in self._stemlist:
            stem.update(rowname, *provide_val)


'''

class TGenerator(MultiStemGenerator): 
    def __init__(self, stockpath, csvfiles):
        super().__init__(stockpath, csvfiles)

class PGenerator(MultiStemGenerator): 
    def __init__(self, stockpath, csvfiles, planting_args):
        super().__init__(stockpath, csvfiles, *planting_args)

'''


class StemBase():

    # generating columns
    columns: Tuple[str]
    main_column: str

    # read data
    def __init__(self, filepath):
        self._filepath = filepath
        # read datafile, dtype?
        self._X_df = pd.read_csv(
            filepath, header=0, index_col='Date', parse_dates=True
        )

    # interface
    def update(self, rowname, *rowx, write=True, drop=False):
        # make pd.Series follow Class variance 'columns' and argument 'rowx'
        rowseries = pd.Series(rowx, index=self.__class__.columns)
        if not write: return rowseries
        if drop:
            self._X_df.drop(index=self._X_df.index[-1], inplace=True)
        
        self._X_df.loc[rowname] = rowseries
        return rowseries

    def axes_plot(self, ax, pltsize=30): pass

    def get_main_data(self):
        return self._X_df.loc[:, self.__class__.main_column].values


