FROM debian:buster-slim as target

# Enable OpenRC
ENV INITSYSTEM on 
ENV UDEV=on

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y build-essential git zlib1g-dev libjpeg-dev libfreetype6-dev libffi-dev libportaudio2 alsa-utils python3 python3-pip && \
    pip3 install --upgrade pip &&\
    pip3 install -U setuptools RPI.gpio spidev Pillow paho-mqtt smbus smbus2 sounddevice enviroplus ST7735 numpy pillow fonts

COPY sensor.py/ .

CMD python3 /usr/src/app/sensor.py
