from util import mthtools as mth
from .msg import PStemBase, PStemGenerator

class PaFAbstract(PStemBase):
    
    columns = ( 'pafabs', )
    main_column = 'pafabs'

    # interface
    def _params_init(self, params):
        self._point, self._reverse = params
        self._abspath = self.get_main_data().tolist()

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

    # interface
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

    def _row_update(self, rowx, close):
        idx = self.__class__.columns
        val, wflag = self.update(close)
        # add index and value
        for i, v in zip(idx, val): rowx[i]=v
        return wflag


    def update(self, close):

        # current point 
        val = int(close) // self._point

        # initial
        if len(self._abspath)<1:
            self._abspath.append(val)
            return (val,), 1
        # last point and direction
        last = self._abspath[-1]
        dsign = self.get_direction()
        
        # movement
        mov = val - last
        # update flagments
        wflag = 0

        # continue growth
        if mov*dsign > 0:
            self._abspath[-1] = val
            wflag = 2 #override
        # resistance and exceed
        elif abs(mov) >= self._reverse:
            self._abspath.append(val)
            wflag = 1 # add
        # no change
        else: wflag = 0
        
        # update elements
        return (val,), wflag


class PaFClosePlanter(PStemGenerator):
    PlantStem = PaFClose
    classid = 'pafclose'
    udflag = 0b100
    depend_rootcol = ('Close', )
    

