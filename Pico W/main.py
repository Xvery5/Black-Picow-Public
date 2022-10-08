# Actually working....
# begun 10-06-22
import gc
import secrets
import time

import dht
import machine
import network
from umqtt.simple import MQTTClient  # type:ignore

wlan = network.WLAN(network.STA_IF)

mcpTemperature = None
dhtTemperature = None
dhtHumidity = None
lightReading = None

# MQTT ...no will just sayin
BUCKET = "HydroPi"
SERVER = "10.0.0.133"
mqttc = MQTTClient("BlackPicow", SERVER)

# onboard
led = machine.Pin("LED", machine.Pin.OUT)

# Photoresistor wired along entire negative rail
photoPin = machine.ADC(26)

# DHT Init
d = dht.DHT11(machine.Pin(17))
dhtPowerPin = machine.Pin(16, machine.Pin.OUT)

# i2c MCP9808
mcp9808 = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))
byte_data = bytearray(2)

gc.enable()


def checkMCP():
    global mcpTemperature
    mcp9808.readfrom_mem_into(24, 5, byte_data)
    value = byte_data[0] << 8 | byte_data[1]
    tempC = (value & 0xFFF) / 16.0  # converts "byte_data" to C
    if value & 0x1000:
        tempC -= 256.0  # formats for temperatures below 0c
    mcpTemperature = tempC
    pubTemperatureMCP()


def connectWIFI():
    SSID = secrets.ssid
    WIFIKEY = secrets.key
    wlan.active(True)
    wlan.connect(ssid=SSID, key=WIFIKEY)
    time.sleep(5)
    print(wlan.ifconfig())


def checkDHT():
    global dhtTemperature
    global dhtHumidity
    dhtPowerPin.on()
    time.sleep(0.4)
    d.measure()
    dhtTemperature = d.temperature()
    dhtHumidity = d.humidity()
    pubTemperatureDHT()
    pubHumidityDHT()
    dhtPowerPin.off()


def checkLight():
    global lightReading
    lightReading = photoPin.read_u16()
    pubLightReading()


def pubTemperatureMCP():
    mqttc.publish("blackpicow/mcptemperature", str(mcpTemperature))
    print("Wrote mcpTemperature {} to: {} @ {}".format(mcpTemperature, BUCKET, SERVER))


def pubTemperatureDHT():
    mqttc.publish("blackpicow/dhttemperature", str(dhtTemperature))
    print("Wrote dhtTemperature {} to: {} @ {}".format(dhtTemperature, BUCKET, SERVER))


def pubHumidityDHT():
    mqttc.publish("blackpicow/dhthumidity", str(dhtHumidity))
    print("Wrote dhtHumidity {} to: {} @ {}".format(dhtHumidity, BUCKET, SERVER))


def pubLightReading():
    mqttc.publish("blackpicow/lightreading", str(lightReading))
    print("Wrote Light Reading {} to: {} @ {}".format(lightReading, BUCKET, SERVER))


connectWIFI()
mqttc.connect()
print("MQTTClient connected to %s" % SERVER)


while True:
    if not wlan.isconnected:
        connectWIFI()
    if wlan.isconnected:
        try:
            checkDHT()
            checkMCP()
            checkLight()
            time.sleep(30)
        finally:
            pass