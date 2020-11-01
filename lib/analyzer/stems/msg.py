from typing import Tuple, Set, Union

import pandas as pd


from analyzer.branchs.sma import SMAGenerator
from util.sytraday import SytraDay


# Planter
class MultiStemGenerator():

    # class for planting: Multi-Stem ex) BufStem, PaF_close
    PlantStem: type
    # identification: this may config file name
    classid: str
    # tuple: dependent root parameters
    depend_rootcol: Union[ str, Tuple[str, ...] ]
    # provide depend_rootcol if tuple: to_list, str: as it
    @classmethod
    def get_dependent(cls, flisted=True): 
        cols = cls.depend_rootcol 
        if type(cols) is tuple: return list(cols)
        elif flisted: return [cols] # listed str
        else: return cols # flisted False: return str
    
    @classmethod
    def _plant_file_init(cls, msgpath, pconf, stockdata): 
        # preparing datafile enable to make Stem instance
        datafiles = pconf['datafiles']
        colstr = 'Date'
        for col in cls.PlantStem.columns: colstr += (','+col)
        colstr+='\n'
        for fname in datafiles: (msgpath/fname).write_text(colstr)
        
        # create class instance
        # call this function from Analyzer: MSG._plant_file_init, MSG=~Planter
        # not in Capsule??
        msg = cls( msgpath, pconf, dict())
        # stockdata from stock.csv, Index parsed to pd.TimeStamp
        msg.stems_batch(stockdata)


    def __init__(self, msgpath, plantconf):
        # create 
        self._stemlist = []
        Stem = self.__class__.PlantStem
        # sep
        datafiles = plantconf['datafiles']
        params = plantconf['p-planting']
        # make stems
        for fname, param in zip(datafiles, params):
            stem = Stem(self, msgpath/fname, param)
            self._stemlist.append(stem)

    # Batch process
    def stems_batch(self, rootdf):
        # get tuple or str
        desired_col = self.__class__.get_dependent(flisted=False)
        # desired_col is str: pd.Series, tuple: pd.DataFrame
        values = rootdf.loc[:, desired_col].values

        # get rownames as list (or to_numpy(): as array)
        rownames = rootdf.index
        # dmode into list
        dmode_list = SytraDay.datemodes(rownames.copy().to_list())

        #print(rownames[-1], values[-1], dmode_list[-1])
        # batch process
        for stem in self._stemlist:
            # protocol: columns=Stem.columns, index.name='Date'
            # how to meet the condition: use StemBase._X_df_create
            stem._batch_update(rownames.to_list(), values, dmode_list)
            stem._X_save()
    # Sequential process
    def stems_update(self, rowname, dmode, rowdata):
        # rowdata is pd.Series, why is the reason listed forthly
        # if returned str: next provide_val is not iteable!
        desired_col = self.__class__.get_dependent(flisted=True)
        # pd.Series.loc[ arg ]: available arg is list or str
        provide_val = rowdata.loc[ desired_col ]

        for stem in self._stemlist:
            # rowx: daily row data, wflag modification flag expressed as int
            stem._row_update(rowname, dmode, *provide_val)
            stem._X_save()

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

class StemBranchGenerator(MultiStemGenerator): 

    # callable Branch dictionary
    Branch_dict = {
        'SMA': SMAGenerator
    }

    # return listed BranchGenerator which is constracted by branch config
    @classmethod
    def _enum_branch(cls, branchconf: dict):
        # use List to express tree
        bglist = []
        for bid, bconf in branchconf.items():
            # get BranchGenerator CLASS
            BG = cls.Branch_dict[bid]
            # make BranchTree instance
            # arg: Stem.Branching.bid.branching
            bgins = BG(bconf['branch'])
            bglist.append(bgins)
        return  bglist
    
    # overload super().__init__
    def __init__(self, msgpath, plantconf, branchconf):
        super().__init__(msgpath, plantconf)
        # call Branching on time
        self._branch_initialized = False
        self._branchconf = branchconf
    
    def branching(self):
        # it already set, return it
        if self._branch_initialized: return self._branchlist
        
        # enumerate branches
        bglist = self.__class__._enum_branch(self._branchconf)

        # if depsolve: solve the branch dependants ??
        
        self._branch_initialized=True
        self._branchlist = bglist
        return bglist


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

    # for loop process at low speed
    # if possible, better to override
    def _batch_update(self, dates, values, dmodes):
        for rowname, rowx, dmode in zip(dates,values,dmodes):
            self._row_update(rowname, dmode, *rowx)

    # utility
    # for sequential update
    def _row_create(self, rowname, values=None, dtype='float64'):
        # prepare Series
        rowx = pd.Series(data=values, index=self.__class__.columns,
                name=rowname, dtype=dtype)
        return rowx

    # for batch update
    def _X_df_create(self, index, values, dtype='float64'):
        cols = self.__class__.columns
        xdf = pd.DataFrame(data=values, index=index, columns=cols, dtype=dtype)
        xdf.index.name = 'Date'
        return xdf

    def axes_plot(self, ax, pltsize=30): pass

    # utility
    def get_main_data(self):
        return self._X_df.loc[:, self.__class__.main_column].to_numpy()
    def _X_update(self, rowx): self._X_df.loc[rowx.name]=rowx
    def _X_drop(self): self._X_df.drop(self._X_df.index[-1], inplace=True)
    def _X_save(self):
        self._X_df.to_csv( self._filepath, mode='w', 
            header=True, index=True, encoding='UTF-8')
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

