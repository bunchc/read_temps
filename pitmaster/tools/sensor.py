#   Copyright 2016 Michael Rice <michael@michaelrice.org>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import os
import time
import math
import RPi.GPIO as GPIO

from pitmaster.exceptions import *

SPICLK = 18
SPIMOSI = 24
SPIMISO = 23
SPICS = 25

GPIO.setmode(GPIO.BCM)
DEBUG = 1
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)


def _temp_raw(sensor=None):
    with open(sensor, "r") as file_reader:
        lines = file_reader.readlines()
    return lines


def _read_thermistor(sensor=None):
    adcnum = int(sensor)
    clockpin = SPICLK
    mosipin = SPIMOSI
    misopin = SPIMISO
    cspin = SPICS

    if ((adcnum > 7) or (adcnum < 0)):
        raise SensorNotFoundException("Invalid Thermisor Location: {}".format(sensor))

    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here

    for i in range(5):
            if (commandout & 0x80):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1       # first bit is 'null' so drop it
    resistor_size = 10000
    r1 = (1023.0 / adcout) - 1.0
    if r1 > 0:
        resistance = resistor_size / r1
    else:
        return -1

    sth_coef_a = 0.000436925136556
    sth_coef_b = 0.000230203788274
    sth_coef_c = 0.000000060486575

    if resistance is None:
        raise MissingPropertyException("resistance can not be None!")
    t = sth_coef_a
    t += sth_coef_b * (math.log(resistance))
    t += sth_coef_c * math.pow((math.log(resistance)), 3)
    t = 1 / t
    t -= 273.15
    return t


def read_temp(sensor=None, offset=None, probe_type=None):
    """
    Reads the temp sensor and returns its temp in C.

    :param sensor: Full path to the sensor file to read from
    :param offset: Offset in degrees C from a standard reference
    :return: Temp in C
    """
    if sensor is None:
        raise MissingPropertyException("sensor must not be None!")
    if probe_type is None:
        raise MissingPropertyException("must specify probe type!")
    if offset is None:
        offset = 0
    if probe_type != "thermistor":
        if not os.path.isfile(sensor):
            raise SensorNotFoundException("Unable to locate: {}".format(sensor))
        lines = _temp_raw(sensor)
        while lines[0].strip()[-3] != 'Y':
            time.sleep(0.2)
            lines = _temp_raw()
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output + 2:]
            temp_c = (float(temp_string) / 1000.0) + offset
            return temp_c
    else:
        temp_c = _read_thermistor(sensor) + offset
        return temp_c


def find_temp_sensors(probe_type=None):
    """
    Looks on system for temp sensors and returns all that it finds in a list

    :return list: List containing all sensors.
    """
    if probe_type is None:
        raise MissingPropertyException("probe type must be set!")

    if probe_type == "thermistor":
        return [
            {
                "name": "Probe 1",
                "location": "0"
            },
            {
                "name": "Probe 2",
                "location": "1"
            },
            {
                "name": "Probe 3",
                "location": "2"
            }
        ]
    else:
        # Hard coded for now while we work out the best way to handel this.
        return [
            {
                "name": "Probe 1",
                "location": "/sys/bus/w1/devices/3b-0000001921e8/w1_slave"
            }
        ]


if __name__ == "__main__":
    for i in range(15):
        test = read_temp(sensor="/sys/bus/w1/devices/3b-0000001921e8/w1_slave")
        print test
