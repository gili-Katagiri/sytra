from util import mthtools as mth
from .msg import StemBase, StemBranchGenerator

class PaFAbstract(StemBase):
    
    columns = ( 'pafabs', )
    main_column = 'pafabs'

    # override interface
    def _params_init(self, params):
        # params = [ point, reverse ]
        self._point, self._reverse = params
        self._abspath = self.get_maindata().tolist()
    def get_params(self):
        return [self._point, self._reverse]
    # override interface
    def row_update(self, rowname, dmode, *rootval):
        # start base branching
        rowx, spflag = self._row_create(rowname, *rootval)
        # spflag is True: branching without rowx
        if spflag: super()._branching(self._X_df.index[-1])
        # spflag is False: rowx overwrite latest update
        else: self._X_drop()
        self._X_update(rowx)

    # overload utilty
    def _row_create(self, rowname, *rootval):
        values, spflag = self._update_(*rootval)
        # values: tuple -> pd.Series (index=__class__.columns)
        rowx = super()._row_create(rowname, values=values, dtype='int64')
        # rowx and specific flag
        return rowx, spflag

    # interface
    def _update_(self, *rootval): pass

    # utility
    def get_direction(self):
        if len(self._abspath) < 2: return 0
        else: return mth.sign(self._abspath[-1] - self._abspath[-2])
    # abspath to relpath
    def get_relpath(self, maxsize=30):

        # get span
        availsize = len(self._abspath)
        abspath = self._abspath[max(-availsize, -maxsize-1):]

        # start point
        intercept = abspath[0]

        preh = intercept
        relpath = []
        # get differences
        for height in abspath[1:]:
            relpath.append( height - preh )
            preh = height
        
        return intercept, relpath

    # override interface
    def axes_plot(self, ax, maxsize=30):
        inter, relpath = self.get_relpath(maxsize=maxsize)
        ax.scatter(0, inter, color='black', marker='o')

        #colors = {-1:'white', 1:'red'}
        #symbols = {-1:'o', 1:'x'}
        #edgecolors = {-1: 'blue', 1:'red'}

        dotdesign = { -1:{ 'color': 'white', 'marker': 'o', 'edgecolor': 'blue'},
                       1:{ 'color':   'red', 'marker': 'x', 'edgecolor':  'red'}  }

        for idx, dots in enumerate(relpath):
            direct, quant = mth.sign(dots), abs(dots)
            plot_x = [idx]*quant
            plot_y = [inter+direct*(k+1) for k in range(quant)]

            ax.scatter( plot_x, plot_y, **(dotdesign[direct]) )
            inter = plot_y[-1]

    def __str__(self):
        s ='point: %d, reverse: %d\n' % (self._point, self._reverse)
        s+='main data:\n'
        s+=str(self._abspath)
        return s


class PaFClose(PaFAbstract):
    columns = ( 'pafc', )
    main_column = 'pafc'

    # interface
    def batch_update(self, dates, cvalues, *nouse):
        # dmode_list used in T-Planting Stem, no use at this class
        # create abspath with pre-REVERSAL DAY's list
        # cvalues: 1D numpy.array
        rd_list = []
        for date, close in zip(dates, cvalues):
            val, reflag = self._update_(close)
            # if reverse: append else overwrite
            if reflag: rd_list.append(date)
            else: rd_list[-1]=date
        # create _X_df by _X_df_create, that meet some conditions
        pafcdf = super()._X_df_create(rd_list, self._abspath, dtype='int64')
        self._X_df = pafcdf
        return pafcdf

    def _update_(self, close):

        # current point 
        val = int(close) // self._point

        # initial
        if len(self._abspath)<1:
            self._abspath.append(val)
            return (val,), True
        # last point and direction
        last = self._abspath[-1]
        dsign = self.get_direction()
        
        # movement
        mov = val - last
        # update flagments
        reflag = False

        # continue growth
        if mov*dsign > 0:
            self._abspath[-1] = val
            reflag = False #override
        # resistance and exceed
        elif abs(mov) >= self._reverse:
            self._abspath.append(val)
            reflag = True # add
        # no change
        else: reflag = False #pass
        
        # update elements
        return (self._abspath[-1],), reflag


class PaFClosePlanter(StemBranchGenerator):
    PlantStem = PaFClose
    classid = 'pafclose'
    depend_rootcol = 'Close'
    

