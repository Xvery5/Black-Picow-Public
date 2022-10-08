from datetime import datetime

import influxdb_client
import paho.mqtt.client as mqtt
from influxdb_client.client.write_api import SYNCHRONOUS

token = "TOKEN HERE!"
org = "EMAIL HERE!"
bucket = "BUCKET HERE"
url = "10.0.0.133"

myInfluxClient = influxdb_client.InfluxDBClient(
    url=url, token=token, org=org, bucket=bucket
)
write_api = myInfluxClient.write_api(write_options=SYNCHRONOUS)


def onConnect(mttc, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print()
    mttc.subscribe("blackpicow/#")
    mttc.subscribe("aControlledStorm/#")


def onMessage(mttc, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    if msg.topic == "blackpicow/dhttemperature":
        TemperaturePayLoad = str(msg.payload)
        stemperature = TemperaturePayLoad.strip("'b,")
        cTemperature = float(stemperature)
        # print(cTemperature)
        if (cTemperature >= 0) and (cTemperature <= 100):
            temperaturePoint = (
                influxdb_client.Point("dhtTemperature")
                .tag("Tag", "BlackPicow")
                .field("Temperature", cTemperature)
            )
            write_api.write(bucket=bucket, org=org, record=temperaturePoint)
            print("Wrote temperature data: ", cTemperature)
            print()



    if msg.topic == "blackpicow/mcptemperature":
        TemperaturePayLoad = str(msg.payload)
        stemperature = TemperaturePayLoad.strip("'b,")
        cTemperature = float(stemperature)
        # print(cTemperature)
        if (cTemperature >= 0) and (cTemperature <= 100):
            temperaturePoint = (
                influxdb_client.Point("mcpTemperature")
                .tag("Tag", "BlackPicow")
                .field("Temperature", cTemperature)
            )
            write_api.write(bucket=bucket, org=org, record=temperaturePoint)
            print("Wrote temperature data: ", cTemperature)
            print()


    if msg.topic == "blackpicow/dhthumidity":
        HumidityPayLoad = str(msg.payload)
        shumidity = HumidityPayLoad.strip("b',")
        cHumidity = int(shumidity)
        # print(cHumidity)
        if (cHumidity >= 0) and (cHumidity <= 100):
            humidityPoint = (
                influxdb_client.Point("dhtHumidity")
                .tag("Tag", "BlackPicow")
                .field("Humidity", cHumidity)
            )
            write_api.write(bucket=bucket, org=org, record=humidityPoint)
            print("Wrote humidity data: ", cHumidity)
            print()

    if msg.topic == "blackpicow/waterlevel":
        WaterLevelPayLoad = str(msg.payload)
        swaterlevel = WaterLevelPayLoad.strip("b'")
        cWaterLevel = int(swaterlevel)
        # print(cWaterLevel)
        waterLevelPoint = (
            influxdb_client.Point("waterLevel")
            .tag("Tag", "BlackPicow")
            .field("Water Level", cWaterLevel)
        )
        write_api.write(bucket=bucket, org=org, record=waterLevelPoint)
        print("Wrote water level data: ", cWaterLevel)
        print()

    if msg.topic == "blackpicow/lightreading":
        lightReadingPayLoad = str(msg.payload)
        slightReading = lightReadingPayLoad.strip("b'")
        clightReading = int(slightReading)
        # print(clightReading)
        LightReadingPoint = (
            influxdb_client.Point("lightReading")
            .tag("Tag", "BlackPicow")
            .field("Light Reading", clightReading)
        )
        write_api.write(bucket=bucket, org=org, record=LightReadingPoint)
        print("Wrote Light Sensor data: ", clightReading)
        print()

    if msg.topic == "acontrolledstorm/temperature":
        TemperaturePayLoad = str(msg.payload)
        stemperature = TemperaturePayLoad.strip("'b,")
        stormTemperature = float(stemperature)
        # print(stormTemperature)
        if (stormTemperature >= 0) and (stormTemperature <= 100):
            temperaturePoint = (
                influxdb_client.Point("dhtTemperature")
                .tag("Tag", "aControlledStorm")
                .field("Temperature", stormTemperature)
            )
            write_api.write(bucket=bucket, org=org, record=temperaturePoint)
            print("Wrote temperature data: ", stormTemperature)
            print()

    if msg.topic == "acontrolledstorm/humidity":
        HumidityPayLoad = str(msg.payload)
        shumidity = HumidityPayLoad.strip("b',")
        cHumidity = int(shumidity)
        # print(cHumidity)
        if (cHumidity >= 0) and (cHumidity <= 100):
            humidityPoint = (
                influxdb_client.Point("dhtHumidity")
                .tag("Tag", "aControlledStorm")
                .field("Humidity", cHumidity)
            )
            write_api.write(bucket=bucket, org=org, record=humidityPoint)
            print("Wrote humidity data: ", cHumidity)
            print()

    if msg.topic == "acontrolledstorm/waterlevel":
        WaterLevelPayLoad = str(msg.payload)
        swaterlevel = WaterLevelPayLoad.strip("b'")
        cWaterLevel = int(swaterlevel)
        # print(cWaterLevel)
        waterLevelPoint = (
            influxdb_client.Point("waterLevel")
            .tag("Tag", "aControlledStorm")
            .field("Water Level", cWaterLevel)
        )
        write_api.write(bucket=bucket, org=org, record=waterLevelPoint)
        print("Wrote water level data: ", cWaterLevel, "under aControlledStorm")
        print()


mttc = mqtt.Client(client_id="Raspberry4Paho")
mttc.on_connect = onConnect
mttc.on_message = onMessage

mttc.connect("10.0.0.133", 1883, 120)

mttc.loop_forever()