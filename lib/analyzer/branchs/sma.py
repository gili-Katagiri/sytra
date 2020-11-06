from collections import deque
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
    def apply(self, stem):
        # get desired columns values
        dcabst = self.__class__.desire_col_abstract
        if dcabst=='main':
            dcvalues = stem.get_maindata()
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


class SMAGenerator(BranchBase):
    # same branch have similar name
    colnamebase = 'SMA'
    desire_col_abstract = 'main'

    # override interface
    def _set_names(self, params):
        # params=[5,8,13,21]
        # _col_names=['SMA05', 'SMA08', 'SMA13', 'SMA21']
        base = self.__class__.colnamebase
        self._col_names = [base+str(s).zfill(2) for s in params]
    
    # override interface
    def _branch_update(self, values):
        vals = []
        for p in self._pbranch_itr:
            # calcuration values
            val = self._sma_calc(p, values)
            vals.append(val)
        rowx = super()._series_create(values=vals)
        return rowx

    # override interface
    def _branch_batch(self, rownames, values, tidxs):
        # get parameters and names of target columns
        params =  [ self._pbranch_itr[idx] for idx in tidxs ]
        columns = [ self._col_names[idx] for idx in tidxs ]
        # create columns as Series and add list
        ss = []
        for p, colname in zip( params, columns):
            # interface ???
            res = self._batch_update( p, values)
            # create Series
            s = super()._series_create(values=res, index=rownames, dtype='float64')
            # rename series to colname
            s.rename(colname, inplace=True)
            ss.append(s)
        return super()._df_create(ss)

    def _batch_update(self, length, values):
        # return values as list at the new column
        if len(values)<length: return [ None for _ in range(len(values)) ]
        result = [ None for _ in range(length) ]
        # FIFO queue
        d = deque(values[:length], maxlen=length)
        s = sum(d)
        result[-1] = s/length
        for a in values[length:]:
            # update deque
            q = d.popleft()
            d.append(a)
            # update result
            s = s-q+a
            result.append( s/length )
        return result

    def _sma_calc(self, length, values):
        if len(values) < length: return None
        else: return sum( [v for v in values[-length:]] )/length
