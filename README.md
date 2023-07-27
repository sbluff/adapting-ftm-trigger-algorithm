# adapting-ftm-trigger-algorithm
As a part of my thesis in TU Berlin in the TKN department (https://www.tkn.tu-berlin.de/) I will develop an adapting FTM sampling algorithm for the FTM protocol based on the existing project https://github.com/tkn-tub/wifi-ftm-ns3

## Prerequisites
python version 3.19.17 or lower
gcc version 11.3.0
g++ version 11.3.0

## Installation

1) Install dependencies (https://www.nsnam.org/docs/tutorial/html/getting-started.html)
2) Run ./build.py --enable-examples --enable-tests
3) In case the error ‘numeric_limits’ is not a member of ‘std’ pops up open the file 'csv-reader.cc' and add '#include <limits>' to the import section
4) In case of python error use this commands to downgrade your version:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.9
sudo unlink /usr/bin/python3
sudo ln -s /usr/bin/python3.9 python3
```

## RUN ns3 simulator

sudo ./waf --run scratch/ftm-ranging.cc 