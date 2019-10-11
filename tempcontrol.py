#!/usr/bin/env python3
"""

"""
import logging
import time
import sys
from mecom import MeCom, ResponseException, WrongChecksum
from serial import SerialException
sys.path.insert(0, '../../')
from lib.serial import connectSerialPort
#sys.path.insert(0, '../../utils')
from lib.utils import confFile

serial_hwid_default = "UNKNOWN"

# default queries from command table below
DEFAULT_QUERIES = [
    "loop status",
    "object temperature",
    "target object temperature",
    "output current",
    "output voltage",
    "sink temperature",
]

# syntax
# { display_name: [parameter_id, unit], }
COMMAND_TABLE = {
    "loop status": [1200, ""],
    "object temperature": [1000, "degC"],
    "target object temperature": [1010, "degC"],
    "output current": [1020, "A"],
    "output voltage": [1021, "V"],
    "sink temperature": [1001, "degC"],
    "ramp temperature": [1011, "degC"],
}


class MeerstetterTEC(object):
    """
    Controlling TEC devices via serial.
    """

    def _tearDown(self):
        self.session().stop()

    def __init__(self, port="/dev/ttyUSB0", channel=1, queries=DEFAULT_QUERIES, *args, **kwars):
        assert channel in (1, 2)
        self.channel = channel
        self.port = port
        self.queries = queries
        self._session = None
        self._connect()

    def _connect(self):
        # open session
        self._session = MeCom(serialport=self.port)
        # get device address
        self.address = self._session.identify()
        logging.info("connected to {}".format(self.address))

    def session(self):
        if self._session is None:
            self._connect()
        return self._session

    def get_temp(self):
        return self.session().get_parameter(parameter_name="Object Temperature", address=self.address)

    def get_data(self):
        data = {}
        for description in self.queries:
            id, unit = COMMAND_TABLE[description]
            try:
                value = self.session().get_parameter(parameter_id=id, address=self.address, parameter_instance=self.channel)
                data.update({description: (value, unit)})
            except (ResponseException, WrongChecksum) as ex:
                self.session().stop()
                self._session = None
        return data

    def set_temp(self, value):
        """
        Set object temperature of channel to desired value.
        :param value: float
        :param channel: int
        :return:
        """
        # assertion to explicitly enter floats
        assert type(value) is float
        logging.info("set object temperature for channel {} to {} C".format(self.channel, value))
        return self.session().set_parameter(parameter_id=3000, value=value, address=self.address, parameter_instance=self.channel)

    def _set_enable(self, enable=True):
        """
        Enable or disable control loop
        :param enable: bool
        :param channel: int
        :return:
        """
        value, description = (1, "on") if enable else (0, "off")
        logging.info("set loop for channel {} to {}".format(self.channel, description))
        return self.session().set_parameter(value=value, parameter_name="Status", address=self.address, parameter_instance=self.channel)

    def enable(self):
        return self._set_enable(True)

    def disable(self):
        return self._set_enable(False)
        
def setPeltierTempImmediate(serial_hwid, tempTarget, configFile = "UNKNOWNconfFile.ini"):
    port = connectSerialPort.get_serial_port(serial_hwid)
    if serial_hwid  == serial_hwid_default:
        serial_hwid = connectSerialPort.get_serial_hwid_by_port(port)
        print("peltier_serial_hwid = " + serial_hwid)
        confFile.update(configFile, "TEMPBENCH", "peltier_serial_hwid", serial_hwid)
    # start logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")
    # initialize controller
    print(port)
    mc = MeerstetterTEC(port)

    # get the values from DEFAULT_QUERIES
    print(mc.get_data())
    ret = mc.set_temp(float(tempTarget))
    return ret

def setPeltierTemp(serial_hwid, tempTarget, configFile = "UNKNOWNconfFile.ini"):
    port = connectSerialPort.get_serial_port(serial_hwid)
    if serial_hwid  == serial_hwid_default:
        serial_hwid = connectSerialPort.get_serial_hwid_by_port(port)
        print("peltier_serial_hwid = " + serial_hwid)
        confFile.update(configFile, "TEMPBENCH", "peltier_serial_hwid", serial_hwid)
    # start logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")
    # initialize controller
    print(port)
    mc = MeerstetterTEC(port)

    # get the values from DEFAULT_QUERIES
    print(mc.get_data())
    mc.set_temp(float(tempTarget))
    time.sleep(2) # wait to exit stability conditions
    stable = "is stable"
    stable_id = mc.session().get_parameter(parameter_name="Temperature is Stable", address=mc.address)
    while stable_id == 1:
        stable = "is not stable"
        temp = str(round(mc.get_temp(),2))
        print("query for loop stability, loop {}, ".format(stable) + "obj temp: " + temp)
        time.sleep(5)
        stable_id = mc.session().get_parameter(parameter_name="Temperature is Stable", address=mc.address)
    if stable_id == 0:
        stable = "temperature regulation is not active"
    elif stable_id == 2:
        stable = "is stable"
    else:
        stable = "state is unknown"
        
    print("exit program with stability status: " + stable)
    #print(mc.get_data())
    data = mc.get_data()
    print(data)
    return stable
    
def readPeltierTemp(serial_hwid, tempTarget, configFile = "UNKNOWNconfFile.ini"):
    port = connectSerialPort.get_serial_port(serial_hwid)
    if serial_hwid  == serial_hwid_default:
        serial_hwid = connectSerialPort.get_serial_hwid_by_port(port)
        print("peltier_serial_hwid = " + serial_hwid)
        confFile.update(configFile, "TEMPBENCH", "peltier_serial_hwid", serial_hwid)
    # start logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")
    # initialize controller
    print(port)
    mc = MeerstetterTEC(port)

    # get the values from DEFAULT_QUERIES
    print(mc.get_data())
    temp = str(round(mc.get_temp(),2))
    print("Peltier temp is: " + temp)
    return temp
    
if __name__ == '__main__':
    #serial_hwid = "UNKNOWN"
    serial_hwid = "0403:6015"	
    nargs = len(sys.argv)
    if (nargs == 2):
        tempTarget = sys.argv[1]
    else:
        print("enter a temperature target in Celsius as argument")
        exit()
    ret = setPeltierTemp(serial_hwid, tempTarget)
    print(ret)
    ret = readPeltierTemp(serial_hwid, tempTarget)
    print(ret)
    #return ret
