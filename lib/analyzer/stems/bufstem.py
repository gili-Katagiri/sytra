import math
from .msg import StemBase, StemBranchGenerator

from exceptions import StemError

class BufStem(StemBase):
    columns = ('Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    main_column = 'Close'
    
    # override interface
    def _params_init(self, params):
        # params = [ tmode, intflag ]
        self._tmode = params[0]
        self._row_initialize = bool(params[1])
    def get_params(self):
        return [self._tmode, int(self._row_initialize)]

    #override interface
    def row_update(self, rowname, dmode: int, *rootval): 
        # end base branching
        rowx = self._row_create(rowname, *rootval)
        if not self._row_initialize: self._X_drop()
        self._X_update(rowx)
        # already intialized 
        self._row_initialize = False
        # dmode&self._tmode > 0: branching and set _row_initialize=True
        if dmode&self._tmode:
            self._branching(rowname)
            self._row_initialize = True

    #override interface
    def batch_update(self, dates, values, dmodes):
        # dates:  pd.Index[ pd.Timestamp, ... ]
        # values: [ [open, high,...], [open, high,...], ... ]
        rowold = None
        # ignore last index
        for idx in range( len(dates) ):
            date, rowvalues, dmode = dates[idx], values[idx], dmodes[idx]
            # create values row
            rowx = self._row_create(date, *rowvalues)
            # correspond to _row_initialize=False
            if rowold is not None: rowx = self._update_(rowx, rowold)
            rowold = rowx
            # specific day
            if dmode&self._tmode:
                # no check update
                super()._X_update(rowx)
                rowold = None  # restart
        # rowold is None: latest rowx is already exists-> not call _X_update
        # else: not exist latest rowx
        if rowold is not None: self._X_update(rowold)
        self._row_initialize=bool(dmodes[-1]&self._tmode)

    # overload utility
    def _row_create(self, rowname, *values):
        # create rowx
        rowx = super()._row_create(rowname, values=values, dtype='float64')
        if not self._row_initialize:
            # get latest values and rename
            rowold = self._X_df.iloc[-1, 0:10].copy().rename(rowname)
            rowx = self._update_(rowx, rowold)
        return rowx

    def _update_(self, rownew, rowold):
        # new instance
        rowx = rowold.copy()
        rowx.rename(rownew.name, inplace=True)
        # High, Low are overwrited depend on values
        rowx['High'] = max(rownew['High'], rowold['High'] )
        rowx['Low'] = min( rownew['Low'], rowold['Low'] )
        # Close is overwrite
        rowx['Close'] = rownew['Close']
        # Volume, Compare are expressed sum of values
        rowx['Volume'] += rownew['Volume']
        rowx['Compare'] += rownew['Compare']
        return rowx

    def _X_update(self, rowx):
        # close value immediately before
        rowoldclose = self._X_df.iat[-1, 3]
        # inference value from latest Close and Compare
        infer = rowx.at['Close'] - rowx.at['Compare']
        if not math.isclose( infer, rowoldclose ):
            raise StemError('pre-close(%.1f) is separated from inference(%.1f)' \
                                % (rowoldclose, infer) )
        super()._X_update(rowx)
        
class BufStemPlanter(StemBranchGenerator):
    PlantStem = BufStem
    classid = 'buffer'
    depend_rootcol = ('Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')

    @classmethod
    def _plant_file_init(cls, msgpath, pconf):
        super()._plant_file_init(msgpath, pconf)
        (msgpath/'daily.csv').unlink()
        (msgpath/'daily.csv').symlink_to('../stock.csv')

    @classmethod
    def _plant_init(cls, rootpath, pconf, bconf, stockdata):
        super()._plant_init(rootpath, pconf, bconf, stockdata, exclude=1)
