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
from numbers import Number
import math

from pitmaster.exceptions import *


def convert_to_resistance(reading=None):
    resistor_size = 10000
    r1 = (1023.0 / reading) - 1.0
    resistance = resistor_size / r1
    return resistance


def resistance_to_temp(resistance=None):
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


def from_c_to_f(temp=None):
    """
    Converts a given temp from Celsius to fahrenheit

    :param temp:
    :return:
    """
    if temp is None:
        raise MissingPropertyException("temp can not be None!")
    if not isinstance(temp, Number):
        raise InvalidPropertyException(
            "temp must be a valid number. Found: {}".format(type(temp))
        )
    return (temp * 9 / 5) + 32.0
