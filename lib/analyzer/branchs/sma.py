from .brbase import BranchBase
from collections import deque

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
            val = self._sma_fit(p, values)
            vals.append(val)
        rowx = super()._series_create(values=vals)
        return rowx

    # override interface
    def _branch_batch(self, rownames, values, tidxs):
        # get parameters and names of target columns
        params =  [ self._pbranch_itr[idx] for idx in tidxs ]
        columns = [ self._col_names[idx] for idx in tidxs ]
        # create columns as Series and add list
        slist = []
        for p, colname in zip( params, columns):
            # interface ???
            res = self._batch_update( p, values)
            # create Series
            s = super()._series_create(values=res, index=rownames, dtype='float64')
            # rename series to colname
            s.rename(colname, inplace=True)
            slist.append(s)
        return super()._df_create(slist)

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

    def _sma_fit(self, length, values):
        if len(values) < length: return None
        else: return sum( [v for v in values[-length:]] )/length
