# rc-mission-operator
RC Mission Vehicle Controller

## Setup
```
git clone git@github.com:Electronya/rc-mission-operator.git
cd rc-mission-operator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ln -s ../../rc-mission-common/src/messages src/client/messages
