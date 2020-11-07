import time

from Devices.mqttClient import MqttClient
"""
Test per verificare che il sitema di invio email 
"""
mediumPacket = {"Name": "Paolo",
                "Surname": "Melissari",
                "CF": "RSSLSS97D04H501N",
                "SensorType": "bloodPressure",
                "Value": 52,
                "Position": {
                    "Lat": 41867838,
                    "Long": 12585241
                }
                }

normalPacket = {"Name": "Paolo",
                "Surname": "Melissari",
                "CF": "RSSLSS97D04H501N",
                "SensorType": "bloodPressure",
                "Value": 70,
                "Position": {
                    "Lat": 41867838,
                    "Long": 12585241
                }
                }

if __name__ == "__main__":
    client = MqttClient("MLSPLA97D04H501U")
    client.connect("localhost", 1883,0)

    #invio email
    send = 0
    while send < 4:
        client.sendData(mediumPacket, "bloodPressure")
        client.loop()
        time.sleep(1)
        send += 1
    #non invia, perchè già ha inviato
    while send < 3:
        client.sendData(mediumPacket, "bloodPressure")
        client.loop()
        time.sleep(1)
        send += 1

    client.sendData(normalPacket,"bloodPressure")
    client.loop()
    client.sendData(mediumPacket, "bloodPressure")
    client.loop()

    while send < 4:
        client.sendData(normalPacket, "bloodPressure")
        client.loop()
        time.sleep(1)
        send += 1

    #non invia l'email se non sono passati almeno 15 minuti
    while send < 4:
        client.sendData(mediumPacket, "bloodPressure")
        client.loop()
        time.sleep(1)
        send += 1




