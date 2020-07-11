from lib.stocker import StockDays
from lib.stocker import StockManegerParams
from lib.stocker import StockManeger as SM
import datetime

SM.STOCK_ROOT = './tests/stocks'

day = datetime.date(2020,6,19)
days = StockDays(day)

sm = SM()
sm._smp = StockManegerParams( [], days)
sm._dump()
