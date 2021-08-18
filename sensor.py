import os
import json
import time

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError, SerialTimeoutError
from enviroplus import gas

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559

    ltr559 = LTR559()
except ImportError:
    import ltr559

def readGasSensor():
    values = {}

    data = gas.read_all()

    values["oxidised"] = int(data.oxidising / 1000)
    values["reduced"] = int(data.reducing / 1000)
    values["nh3"] = int(data.nh3 / 1000)
    values["lux"] = int(ltr559.get_lux())
    return values

def readEnvironmentData(bme280):
    values = {}
    values["temperature"] = int(bme280.get_temperature())
    values["pressure"] = int(bme280.get_pressure() * 100)
    values["humidity"] = int(bme280.get_humidity())
    return values

def getParticleData(pms5003):
    values = {}
    try:
        pm_values = pms5003.read()  # int
        values["pm1"] = pm_values.pm_ug_per_m3(1)
        values["pm25"] = pm_values.pm_ug_per_m3(2.5)
        values["pm10"] = pm_values.pm_ug_per_m3(10)
    except ReadTimeoutError:
        pms5003.reset()
        pm_values = pms5003.read()
        values["pm1"] = pm_values.pm_ug_per_m3(1)
        values["pm25"] = pm_values.pm_ug_per_m3(2.5)
        values["pm10"] = pm_values.pm_ug_per_m3(10)
    return values


def main():
    broker = os.environ['MQTT_BROKER']
    port = os.environ['MQTT_PORT']
    topic = os.environ['MQTT_TOPIC']

    mqtt_client = mqtt.Client(client_id='enviroplus-sensor')
    mqtt_client.connect(broker, port=int(port))

    bus = SMBus(1)

    # Create BME280 instance
    bme280 = BME280(i2c_dev=bus)

    # Try to create PMS5003 instance
    HAS_PMS = False
    pms5003 = None
    
    while True:
        if not HAS_PMS:
            try:
                pms5003 = PMS5003()
                pm_values = pms5003.read()
                HAS_PMS = True
                print("PMS5003 sensor is connected")
            except Exception as e:
                print('Error setting up PMS5003')
                print(e)

        values = {}

        try:
            values.update(readGasSensor())
        except Exception as e:
            print('Error trying to get Gas data')
            print(e)
        
        try:
            values.update(readEnvironmentData(bme280))
        except Exception as e:
            print('Error trying to get Environment data')
            print(e)

        try:
            values.update(readEnvironmentData(bme280))
        except Exception as e:
            print('Error trying to get Environment data')
            print(e)
        
        if HAS_PMS:
            try:
                values.update(getParticleData(pms5003))
            except Exception as e:
                print('Error trying to get Particle data')
                print(e)


        mqtt_client.publish(topic, json.dumps(values))
        print("Published values {}".format(values))
        time.sleep(60)


if __name__ == "__main__":
    main()