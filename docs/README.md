# weather-station
Home weather station with Raspberry Pi Pico &amp; Kitronik Air Quality Board

![Temperature](https://img.shields.io/badge/temperature-%C2%B0C-blue)
![Pressure](https://img.shields.io/badge/pressure-Pa-green)
![Humidity](https://img.shields.io/badge/humidity-％-yellow)
![IAQ](https://img.shields.io/badge/IAQ-orange)
![eCO2](https://img.shields.io/badge/eCO2-ppm-teal)

![Weather station home](Weather_station_home.png)

# Development

* To run the server go to the ```src``` directory and type:
```
flask --app server run --debug --host=0.0.0.0
```

* The ```rp2``` directory mirrors the scripts that will go onto the Raspberry Pi Pico. 

# Set up

## Pyenv
Use `pyenv` to change the python version for the project directory. 
```
pyenv install 3.11.10
pyenv local 3.11
```
Add the following to your ~/.zshrc:
```
export PATH="/Users/username/.pyenv:$PATH"
eval "$(pyenv init -)"
```


## Poetry
To set up poetry environment:
```
poetry init
poetry shell
poetry install
```

## SQLite Database
From the `src` directory, initialise the SQLite database with:
```
flask --app server init-db
```
The database will appear in the `instance` directory as `weather.sqlite`

## Raspberry Pi Pico W + Kitronik Air Quality Board
* Copy scripts from ```rp2``` onto Raspberry Pi. 
* Change constants at the top of the copy of ```send_data.py``` on the Pico:
```
SERVER_URL = 'localhost'+'/data'
WIFI_NAME = 'Wifi_name'
WIFI_PASSWORD = 'Wifi_password'
```

