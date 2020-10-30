import time

from Devices.mqttClient import MqttClient

criticalPacket = {
                "Name": "Alessio",
                "Surname": "Verdi",
                "CF": "VRDLSS97D04F839L",
                "SensorType": "bloodPressure",
                "Value": 40,
                "Position": {
                    "Lat": 41867838,
                    "Long": 12585241
                }
                }

criticalPacket2 = {
                "Name": "Alessio",
                "Surname": "Verdi",
                "CF": "VRDLSS97D04F839L",
                "SensorType": "bloodOxygen",
                "Value": 40,
                "Position": {
                    "Lat": 41867838,
                    "Long": 12585241
                }
                }

normalPacket = {
                "Name": "Alessio",
                "Surname": "Verdi",
                "CF": "VRDLSS97D04F839L",
                "SensorType": "bloodPressure",
                "Value": 70,
                "Position": {
                    "Lat": 41867838,
                    "Long": 12585241
                }
                }


if __name__ == "__main__":
    client = MqttClient("MLSPLA97D04H501U")
    client.connect("localhost", 1883)
    send = 0
    while send < 4:
        client.sendData(criticalPacket, "bloodPressure")
        client.loop()
        time.sleep(2)
        send += 1
    send = 0
    while send < 3:
        client.sendData(criticalPacket, "bloodPressure")
        client.loop()
        time.sleep(2)
        send += 1
    send = 0
    client.sendData(normalPacket,"bloodPressure")
    client.loop()
    client.sendData(criticalPacket, "bloodPressure")
    client.loop()
    while send < 4:
        client.sendData(normalPacket, "bloodPressure")
        client.loop()
        time.sleep(2)
        send += 1
    send = 0
    #manda solo email, ma non cloud
    while send < 4:
        client.sendData(criticalPacket2, "bloodOxygen")
        client.loop()
        time.sleep(2)
        send += 1





