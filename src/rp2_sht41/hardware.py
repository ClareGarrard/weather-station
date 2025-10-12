"""Hardware-related functions for the Raspberry Pi Pico."""

import socket
import struct
import time
from time import gmtime

import network
from machine import ADC, I2C, RTC, Pin
from micropython_dps310 import dps310
from micropython_sht4x import sht4x

NTP_DELTA = 2208988800
NTP_HOST = "pool.ntp.org"

led = Pin("LED", Pin.OUT)
rtc = RTC()
i2c = I2C(0, sda=Pin(4), scl=Pin(5))


def read_location():
    """
    Read the sensor location from the header pins on the proto-board.

    Returns an integer from 0 to 15.
    """
    headers = {
        6: "Downstairs",  # 1
        7: "Front",  # 2
        8: "East",  # 4
        9: "Debug",  # 8
    }
    # setup pins as inputs, with pull-up resistors
    pins = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in sorted(headers)]
    # read the values
    total = sum([pin.value() << i for i, pin in enumerate(pins)])
    return 15 - total


def read_vsys():
    """
    Read the system voltage from the ADC, disabling the WLAN chip to avoid interference.

    Source: https://www.reddit.com/r/raspberrypipico/comments/xalach/comment/ipigfzu/
    """
    CONVERSION_FACTOR = 3 * 3.3 / 65535
    wlan = network.WLAN(network.STA_IF)
    wlan_active = wlan.active()

    try:
        # Don't use the WLAN chip for a moment.
        wlan.active(False)

        # Make sure pin 25 is high.
        Pin(25, mode=Pin.OUT, pull=Pin.PULL_DOWN).high()

        # Reconfigure pin 29 as an input.
        Pin(29, Pin.IN)
        vsys = ADC(29)

        # Take the average of 5 voltage readings
        readings = []
        for _ in range(5):
            time.sleep(0.1)  # Small delay before reading
            voltage = vsys.read_u16() * CONVERSION_FACTOR
            readings.append(voltage)

        average_voltage = sum(readings) / len(readings)
        return round(average_voltage, 3)

    finally:
        # Restore the pin state and possibly reactivate WLAN
        Pin(29, Pin.ALT, pull=Pin.PULL_DOWN, alt=7)
        wlan.active(wlan_active)


def read_sht4x():
    """Read temperature and humidity from the SHT4x sensor."""
    try:
        sht = sht4x.SHT4X(i2c)
        sht.temperature_precision = sht4x.HIGH_PRECISION
        temperature, relative_humidity = sht.measurements
        temperature = round(temperature, 2)
        relative_humidity = round(relative_humidity, 2)
    except Exception as e:
        print("Error reading SHT4x sensor:", e)
        temperature = None
        relative_humidity = None

    return temperature, relative_humidity


def read_pressure():
    """Read pressure from the DPS310 sensor."""
    try:
        dps = dps310.DPS310(i2c)
        dps.pressure_oversample = dps310.SAMPLE_PER_SECOND_128
        dps.pressure_rate = dps310.RATE_128_HZ
        dps.temperature_oversample = dps310.SAMPLE_PER_SECOND_128
        dps.temperature_rate = dps310.RATE_128_HZ
        dps.mode = dps310.ONE_PRESSURE

        # Wait for the sensor to stabilise
        dps._wait_pressure_ready()

        raw_pressure = dps.pressure  # in hPa
        pressure = round(raw_pressure * 100)  # in Pa
    except Exception as e:
        print("Error reading DPS310 sensor:", e)
        pressure = None

    return pressure


def connect_to_wifi(wifi_name, wifi_password):
    """
    Connect to WiFi network using the given SSID and password.

    Based on the example from the MicroPython documentation, 3.6. Connecting to a wireless network:
    https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf with LED feedback.

    The function will attempt to connect to the network and will toggle the onboard LED while waiting.
    If the connection is successful, the LED will turn off and the IP address will be printed.
    If the connection fails, the LED will turn on and an error will be raised.
    """
    global led
    led.on()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_name, wifi_password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("waiting for connection...")
        led.toggle()
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        led.on()
        print("network connection failed")
    else:
        led.off()
        print("connected")
        status = wlan.ifconfig()
        print("ip = " + status[0])

    return wlan


def deactivate_wifi(wlan):
    """Completely deactivate the WiFi interface."""
    wlan.disconnect()
    wlan.active(False)
    wlan.deinit()
    print("WiFi deactivated")


def set_rtc_time() -> None:
    # Get the external time reference
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(10)
        s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()

    # Set our internal time
    val = struct.unpack("!I", msg[40:44])[0]
    tm = val - NTP_DELTA
    t = gmtime(tm)
    rtc.datetime((t[0], t[1], t[2], t[6] + 1, t[3], t[4], t[5], 0))


def get_iso_datetime() -> str:
    year, month, day, _dow, hour, mins, secs, _subsec = rtc.datetime()
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(year, month, day, hour, mins, secs)
