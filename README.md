## Sytra Stock Data Generating Framework

## Abstract
Sytra is stock price analysis tool under development.
Currently available processes are stock price conversion 
into some useful *technical* data, and further data generation.

## Installation

---
[install-docker]: https://github.com/gili-Katagiri/sytra-docker
***Note:** We recommend using Docker for installation. 
If follow, refer to [sytra-docker][install-docker] 
and skip this installation paragraph.*

---

Required [poetry](https://python-poetry.org/docs/#installation) 
to install Sytra.
Check if `poetry` is available using the following command.
```bash
    poetry --version
```
Please install `poetry` if you have not yet.

Next, clone repository into your local directory(meta:`path/to/sytra`).
Install python packages by use poetry.
```bash
    git clone https://github.com/gili-Katagiri/sytra path/to/sytra
    cd path/to/sytra
    poetry install
```
`poetry` creates virtual python environment.
Therefore, in order to use sytra, 
you must be in the `path/to/sytra` where `.venv` exists.  

After installing the dependent packages,
not required but recommended to do the following
for convenience of explain (or improvement of convenience).
1. set system environment variable as path to store the generated data.
1. create an alias sytra='poetry run sytra/bin/sytra'

It is better to add these to the "rc-file" of your default shell 
(but you have to be careful, '2' depends on the current directory).
```bash
    export STOCKROOT='path/to/data'
    alias sytra='poetry run sytra/bin/sytra'
```
At the end of setup, call `sytra init` with `$STOCKROOT`.
```bash
    sytra init --root-directory $STOCKROOT
```

## Usage
### follow
You have to prepare stock data file as `$STOCKROOT/prepare/9999.csv`.
'9999' represents the id, which depends on the stock.
`9999.csv` is a CSV file with the following format.
```
"日付","始値","高値","安値","終値","出来高","前日比","貸株残高","融資残高","貸借倍率","逆日歩"
"2000/01/01","1,000.0","1,100.0","900.0","1,000.5","123,456","-10.0","100","0","0.00","-"
...
```
After preparing file like this, call process `sytra follow`.
This process make system recognize 
that you are monitoring stock data corresponding to '9999'.

### analyze
##### Prepare and Consistency
`follow` processed without issue,
directory including `stock.csv` and `analyconf.toml`
would be created as `$STOCKROOT/9999/`. 
Sytra read `analyconf.toml` to generate data for analysis.
You should be customize it with your editor 
according to the stock data features.

When the setting is completed, exec `sytra analyze -C`. 
This command creates datafiles 
obtained combining 'Stem-data' 
(`buffer/{daily.csv, weekly.csv monthly.csv}` even `pafclose/`) 
with 'Branch-data' (including SMA) at `$STOCKROOT/9999/`. 
Every time after editing the `analyconf.toml`, 
you need to call this process from now on.
This keeps the generated data and the `analyconf.toml` consistent.

##### Daily update
Daily update need `summary.csv` with the following format.
```
2000-01-02
Code,Open,High,Low,Close,Volume,Compare,MDB,MSB,RMB,Backword
9999,1111.1,1234.5,1000.0,1100.5,9870000,65,0,25100,0,0
...
```
Summary is to be desired
1. including all the 'following' stock data,
1. enter the update date on the first line, 
and this matches the scheduled one.

Both of these are listed in the `$STOCKROOT/sytraconf.toml`.

---
***Info:***
*You can use 
[sytra-auto-collector](https://github.com/gili-Katagiri/sytra-auto-collector),* 
***but this is deprecated.***
*In the present circumstances, it is not yet stable release 
and dependent environment, tools and settings are too complex to use.*

---
If you have prepared `STOCKROOT/summary.csv`, exec `sytra analyze`.
This command generate and store data for analysis following `analyconf.toml`.
