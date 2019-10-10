Python3 only

In this directory, only tempcontrol.py was developped by Baylibre to take benefit of pythons libs delivered by Meerstetter.
Original sources for all the sw in this directory except tempcontrol.py can be found here: https://github.com/spomjaksilp/pyMeCom

Prerequesites:
sudo apt-get install python3-serial
sudo apt-get install python3-pip
sudo pip3 install PyCRC

Set Peltier temperature on thermal bench:
python3 ./tempcontrol.py tempvalueC

Example, to set Temp to 20°C:
python3 ./tempcontrol.py 20

Script will execute, return current value until controller stabilized. Exit program when controller is stable.
