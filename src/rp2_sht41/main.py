"""
Send temperature, humidity data from a SHT4x sensor to a server.

The server address, WiFi credentials, and update period are defined as constants
at the beginning of the script and should be changed as required.

After sending the data, the script will enter deep sleep mode for the specified
period, before waking up and running the main.py script again.
"""

import errno
import time

import urequests
from hardware import (
    connect_to_wifi,
    deactivate_wifi,
    get_iso_datetime,
    read_location,
    read_pressure,
    read_sht4x,
    read_vsys,
)
from machine import deepsleep, unique_id

start_time = time.ticks_ms()

# Constants
WIFI_NAME = "Wifi_name"
WIFI_PASSWORD = "Wifi_password"
SERVER = "http://localhost:5000"
UPDATE_PERIOD = 60 * 5  # seconds

uid = "".join("{:02x}".format(x) for x in unique_id())  # pico hardware-based unique ID

voltage = read_vsys()
location = read_location()
temperature, relative_humidity = read_sht4x()
pressure = read_pressure()

wlan = connect_to_wifi(WIFI_NAME, WIFI_PASSWORD)
# TODO: re-enable once time-setting is working again
# set_rtc_time()
# ntptime.settime()

# print("retrieved time from NTP server")
# print("current time:", get_iso_datetime())

payload = {
    "timestamp": get_iso_datetime(),
    "uid": uid,
    "location": location,
    "voltage": voltage,
    "temperature": temperature,
    "humidity": relative_humidity,
    "pressure": pressure,
    "air_quality": 0,
    "e_co2": 0,
}
# Remove any measurements that are None
# TODO: re-enable when server is able to handle missing parameters
# payload = {key: value for key, value in payload.items() if value is not None}

headers = {"Content-Type": "application/json"}

try:
    # Send data to the server
    response = urequests.post(url=SERVER + "/data", headers=headers, json=payload)
    response.close()
    print("Payload successfully sent")
except OSError as e:
    if e.errno == errno.ECONNABORTED:
        print("Connection aborted (ECONNABORTED)")
        print("Server not found")
    else:
        print("Error sending payload:", e)
except Exception as e:
    print("Error sending payload:", e)
    print("could not connect (status = " + str(wlan.status()) + ")")

deactivate_wifi(wlan)

end_time = time.ticks_ms()
time_taken = time.ticks_diff(end_time, start_time)
time_sleep = UPDATE_PERIOD * 1000 - time_taken

print("Going to sleep for", time_sleep, "seconds")
deepsleep(time_sleep)
