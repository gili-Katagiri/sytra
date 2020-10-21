from typing import Tuple, Set

import pandas as pd


from analyzer.branchs.sma import SMAGenerator


# Planter
class MultiStemGenerator():

    # class for planting: Multi-Stem ex) Buffer, PaF_close
    PlantStem: type
    # identification: this may config file name
    classid: str
    # timely flag
    udflag: int
    # tuple: dependent root parameters
    depend_rootcol: Tuple[str]
    @classmethod
    def get_dependent(cls): return cls.depend_rootcol
    # callable Branch dictionary
    Branch_dict = {
        'SMA': SMAGenerator
    }

    def __init__(self, msgpath, datafiles, tpargs):
        # create 
        self._stemlist = []
        Stem = self.__class__.PlantStem
        # make stems
        for fname, param in zip(datafiles, tpargs):
            stem = Stem( msgpath/fname, param)
            self._stemlist.append(stem)

    # make branch tree
    def _enum_branch(self, dmode, branchconf):
        # use List to express tree
        bglist = []
        for bid, bconf in branchconf.items():
            # get BranchGenerator CLASS
            BG = self.__class__.Branch_dict[bid]
            # make BranchTree instance
            # arg: Stem.Branching.bid.branching
            bgins = BG(bconf['branch'])
            bglist.append(bgins)
        return  bglist

    def branching(self, dmode, branchconf):
        if self.__class__.udflag&dmode==0 : return []
        # enumerate branches
        bglist = self._enum_branch(dmode, branchconf)
        # if depsolve: solve the branch dependants ??
        
        return bglist


    def stems_update(self, rowname, rowdata, bglist):
        # get list
        desired_lst = list(self.__class__.get_dependent())
        # pd.Series.loc[ arg ]: available arg is list or str
        # str-> numpy.'~', list-> pd.Series
        provide_val = rowdata.loc[ desired_lst ]

        for stem in self._stemlist:
            # rowx: daily row data, wflag modification flag expressed as int
            rowx, wflag = stem.update_maindata(rowname, *provide_val)
            if wflag==0: return
            stem.apply(bglist, rowx)
            stem.update_X(rowx, wflag)


    """
    def depend_solve(self, branchenume, bfilter):
        udflag = self.__class__.udflag
        
        # solved branch list
        solved = []
        while branchenume:
            Branch = branchenume.pop(0) # should be dequeue
            if not udflag & Branch.udflag & bfilter: continue
            dependant = Branch.depends # type: Set
            if dependant <= set(solved): solved.append(Branch)
            else: branchenume.append(Branch)

        return solved
    """

'''
    TBranchingGenerator and PBranchingGenerator have function __init__,
    those are the SAME function which defined in MultiStemGenerator
    except for the argment names.
    
    These classes should be distinguished as different branching system.
    P-Branching process completed without considering which process should be done,
    but T-Branching process need to switch according to variable 'dmode'.
'''

class TStemGenerator(MultiStemGenerator): 
    # T-Branching desire stems have timeid: ( t1, t2, ...)
    def __init__(self, msgpath, plantconf):
        # make Stems and append
        datafiles = platnconf['datafiles']
        t_planting = plantconf['t-planting']
        super().__init__(msgpath, datafiles, t_planting)
    '''
    def branching(self, dmode, branchconf):
        # get BranchGeneratorTree as List
        bglist = super().branching(dmode, branchconf)
        for stem in self._stemlist:
            # T-Stem's udflags may be different every instance
            if stem._tmode & dmode:
                for bg in bglist: stem.apply(bg)
    '''

class PStemGenerator(MultiStemGenerator): 
    # args example PaF: ( (p1, r1), (p2, r2), ... )
    def __init__(self, msgpath, plantconf):
        datafiles = plantconf['datafiles']
        p_planting = plantconf['p-planting']
        super().__init__(msgpath, datafiles, p_planting)
    '''
    def branching(self, dmode, branchconf):
        # get BranchGeneratorTree as List
        bglist = super().branching(dmode, branchconf)
        # all of P-Stem's udflags is the same value
        if self.__class__.udflag&dmode==0: return
        for stem in self._stemlist:
            for bg in bglist: stem.apply(bg)
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

    def update_maindata(self, rowname, *desirevalues):
        rowx = pd.Series(name=rowname)
        wflag = self._row_update(rowx, *desirevalues)
        return rowx, wflag
    
    def update_X(self, rowx, writeflag):
        # writeflag--- 0: Nochange, 1: Add, 2: Overwrite
        if writeflag < 1: return
        elif writeflag > 1:
            self._X_df.drop(index=self._X_df.index[-1], inplace=True)
        self._X_df.loc[rowx.name] = rowx


    def apply(self, bglist, rowx):
        # prepare desired data 
        mvalues = self.get_main_data()
        for bg in bglist:
            bg.apply(mvalues, rowx)
            

    def axes_plot(self, ax, pltsize=30): pass

    def get_main_data(self):
        return self._X_df.loc[:, self.__class__.main_column].values
    def get_dataframe(self, colname):
        return self._X_df.loc[:, self._X_df.columns.str.startswith('SMA')]

class TStemBase(StemBase):
    def __init__(self, filepath, tmode):
        super().__init__(filepath)
        self._tmode = tmode


class PStemBase(StemBase):
    
    def __init__(self, filepath, params):
        super().__init__(filepath)
        self._params_init(params)
    #interface
    def _params_init(self, params): pass

