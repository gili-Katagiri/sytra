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

    def __init__(self, msgpath, datafiles, tpargs, branchconf):
        # create 
        self._stemlist = []
        Stem = self.__class__.PlantStem
        # call Branching on time
        self._branch_initialized = False
        self._branchconf = branchconf
        # make stems
        for fname, param in zip(datafiles, tpargs):
            stem = Stem(self, msgpath/fname, param)
            self._stemlist.append(stem)

    # make branch tree
    def _enum_branch(self):
        # use List to express tree
        bglist = []
        for bid, bconf in self._branchconf.items():
            # get BranchGenerator CLASS
            BG = self.__class__.Branch_dict[bid]
            # make BranchTree instance
            # arg: Stem.Branching.bid.branching
            bgins = BG(bconf['branch'])
            bglist.append(bgins)
        return  bglist

    def branching(self):
        # it already set, return it
        if self._branch_initialized: return self._branchlist
        
        # enumerate branches
        bglist = self._enum_branch()
        # if depsolve: solve the branch dependants ??
        
        self._branch_initialized=True
        self._branchlist = bglist
        return bglist


    def stems_update(self, rowname, dmode, rowdata):
        # get list
        desired_lst = list(self.__class__.get_dependent())
        # pd.Series.loc[ arg ]: available arg is list or str
        # str-> numpy.'~', list-> pd.Series
        provide_val = rowdata.loc[ desired_lst ]

        for stem in self._stemlist:
            # rowx: daily row data, wflag modification flag expressed as int
            stem._row_update(rowname, dmode, *provide_val)
            #stem.apply(rowname, bglist)

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


class PStemGenerator(MultiStemGenerator): 
    # args example PaF: ( (p1, r1), (p2, r2), ... )
    def __init__(self, msgpath, plantconf, branchconf):
        datafiles = plantconf['datafiles']
        p_planting = plantconf['p-planting']
        super().__init__(msgpath, datafiles, p_planting, branchconf)


'''
class TStemGenerator(MultiStemGenerator): 
    # T-Branching desire stems have timeid: ( t1, t2, ...)
    def __init__(self, msgpath, plantconf, branchconf):
        # make Stems and append
        datafiles = platnconf['datafiles']
        t_planting = plantconf['t-planting']
        super().__init__(msgpath, datafiles, t_planting, branchconf)
'''

class StemBase():

    # generating columns
    columns: Tuple[str]
    main_column: str

    # read data
    def __init__(self, parent, filepath, params):
        self._parent_generator = parent
        self._filepath = filepath
        # read datafile, dtype?
        self._X_df = pd.read_csv(
            filepath, header=0, index_col='Date', parse_dates=True
        )
        self._params_init(params)

    # interface
    def _params_init(self, params): pass
    def _row_update(self, rowname, dmode, *rootval): pass

    # utility
    def _row_create(self, rowname, values=None, dtype='float64'):
        # prepare Series
        rowx = pd.Series(data=values, index=self.__class__.columns,
                name=rowname, dtype=dtype)
        return rowx


    def axes_plot(self, ax, pltsize=30): pass

    # utility
    def get_main_data(self):
        return self._X_df.loc[:, self.__class__.main_column].values
    def _X_update(self, rowx): self._X_df.loc[rowx.name]=rowx
    def _X_drop(self): self._X_df.drop(self._X_df.index[-1], inplace=True)
    def _branching(self, rowname):
        # get branch list
        blist = self._parent_generator.branching()
        # get main values for update branch
        mainvalues = self.get_main_data()
        for branch in blist:
            # brrow is pd.Series
            brrow = branch.apply(mainvalues)
            idxs = brrow.index.tolist()
            # _X_df's latest row is updated, but NOT save ??
            self._X_df.loc[rowname, idxs] = brrow

