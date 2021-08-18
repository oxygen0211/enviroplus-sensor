# Enviro+ to MQTT adapter

A small script that connects the [Enviro+ sensor board](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-enviro-plus) and an optional PMS5003 particulate matter sensor to MQTT - without all the extra fuss that the official example is doing.

I'm using this myself to create an air quality sensor for my smart home using [Home Assistant MQTT Sensor](https://www.home-assistant.io/integrations/sensor.mqtt/)

## Building

Build normally with Docker build or Docker buildx according to your requirements.

e.g

```
docker buildx build --push --platform linux/arm/v7 -t oxygen0211/enviroplus-mqtt .
```

## Running
Make sure to set the environment variables `MQTT_BROKER` `MQTT_PORT` and `MQTT_TOPIC` and run either with Python 3
```
python3 sensor.py
```
(this will only work on a Rapsberry Pi with the enviro+ attached)

or using the Docker image

```
docker run -e MQTT_BROKER=localhost -e MQTT_PORT=1883 -e MQTT_TOPIC=airquality oxygen0211/enviroplus-mqtt
```

... or adapt accordingly in your Orchestrator of choice...