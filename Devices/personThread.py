import json
import random
import time
from random import randint
from threading import Thread


def getFogList():
    with open("settings/fogDiscovery.json") as configFile:
        data = json.load(configFile)
        configFile.close()
        fogList = []
        for fogNode in data:
            fogList.append(fogNode)
        return fogList


def getActualPosition(person):
    sensors = person["Sensors"]
    for sensor in sensors:
        if sensor["SensorType"] == "position":
            return sensor["ActualPosition"]
    return "Position Undefined"


def setNewPosition(person):
    fogIdList = []
    for fogNode in fogList:
        if fogNode["FogId"] != person["ActualZone"]:
            fogIdList.append(fogNode["FogId"])
    newPosSelect = random.choice(fogIdList)
    newPos = fogList[newPosSelect]
    posCoordinates = {
        "Lat": newPos["Latitude"],
        "Long": newPos["Longitude"]
    }
    return (newPos, posCoordinates)


def getProbability():
    with open("settings/dataCreatorConfig.json") as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


def getSensorInterval(sensorsList, sensorType):
    for sensor in sensorsList:
        if sensor["name"] == sensorType:
            return sensor["interval"]


def getSensorList():
    with open('settings/sensorTypes.json') as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


probabilities = getProbability()
mediumProb = probabilities["MediumProbability"]
criticalProb = probabilities["CriticalProbability"]
changeZoneProb = probabilities["ChangeZoneProbability"]
fogList = getFogList()
sensors = getSensorList()


class PersonThread(Thread):
    name = ""
    interval = 0
    person = []
    connectors = {}

    def __init__(self,mqttConnectorsList, persons):
        super().__init__()
        self.persons = persons
        self.sensor = sensor
        self.interval = interval
        self.connectors = mqttConnectorsList

    def changeBroker(self, broker, person):
        self.connectors[person["CodiceFiscale"]].disconnect()
        port = broker['port']
        self.connectors[person["CodiceFiscale"]].setPort(port)
        self.connectors[person["CodiceFiscale"]].connect("localhost", port)

    def setPosition(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    changeZone = randint(0, 100)
                    if 0 < changeZone < changeZoneProb:
                        newPos = setNewPosition(person)
                        newCoordinates = newPos[1]
                        broker = newPos[0]
                        person["ActualZone"] = broker["FogId"]
                        self.changeBroker(broker, person)
                        sensor["ActualPosition"] = newCoordinates
                        print("Changed fog node :", person["CodiceFiscale"], "New fog node: ", person["ActualZone"])

                    if sensor["SensorType"] == self.name:
                        move = randint(0, 100)
                        if 0 <= move < 100:
                            lat = sensor["ActualPosition"]["Lat"]
                            long = sensor["ActualPosition"]["Long"]
                            randVal = randint(0, 100)
                            if 0 <= randVal < 5:
                                lat = lat + 1000
                                long = long + 1000
                            if 5 <= randVal < 20:
                                lat = lat + 100
                                long = long + 100
                            if 20 <= randVal < 100:
                                lat = lat + 100
                                long = long + 100
                            position = {"Lat": lat, "Long": long}
                            sensor["ActualPosition"] = position
            time.sleep(self.interval)

    def setMovementSensor(self):
        while True:
            for person in self.person:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        caduta = randint(0, 100)
                        if 0 <= caduta < 1:
                            value = "True"
                        else:
                            value = "False"

                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": value,
                                "Position": getActualPosition(person)
                                }
                        self.connectors[person["CodiceFiscale"]].sendData(data, self.name)
                        self.connectors[person["CodiceFiscale"]].loop()
            time.sleep(self.interval)

    def setBloodPressureSensor(self):
        while True:
            for person in self.person:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        value = randint(40, 170)
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": value,
                                "Position": getActualPosition(person)}
                        self.connectors[person["CodiceFiscale"]].sendData(data, self.name)
                        self.connectors[person["CodiceFiscale"]].loop()
            time.sleep(self.interval)

    def setBloodOxygenSensor(self):
        while True:
            for person in self.person:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        value = randint(45, 140)
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": value,
                                "Position": getActualPosition(person)}
                        self.connectors[person["CodiceFiscale"]].sendData(data, self.name)
                        self.connectors[person["CodiceFiscale"]].loop()
            time.sleep(self.interval)

    def setHearthBeatSensor(self):
        while True:
            for person in self.person:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": randint(30, 120),
                                "Position": getActualPosition(person)}
                        self.connectors[person["CodiceFiscale"]].sendData(data, self.name)
                        self.connectors[person["CodiceFiscale"]].loop()
            time.sleep(self.interval)

    def setSensor(self):
        if self.name == "heartbeat":
            self.setHearthBeatSensor()
        if self.name == "bloodPressure":
            self.setBloodPressureSensor()
        if self.name == "bloodOxygen":
            self.setBloodOxygenSensor()
        if self.name == "position":
            self.setPosition()
        if self.name == "movement":
            self.setMovementSensor()

    def run(self):
        self.setSensor()
