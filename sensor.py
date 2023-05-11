import os
import json
import time

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError, SerialTimeoutError
from enviroplus import gas
import ST7735

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
    values["pressure"] = int(bme280.get_pressure())
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


def display_data(values, disp):
    # Width and height to calculate text position
    WIDTH = disp.width
    HEIGHT = disp.height
    # Text settings
    font_size = 12
    font = ImageFont.truetype(UserFont, font_size)

    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170) if check_wifi() else (85, 15, 15)
    
    message = "Temp: {}°C\nhum: {}%\npress: {}hPa".format(
        values["temperature"], values["humidity"], values["pressure"]
    )
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    size_x, size_y = draw.textsize(message, font)
    x = (WIDTH - size_x) / 2
    y = (HEIGHT / 2) - (size_y / 2)
    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((x, y), message, font=font, fill=text_colour)
    disp.display(img)

def main():
    broker = os.environ['MQTT_BROKER']
    port = os.environ['MQTT_PORT']
    topic = os.environ['MQTT_TOPIC']

    mqtt_client = mqtt.Client(client_id='enviroplus-sensor')
    mqtt_client.connect(broker, port=int(port))

    bus = SMBus(1)

    # Create BME280 instance
    bme280 = BME280(i2c_dev=bus)

    # Create LCD instance
    disp = ST7735.ST7735(
        port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000
    )

    # Initialize display
    disp.begin()

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
        display_data(values, disp)
        time.sleep(60)


if __name__ == "__main__":
    main()