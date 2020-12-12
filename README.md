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
This command generate and store data for analysis according to `analyconf.toml`.

## Sample Flow
The sytra workflow consists of data preparation and `follow` or `analyze` command.
Try how to use `sytra` with the sample in `sytra/data_sample`.

---
***Note:** Keep in mind that the data you want to analyze must be prepared by yourself*.

---
***Note:** If you installed using Docker,
run `/bin/bash` in a container created by sytra image in advance.*
```bash
    docker run -it -v sytra-stocks:/root/data sytra:latest /bin/bash
```

---

If you have taken the above installing step, 
the stocks directory-tree looks like below.
```
    $STOCKROOT/
    |-- holidays
    |-- log
    |   `-- trash
    |-- prepare
    `-- sytraconf.toml
```
First, register the holiday data as file.
Sytra requires yearly schedule with no stock-trading day.
`data_sample/h2020` and `data_sample/h2021` are the correct one for it.
```bash
    # must be $STOCKROOT/holidays/YYYY.csv
    cp data_sample/h2020 $STOCKROOT/holidays/2020.csv
    cp data_sample/h2021 $STOCKROOT/holidays/2021.csv
```

There are two things to do before following
1. move( or copy) the stock data to `prepare/`
1. rewrite the 'latest' variable in `sytracong.toml`
```bash
    # copy sample to prepare/
    # these are the sample stock data
    cp data_sample/9999.csv $STOCKROOT/prepare
    cp data_sample/1111.csv $STOCKROOT/prepare

    # rewrite latest="..." -> latest="2020-07-10"
    # Must match the latest date of the prepared data(9999.csv).
    sed -i '$d' $STOCKROOT/sytraconf.toml
    echo 'latest = "2020-07-13"' >> $STOCKROOT/sytraconf.toml
```
Now, you can use `follow` command.
```bash
    sytra follow
```
This is just a process 
to make sytra recognize two sample stock data
that are treated as code '1111' and '9999'.

To generate data available to users, 
it is important to make settings for individual stocks
and call `analyze -C`.
The prepared `ac1111` and `ac9999` can be used as `analyconf.toml`.
```bash
    # there is also a default config file
    cp -f data_sample/ac1111 $STOCKROOT/1111/analyconf.toml
    cp -f data_sample/ac9999 $STOCKROOT/9999/analyconf.toml

    # data generation according to analyconf.toml
    sytra analyze -C
```

Next, if you get the data for 2020-07-13(sample filename: 'summary\_0713.csv'),
it must be as `$STOCKROOT/summary.csv`.
And if so, it is possible to call `analyze`.
```bash
    # must be $STOCKROOT/summary.csv'
    cp data_sample/summary_0713.csv $STOCKROOT/summary.csv

    # data generation according to analyconf.toml
    sytra analyze
    # summary.csv is moved into $STOCKROOT/log/%Y%m%d
```

Delete the code you no longer need to analyze
with the `follow` and `-d` option.
The specified code is no longer recognaized by sytra.
```bash
    # data will be moved to the $STOCKROOT/loga/trash
    sytra follow -d 1111 9999
```
