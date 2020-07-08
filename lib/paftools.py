from abc import ABCMeta, abstractmethod

import matplotlib.pyplot as plt
from . import mthtools as mth
from typing import NamedTuple, Sequence, Tuple

# READONLY else if classes extended PaFAbstract.
class PaFParams(NamedTuple):
    point: int
    reverse: int
    prevalue: int = -1
    relpath: Sequence[int] = []

    def get_size(self)-> int: return len(self.relpath)
    def get_index(self)-> int: return self.get_size()-1
    def get_direction(self)-> int:
        if self.get_size()==0: return 0
        else: return mth.sign(self.relpath[-1])
    def exist(self)-> bool: 
        if self.prevalue > 0 : return True
        else: return False
    def get_abspath(self)-> Tuple[int, ...]:
        size = self.get_size()
        abspath = [0] *( size+1 )

        abspath[0] = self.prevalue
        for i in range(size):
            abspath[i+1] = abspath[i]+self.relpath[i]
        return tuple(abspath)

    def __str__(self)-> str:
        s='point={0}, reverse={1}\n'.format(self.point, self.reverse)
        if self.exist():
            s+= str( self.get_abspath() )
        else: 
            s+= 'PaF chart has been not plotted.'
        return s

class PaFAbstract(metaclass=ABCMeta):
    def __init__( self, point: int, reverse: int):
        # (0,0) is available for set_params
        if point<0 or reverse<0: 
            raise ValueError('Error: point={0} or reverse={1} is infeasible.'.format(point,reverse))
        self._params = PaFParams(point,reverse)

    def set_params(self, params: PaFParams):
        if self._params.point == 0 and self._params.reverse==0:
            self._params = params
        else: 
            raise TypeError('Error: this instance has been fixed.')

    def fixprevalue(self, value: int):
        if value < 0:
            raise ValueError('Error: prevalue would be fixed negative number.')
        elif self._params.exist():
            raise TypeError('Error: this prevalue has been fixed.')
        self._params = self._params._replace(prevalue=value)

    def get_params(self, writable=False) -> PaFParams:
        if writable: return self._params
        else:
            relpath_r = tuple( self._params.relpath )
            return self._params._replace(relpath=relpath_r)

    # read only relpath
    # cutsize is new relpath's size
    def cutting(self, cutsize: int)-> PaFParams:
        if cutsize < 0:
            raise ValueError('Error: cut size should be Natural number (include 0), but cutsize={0}.'.format(cutsize))
        size = self._params.get_size()
        if size <= cutsize:
            #print('Warning: this paf size is less than cutting size.')
            return self.get_params(writable=False)
        prevalue = self._params.get_abspath()[size-cutsize]
        relpath = tuple( self._params.relpath[size-cutsize:] )
        return self._params._replace(prevalue=prevalue, relpath=relpath)

    @abstractmethod
    def update(self, value: int): pass

    def plot_axes(self, ax: plt.axes, pltsize=30):
        params = self.cutting(pltsize)
        start = params.prevalue
        ax.scatter(0, start, color='black', marker='o')

        colors = {-1:'white', 1:'red'}
        symbols = {-1:'o', 1:'x'}
        edgecolors = {-1: 'blue', 1:'red'}

        for index, movement in enumerate(params.relpath):
            direct, count = mth.sign(movement), abs(movement)
            plot_x = [index] * count
            plot_y = [start+direct*(k+1) for k in range(count)]

            ax.scatter(plot_x, plot_y, color=colors[direct], marker=symbols[direct], edgecolor=edgecolors[direct] )
            start = plot_y[-1]

# define SIGNALS: should be included AbstractClass
SIGNAL_UNCHANGE = 0
SIGNAL_EXTENSION = 1
SIGNAL_INVERSION = 2
class PaFSimple(PaFAbstract):
    def update(self, value: int)-> Tuple[int, PaFParams]:
        if not self._params.exist():
            self.fixprevalue(value)
            return (SIGNAL_UNCHANGE, self.get_params()) 
        
        abspath = self._params.get_abspath()
        latest_value: int = abspath[-1]
        movement: int = value - latest_value
        latest_move_direction: int = self._params.get_direction()
        
        #print('abspath:{0}, latest_value: {1}, movement: {2}, latest_move_direction: {3}'.format(abspath, latest_value, movement, latest_move_direction))

        if movement == 0: pass
        elif movement*latest_move_direction > 0 :
            self._params.relpath[-1] += movement
            return (SIGNAL_EXTENSION, self.get_params())
        elif self._params.reverse <= abs(movement):
            self._params.relpath.append(movement)
            return (SIGNAL_INVERSION, self.get_params())

        return (SIGNAL_UNCHANGE, self.get_params())
