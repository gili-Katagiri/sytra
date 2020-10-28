from .msg import StemBase, PStemGenerator

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
        self._X_update(rowx)
        # dmode&self._tmode > 0: branching and set _row_initialize=True
        if dmode&self._tmode:
            self._branching(rowname)
            self._row_initialize = True

    # overload utility
    def _row_create(self, rowname, *values):
        # create rowx
        if self._row_initialize:
            self._row_initialize=False
            rowx = super()._row_create(rowname, values=values, dtype='float64')
        else:
            # get latest values and rename
            rowx = self._X_df.iloc[-1].copy().rename(rowname)
            self._X_drop()
            # High, Low are overwrited depend on values
            rowx['High'] = max(rowx['High'], values[1] )
            rowx['Low'] = min( rowx['Low'], values[2] )
            # Close is overwrite
            rowx['Close'] = values[3]
            # Volume, Compare are expressed sum of values
            rowx['Volume'] += values[4]
            rowx['Compare'] += values[5]

        return rowx



class BufStemPlanter(PStemGenerator):
    PlantStem = BufStem
    classid = 'buffer'
    depend_rootcol = ('Open', 'High', 'Low', 'Close', 'Volume', 'Compare', 'MDB', 'MSB', 'RMB', 'Backword')
