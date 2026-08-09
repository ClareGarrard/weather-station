import math


def round_sig(x, sig=3):
    """
    Round to significant figures.

    Source: https://stackoverflow.com/a/3413529
    """
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


def calc_dew_point(relative_humidity, temperature):
    """
    Calculate the dew point, given the relative humidity and temperature, using the Magnus formula.

    Args:
        humidity (float): The relative humidity.
        temperature (float): The temperature in degrees Celsius.

    Returns:
        float: The dew point in degrees Celsius.

    Sources:
        https://gist.github.com/sourceperl/45587ea99ff123745428?permalink_comment_id=5119362#gistcomment-5119362
        https://journals.ametsoc.org/view/journals/apme/35/4/1520-0450_1996_035_0601_imfaos_2_0_co_2.xml
    """
    a = 17.625
    b = 243.04
    alpha = math.log(relative_humidity / 100.0) + ((a * temperature) / (b + temperature))
    dewpoint = (b * alpha) / (a - alpha)

    return round_sig(dewpoint, 4)


def calc_absolute_humidity(relative_humidity, temperature):
    """
    Calculate the absolute humidity given the relative humidity and temperature.

    Args:
        humidity (float): The relative humidity.
        temperature (float): The temperature in degrees Celsius.

    Returns:
        float: The absolute humidity in g/m³.

    Sources:
        https://carnotcycle.wordpress.com/2012/08/04/how-to-convert-relative-humidity-to-absolute-humidity/
        https://journals.ametsoc.org/view/journals/apme/35/4/1520-0450_1996_035_0601_imfaos_2_0_co_2.xml
        https://en.wikipedia.org/wiki/Vapour_pressure_of_water
    """
    # saturation vapour pressure at 0°C in hPa
    e0 = 6.1094
    # empirical constants from Alduchov and Eskridge, 1996, equation (21)
    a = 17.625
    b = 243.04
    # Magnus formula for saturation vapour pressure
    saturation_vapor_pressure = e0 * math.exp((a * temperature) / (temperature + b))
    vapor_pressure = saturation_vapor_pressure * relative_humidity
    absolute_humidity = 2.1674 * vapor_pressure / (273.15 + temperature)

    return round_sig(absolute_humidity, 4)
