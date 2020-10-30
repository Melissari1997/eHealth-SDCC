import json
import time
import requests
from flask import Flask
from paho.mqtt.client import Client

mqttSubscriber = Flask(__name__)
"""
MQTT client che si sottoscrive al broker per ricevere i dati
"""
def send(message):
    # dataToSend = json.dumps(message).encode('utf-8')
    res = requests.post("http://healthchecker:5000/sendData", json=message)
    # print(res.content, flush=True)
    content = json.loads(res.content)
    client.publish("/speedTest", content["difference"])


def on_connect(client, userdata, flags, rc):
    client.loop_start()  # start the loop
    client.subscribe("pazienti/bloodPressure", qos=1)
    client.subscribe("pazienti/heartbeat", qos=1)
    client.subscribe("pazienti/bloodOxygen", qos=1)
    client.subscribe("pazienti/movement", qos=1)
    time.sleep(1)


############
def on_message(mqttClient, userdata, message):
    # print("message received from sensor", str(message.payload.decode("utf-8")))
    send(json.loads(message.payload))
    # time.sleep(0.1)


client = Client("MqttSubscriber", clean_session=False)
broker_address = "broker"
client.on_message = on_message  # attach function to callback
client.on_connect = on_connect
client.connect(broker_address, keepalive=320)  # connect to broker
client.loop_start()  # start the loop
time.sleep(3)

if __name__ == "__main__":
    # broker_address = "localhost"

    mqttSubscriber.run(host='0.0.0.0', port=8080)
