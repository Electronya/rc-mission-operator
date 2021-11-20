# rc-mission-operator
RC Mission Vehicle Controller

![test](https://github.com/Electronya/rc-mission-operator/actions/workflows/test.yml/badge.svg)
[![coverage](https://codecov.io/gh/Electronya/rc-mission-operator/branch/develop/graph/badge.svg?token=WEAWM1E3HZ)](https://codecov.io/gh/Electronya/rc-mission-operator)

## Setup
```
git clone git@github.com:Electronya/rc-mission-operator.git
cd rc-mission-operator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ln -s ../../rc-mission-common/src/pkgs/messages src/pkgs/messages
ln -s ../../rc-mission-common/src/pkgs/mqttClient src/pkgs/mqttClient
