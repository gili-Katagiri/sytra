# Sytra Stock Data Generating Framework
## Installation
```bash
    cd path/to/root
    git clone -b master https://github.com/gili-Katagiri/sytra
```

Install python packages by use poetry.
```bash
    cd sytra
    poetry install
```
---
## How to use
### init
At first, you have to call init process for make directories. 
```
    sytra init [--root-directory path/to/stockroot/]
```
The option `--root-directory` specify the stock data location[^1].
[^1]:path/to/stockroot/ is not sytra system root.
---

### follow
You have to prepare stock data file as 'psth/to/stockroot/prepare/*code*.csv'.
'*code*.csv' format like below.
```
"日付","始値","高値","安値","終値","出来高","前日比","貸株残高","融資残高","貸借倍率","逆日歩"
"2000/01/01","1,000.0","1,100.0","900.0","1,000.5","123,456","-10.0","100","0","0.00","-"
```
After preparing stock data, call follow process by `sytra follow`.This process make system recognize that you are monitoring *code* stock data.

---
### analyze
Then, stock.csv and analyconf.toml would be created in path/to/stockdata/ directory. 'analyconf.toml' is the setting file for data generating process. You should be customize it according to the stock data features.

When the setting is completed, create datafiles `sytra analyze -C`. 
After this commands, datafiles(daily, weekly and monthly, even pafclose) are exists in path/to/stockdata/*code*/ with branch data. 

Daily update need 'summary.csv' which created by 'sytra-auto-collection'. If prepare 'summary.csv', command `sytra analyze`.

---
