import json
import time
import paho.mqtt.client as mqtt

from Devices import dataThread
from Devices.dataThread import getNearestFog
"""
Client MQTT che invia e riceve dati dal broker
"""

def on_connect(client, userdata, flags, rc):
    print(client._client_id, "Connected with result: " + mqtt.error_string(rc))


def on_disconnect(client, userdata, rc):
    print(client._client_id, "Disconnected with result: " + mqtt.error_string(rc))



class MqttClient:
    id = ""
    client = None

    def __init__(self, identifier):
        self.id = identifier
        self.client = mqtt.Client(self.id)  # create new instance
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.brokerPort = None
        self.hostname = None


    def connect(self, hostname, brokerPort):
        self.brokerPort = brokerPort
        self.hostname = hostname
        self.client.connect(hostname, port=brokerPort, keepalive=540)  # connect to broker
       # time.sleep(0.2)

    def setPort(self, port):
        self.client._port = port

    def disconnect(self):
        self.client.disconnect()
        #time.sleep(0.2)

    # time.sleep(0.1)
    #   self.client.loop_start()  # start the loop

    def loop(self):
        try:
            self.client.loop()
        except:
            pass

    def sendData(self, data, sensorName):
        topic = "pazienti/" + str(sensorName)
        qos = 0
        if sensorName == "movement":
            qos = 1
        res = self.client.publish(topic, json.dumps(data), qos=qos)
        self.loop()
        print("Client: ", self.id, " sent message for sensor ", sensorName, ": ", data["Value"], ". Message ID: ",
              res[1], ". Result: ", mqtt.error_string(res[0]))

        #cambia fog node se quello attuale si è disconnesso
        if res[0] != 0:
            print("Res: ", res[0])
            self.client.disconnect()
            time.sleep(2)
            print("Changing with port ignore = ", self.brokerPort)
            nextFog = dataThread.getNearestFog(data["Position"]["Lat"],data["Position"]["Long"],self.brokerPort)
            print(nextFog)
            if nextFog is not None:
                print("Connected: ", self.client.is_connected())
                changed = False
                while not changed:
                        time.sleep(3)
                        try:
                         self.connect(self.hostname, nextFog['port'])
                         changed = True
                        except:
                            print("Retry with previous node")
                            time.sleep(1)
                            try:
                             self.connect(self.hostname, self.brokerPort)
                             changed = True
                            except:
                                print("Retry")
                                time.sleep(1)

