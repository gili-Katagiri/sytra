import pandas as pd

class BranchBase():
    # name base str
    colnamebase: str
    # need values Abstract from _X_df
    desire_col_abstract: str
    
    def __init__(self, params):
        # [ [br0, anch0, ...], [br1, anch1, ... ], ... ]
        self._pbranch_itr = params
        self._set_names(params)

    # utility but if possible, better to overload
    # decide branching names as list
    def _set_names(self, params): 
        base = self.__class__.colnamebase
        # set [ 'base0', 'base1', ... ]
        self._col_names = [ base+str(i) for i in range( len(params) ) ]

    # branching entrypoint
    def apply(self, stem, rowname: pd.Timestamp):
        # get desired columns values
        dcabst = self.__class__.desire_col_abstract
        if dcabst=='main':
            dcvalues = stem.get_maindata(end=rowname)
        else: dcvalues=[]
        return self._branch_update(dcvalues)
    # batch process entrypoint
    def apply_batch(self, stem, tidxs):
        dcabst = self.__class__.desire_col_abstract
        if dcabst=='main': 
            dcvalues = stem.get_maindata()
        else: dcvalues=[]
        rownames = stem.get_rownames()
        return self._branch_batch(rownames, dcvalues, tidxs)

    # interface branching
    def _branch_update(self, values): pass
    # interface batch process
    def _branch_batch(self, rownames, values, tidxs): pass
        
    # utility
    def _series_create(self, values=None, index=None, dtype='float64'):
        # given None index: set column names
        idxs = self._col_names if index is None else index
        rowx = pd.Series(data=values, index=idxs, dtype=dtype)
        return rowx
    def _df_create(self, serieslist):
        dfx = pd.concat( serieslist, axis=1, join='inner')
        dfx.index.name = 'Date'
        return dfx
    def check_columns_in(self, columns):
        # columns: pd.Index
        nocols = []  # not in column index list
        for idx, name in enumerate(self._col_names):
            if not ( name in columns ): nocols.append(idx)
        return nocols


