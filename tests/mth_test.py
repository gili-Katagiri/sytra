import pytest
from util import mthtools as mth

@pytest.fixture(scope='class')
def fixture_point():
    pa = mth.Point(2,2)
    pb = mth.Point(1,3)
    pc = mth.Point(4,5)
    nullp = mth.Point()
    origin = mth.Point(0,0)
    print('prefix Points: pa={0}, pb={1}, pc={2}, nullp={3}.'.format(pa, pb,pc,nullp))
    yield (pa, pb, pc, nullp, origin)
    print('result Points: pa={0}, pb={1}, pc={2}, nullp={3}.'.format(pa, pb,pc,nullp))

class TestPoint():
    def test_get(self, fixture_point):
        pa, pb, pc, nullp, origin = fixture_point
        assert pa.get_x()==2 and pa[1]==2
        assert pb.get_y()==3 and pb[0]==1
        assert pc.get_coordinates()==(4,5)
        with pytest.raises(ValueError): nullp.get_x()
        with pytest.raises(ValueError): nullp.get_y()
        with pytest.raises(ValueError): nullp.get_coordinates()
        
        assert str(pa)==str((2,2))
        assert str(nullp)=='(NULLPOINT)'

    def test_set(self, fixture_point):
        pa, pb, pc, nullp, origin = fixture_point
        pa.set_x(3)
        assert pa.get_x()==3 and pa[0]==3
        pb.set_y(5)
        assert pb.get_y()==5 and pb[1]==5
        pc.set_coordinates( (0,0) )
        assert pc.get_coordinates()==(0,0)
        nullp.overwrite(pa)
        assert nullp!=pa
        assert nullp.get_coordinates()==pa.get_coordinates()
        nullp.reset()
        assert nullp.exist()==0
    
@pytest.fixture(scope='class')
def fixture_line(fixture_point):
    pa,pb,pc,nullp,origin = fixture_point

    l1=mth.Line(pa,pb)
    l2=mth.Line(origin,nullp)
    print('Line test prefix:\n\tl1={0}, \n\tl2={1}'.format(l1,l2))
    yield (l1,l2,fixture_point)

class TestLine():
    def test_get(self,fixture_line):
        l1,l2,points = fixture_line
        assert l1[0] == l1.start
        assert l2[1] == l2.end
        assert l1.exist()==1 and l2.exist()==0

    def test_set(self, fixture_line):
        l1,l2,points = fixture_line
        pa,pb,pc,nullp,origin = points
        
        l3 = mth.Line()
        l3.overwrite(l2)
        assert str(l2)==str(l3)

        with pytest.raises(TypeError): l1[0] = pc
        
        l3.revolve(pa.get_coordinates())
        l3.revolve(pb.get_coordinates())
        assert str(l1)==str(l3)

        l3.reset()
        with pytest.raises(ValueError):
            l3[0].get_coordinates()

        l3[0].overwrite(origin)
        assert str(l2)==str(l3)

        assert l3.exist()==False

    def test_calc(self, fixture_line):
        l1,l2,points = fixture_line
        pa,pb,pc,nullp,origin = points

        assert l1.xlength()==-1 and l1.ylength()==1

        l2[1].overwrite(pc)
        assert l2.slope()==5/4

        assert l1.border(4)==0

        assert l1.turn_sign(pc)==-1
        assert l2.turn_sign(pb)==1
