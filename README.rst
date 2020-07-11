====
Sytra: tools for technical analysis and machine learning for system trade.
====

this package has some useful kit for systemtrade.
stocker.py is maneger for stock data.
mthtools.py have just mathematical tools.
paftools.py is calculator for Point And Figure chart.

install
====
install ver1.0.0 by git and poetry(vdeck)
----
::
    cd /usr/local/src/
    sudo git clone -l ~/sytra -b master ./sytra
    sudo chown gilito:gilito -R sytra
    cd sytra
    sudo mkdir stocks
    sudo mkdir stocks/log stocks/holidays
    # and add YYYY.csv
    vdeck poetry install --no-dev

register ailias
    sytra: docker run --rm -it -v /usr/local/src/sytra:/root/project poetry run bin/sytra

