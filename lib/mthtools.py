import sys
from typing import Optional, Tuple#, Union
from collections import namedtuple

def sign(x: int)-> int:
    return 1 if x>0 else ( 0 if x==0 else -1 )

# integer only & in FIRST quadrant
# -1 is regarded as None
class Point:
    def __init__( self, x: int = -1, y: int = -1):
        self.set_coordinates( (x,y) )

    def __str__(self)-> str:
        try:
            coord = self.get_coordinates()
        except ValueError:
            return '(NULLPOINT)'
        return str(coord)

    def __getitem__(self,key):
        if key==0 : return self.get_x()
        elif key==1: return self.get_y()
        else:
            raise IndexError(
                'Error: available key values are \'0\' or \'1\''
            )

    def get_x(self) -> int:
        if self._x == -1:
            raise ValueError('Error: x is not defined.')
        return self._x

    def get_y(self) -> int:
        if self._y == -1:
            raise ValueError('Error: y is not defined.')
        return self._y

    def get_coordinates(self)-> Tuple[int, int]:
        if self.exist() == False:
            raise ValueError('Error: point (-1,-1) is not available.')
        return ( self.get_x(), self.get_y() )

    # MUTABLE
    def set_x(self, x: int):
        self._x = x
    def set_y(self, y: int):
        self._y = y
    def set_coordinates(self, coordinates: Tuple[int,int]):
        self.set_x(coordinates[0])
        self.set_y(coordinates[1])
    
    # IMMUTABLE like
    def overwrite(self, point: "Point"):
        try:
            self.set_coordinates( point.get_coordinates() )
        except(ValueError):
            self.reset()

    def reset(self):
        self.set_coordinates( (-1,-1) )
    
    def exist(self) -> bool:
        return self._x != -1 and self._y != -1

    def slope( self, point: "Point")-> float:
        return slope( self, point)

def xlength(pa: Point, pb: Point)-> int:
    return pb.get_x() - pa.get_x()

def ylength(pa: Point, pb: Point)-> int:
    return pb.get_y() - pa.get_y()

def slope( pa: Point, pb: Point)-> float:
    return ylength(pa,pb) / xlength(pa,pb)

def signed_triangle(pa: Point, pb: Point, pc: Point)-> int:
    a: Tuple[int,int] = pa.get_coordinates()
    b: Tuple[int,int] = pb.get_coordinates()
    c: Tuple[int,int] = pc.get_coordinates()
    rs: int = a[0]*b[1] + b[0]*c[1] + c[0]*a[1]\
                -a[1]*b[0] - b[1]*c[0] -c[1]*a[0]
    return rs


# Line near by Tuple
Line_Base = namedtuple('Line_Base','start end',defaults=(Point(),Point()) )
class Line(Line_Base):
    def __str__(self)-> str:
        s = str(self[0]) + '->' + str(self[1])
        #s = str(self[0]) if self[0].exist() else 'None'
        #s+= ' -> '
        #s+= str(self[1]) if self[1].exist() else 'None'
        return s

    # IMMUTABLE
    def overwrite(self, line: 'Line'):
        for i in range(2):
            self[i].overwrite( line[i] )
    def revolve(self, point: Tuple[int,int] = (-1,-1) ):
        self.start.overwrite( self.end )
        self.end.set_coordinates( point )
    def reset(self):
        for point in self: point.reset()

    def exist(self) -> bool:
        return self.start.exist() and self.end.exist()

    def xlength(self)-> int:
        return self[1].get_x() - self[0].get_x()

    def ylength(self)-> int:
        return self[1].get_y() - self[0].get_y()

    def slope(self) -> float:
        return slope(self[0], self[1])

    def border(self, idx: int)-> float:
        slope = self.slope()
        return self[1].get_y() + slope * ( idx-self[1].get_x() )

    def turn_sign(self, expoint: Point):
        return sign( signed_triangle(self[0], self[1], expoint) )
