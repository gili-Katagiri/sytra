from typing import List, Tuple, Set, Union, Optional

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
    def plant_file_init(cls, msgpath, pconf): 
        # preparing datafile enable to make Stem instance
        datafiles = pconf['datafiles']
        colstr = 'Date'
        for col in cls.PlantStem.columns: colstr += (','+col)
        colstr+='\n'
        # create datafiles
        for fname in datafiles: (msgpath/fname).write_text(colstr)
        

    def __init__(self, msgpath, plantconf: dict):
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
    def stems_batch(self, rootdf: pd.DataFrame, skip: int=0):
        # get tuple or str
        desired_col = self.__class__.get_dependent(flisted=False)
        # desired_col is str: pd.Series, tuple: pd.DataFrame
        values = rootdf.loc[:, desired_col].values

        # get rownames Index of pd.Timestamp
        rownames = rootdf.index # type: pd.Index[pd.Timestamp]
        # dmode into list
        dmode_list = SytraDay.datemodes(rownames.copy().date.tolist())

        #print(rownames[-1], values[-1], dmode_list[-1])
        # batch process
        for stem in self._stemlist[skip:]:
            # protocol: columns=Stem.columns, index.name='Date'
            # how to meet the condition: use StemBase._X_df_create
            stem.batch_update(rownames, values, dmode_list)
            stem._X_save()

    # Sequential process
    def stems_update(self, rowname: pd.Timestamp, dmode: int, rowdata: pd.Series):
        # rowdata is pd.Series, why is the reason listed forthly
        # if returned str: next provide_val is not iteable!
        desired_col = self.__class__.get_dependent(flisted=True)
        # pd.Series.loc[ arg ]: available arg is list or str
        provide_val = rowdata.loc[ desired_col ]

        for stem in self._stemlist:
            # rowx: daily row data, wflag modification flag expressed as int
            stem.row_update(rowname, dmode, *provide_val)
            stem._X_save()

    # utility
    def get_planting_params(self):
        return [ stem.get_params() for stem in self._stemlist ]

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
    def _enum_branch(cls, branchconf: dict)-> list:
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
    
    def branching(self)-> list:
        # it already set, return it
        if self._branch_initialized: return self._branchlist
        
        # enumerate branches
        bglist = self.__class__._enum_branch(self._branchconf)

        # if depsolve: solve the branch dependants ??
        
        self._branch_initialized=True
        self._branchlist = bglist
        return bglist

    # check branching interface 
    # entrypoint itr process
    def check_branching(self, withbatch=True):
        # get branch list
        blist = self.branching()
        # same MSG's stems have same columns
        leader = self._stemlist[0]
        columns = leader._X_df.columns
        print('Existing columns:', columns.to_list())
        # collect the not-in columns
        for bgene in blist:
            nocols = bgene.check_columns_in(columns)
            if nocols:
                print('[Modified]: {0} is not included.'\
                        .format([bgene._col_names[i] for i in nocols]))
                if withbatch:
                    print('[Call]: Batch process for branches which is not exist.')
                    self._branch_batch(bgene, nocols)
            else: print('[Complete]:Already, Ready to Branching!')
    
    # call batch process for branches which is not exist
    def _branch_batch(self, bgene, nocols: List[int]): 
        # target: all stems
        for stem in self._stemlist:
            # create missed dataframe
            subdf = bgene.apply_batch(stem, nocols)
            # concatinate
            stem._X_df=pd.concat([stem._X_df, subdf], axis=1, join='outer')
            stem._X_save()



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
    def get_params(self): pass
    def row_update(self, rowname: pd.Timestamp, dmode: int, *rootval):
        pass
    # for loop process at low speed
    # if possible, better to override
    def batch_update(self, dates, values, dmodes: List[int]):
        for rowname, rowx, dmode in zip(dates,values,dmodes):
            self.row_update(rowname, dmode, *rowx)

    # utility
    # for sequential update
    def _row_create(self, rowname: pd.Timestamp, values=None, dtype='float64'):
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

    # interface
    def axes_plot(self, ax, pltsize=30): pass
    # utility
    def get_maindata(self, end: Optional[pd.Timestamp]=None):
        return self._X_df.loc[:end, self.__class__.main_column].to_numpy()
    def get_rownames(self):
        return self._X_df.index.values
    def _X_update(self, rowx: pd.Series): self._X_df.loc[rowx.name]=rowx
    def _X_drop(self): self._X_df.drop(index=self._X_df.index[-1], inplace=True)
    def _X_save(self):
        simX = self._X_df.copy()
        simX.index = self._X_df.index.date
        simX.index.name = 'Date'
        simX.to_csv( self._filepath, mode='w', 
                        header=True, index=True, encoding='UTF-8')

    # branching utility
    def _branching(self, rowname):
        # get branch list
        blist = self._parent_generator.branching()
        for branch in blist:
            # brrow is pd.Series
            brrow = branch.apply(self, rowname)
            idxs = brrow.index.tolist()
            # _X_df's latest row is updated, but NOT save ??
            self._X_df.loc[rowname, idxs] = brrow
