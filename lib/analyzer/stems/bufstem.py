from .msg import StemBase, StemBranchGenerator

class BufStem(StemBase):
    columns = ('Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
    main_column = 'Close'
    
    # override interface
    def _params_init(self, params):
        # params = [ tmode, intflag ]
        self._tmode = params[0]
        self._row_initialize = bool(params[1])

    #override interface
    def _row_update(self, rowname, dmode, *rootval): 
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
    def _batch_update(self, dates, values, dmodes):
        # dates:  ['2020-01-04', '2020-01-05', ... ]
        # values: [ [open, high,...], [open, high,...], ... ]
        rowold = None
        # ignore last index
        for idx in range( len(dates)-1 ):
            date, rowvalues, dmode = dates[idx], values[idx], dmodes[idx]
            # create values row
            rowx = self._row_create(date, *rowvalues)
            # correspond to _row_initialize=False
            if rowold is not None: rowx = self._update_(rowx, rowold)
            rowold = rowx
            # specific day
            if dmode&self._tmode:
                self._X_update(rowx)
                rowold = None  # restart
        if rowold is None: # updated just before break loop
            self._row_initialize = True
        else:
            self._X_update(rowold)  # add tail _X_df
            self._row_initialize=False
        # last index
        self._row_update(dates[-1], dmodes[-1], *values[-1])

    # overload utility
    def _row_create(self, rowname, *values):
        # create rowx
        rowx = super()._row_create(rowname, values=values, dtype='float64')
        if not self._row_initialize:
            # get latest values and rename
            rowold = self._X_df.iloc[-1].copy().rename(rowname)
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
        
class BufStemPlanter(StemBranchGenerator):
    PlantStem = BufStem
    classid = 'buffer'
    depend_rootcol = ('Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')

    @classmethod
    def _plant_file_init(cls, rootpath, pconf, stockdata):
        # datafiles name can not be changed 
        (rootpath/'daily.csv').symlink_to('../stock.csv')

        # delete daily config
        del pconf['datafiles'][0]
        del pconf['p-planting'][0]
        super()._plant_file_init(rootpath, pconf, stockdata)
