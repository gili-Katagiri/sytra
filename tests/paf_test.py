import pytest
from tools import paftools as paf

EXEC_BY_TMUX = True

@pytest.fixture(scope='class')
def fixture_params():
    prefixp = paf.PaFParams(5,3)
    params = paf.PaFParams(5,3,10,[3,-4,7])
    print('prefixp: {0}\n params: {1}'.format(prefixp,params))
    yield prefixp,params

class TestParams():
    def test_get(self,fixture_params):
        prefixp, params = fixture_params
        assert params.point == 5 and params.reverse==3
        assert prefixp.exist()==False and params.exist()
        assert prefixp.get_direction() == 0 and \
                prefixp.get_size() == 0 and \
                prefixp.get_index() == -1
        assert params.get_direction() == 1 and \
                params.get_size()==3 and \
                params.get_index() == 2
        assert prefixp.get_abspath() == (-1,)
        assert params.get_abspath() == (10,13,9,16)
        

@pytest.fixture(scope='class')
def fixture_chart():
    nullchart = paf.PaFSimple(0,0)
    chart = paf.PaFSimple(5,3)
    closes = [10,7,8,7,6,9,8,10,12,15,14,15,6,10]
    yield nullchart, chart, closes

    if EXEC_BY_TMUX == False:
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)

        nullchart.plot_axes(ax)
        plt.show()

class TestPaFSimple():
    def test_set(self, fixture_params, fixture_chart):

        with pytest.raises(ValueError): chart = paf.PaFSimple(-1,4)

        prefixp, params = fixture_params
        null,chart,closes = fixture_chart

        with pytest.raises(TypeError): chart.set_params(params)

        with pytest.raises(ValueError): chart.cutting(-10)
        assert chart.cutting(100).get_abspath() == (-1,)
    
        null.set_params(params)
        assert null.get_params().relpath.__class__.__name__ == 'tuple'
        assert null.get_params(writable=True) == params

        chart = null.cutting(1)
        assert chart.prevalue == 9
        assert tuple( chart.relpath ) == (7,)

        with pytest.raises(ValueError): null.fixprevalue(-3)
        with pytest.raises(TypeError): null.fixprevalue(4)

    def test_update(self, fixture_chart):
        # nullchart was modified by test_set, chart2 was not.
        chart1, chart2, closes = fixture_chart
        for close in closes: chart2.update(close)
        print(chart2.get_params())
        params = chart2.get_params()
        assert params.prevalue == 10
        assert params.relpath == (-4,9,-9,4)
