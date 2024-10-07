"""Hardware-related functions for the Raspberry Pi Pico."""

from machine import ADC, Pin
import network
import time

led = Pin("LED", Pin.OUT)


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


def connect_to_wifi(wifi_name, wifi_password):
    """Connect to WiFi network using the given SSID and password.

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
