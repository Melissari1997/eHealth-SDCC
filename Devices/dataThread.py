import json
import random
import time
from random import randint
from threading import Thread

"""
Thread che genera i dati di ogni sensori di una lista di persone
"""

def getPersonList(filename):
    with open(filename) as configFile:
        data = json.load(configFile)
        configFile.close()
        return data



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


"""
Setta la nuova zona di appartenenza (quindi cambia il fog node di appartenenza)
"""


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


# probabilità di cambiare zona
def getProbability():
    with open("settings/dataCreatorConfig.json") as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


"""
Calcola il nodo fog più vicino
"""


def getNearestFog(lat, long, ignorePort=None):
    candidateFog = fogList.copy()
    if ignorePort is not None:
        for i in range(0, len(candidateFog)):
            print("Candidate Fog ", i, " : ", candidateFog[i] )
            print("Port: ", candidateFog[i]["port"])
            if candidateFog[i]["port"] == ignorePort:
                candidateFog.pop(i)
                print("popped ", i)
                break
    return computeDistance(lat, long, candidateFog)


"""
ritorna il nodo fog più vicino alle coordinate inviate 
"""


def computeDistance(lat, long, candidateFog):
    minSum = 100000000
    chosenFog = None
    for fog in candidateFog:
        latDiff = lat - fog["Latitude"]
        longDiff = long - fog["Longitude"]
        sum = abs(latDiff) + abs(longDiff)
        if sum < minSum:
            minSum = sum
            chosenFog = fog
    return chosenFog


fogList = getFogList()


class SensorThread(Thread):
    name = ""
    interval = 0
    person = []
    connectorsList = {}

    def __init__(self, sensor, mqttConnectorsList, personList):
        super().__init__()
        self.persons = personList
        self.name = sensor["name"]
        self.interval = sensor["interval"]
        self.connectorsList = mqttConnectorsList
        probabilities = getProbability()
        self.changeZoneProb = probabilities["ChangeZoneProbability"]

    def setPersons(self, persons):
        self.persons = persons

    def changeBroker(self, broker, person):
        self.connectorsList[person["CodiceFiscale"]].disconnect()
        port = broker['port']
        # self.connectorsList[person["CodiceFiscale"]].setPort(port)
        try:
            self.connectorsList[person["CodiceFiscale"]].connect("localhost", port)
        except:
            print("Changed not possibile. Fog node: ", broker, " is not available")

    #cambia (di poco) le coordinate del paziente
    def setPosition(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        changeZone = randint(0, 100)
                        if 0 < changeZone < self.changeZoneProb:
                            brokerId = self.connectorsList[person["CodiceFiscale"]].getActualBroker()
                            person["ActualZone"] = brokerId
                            newPos = setNewPosition(person)
                            newCoordinates = newPos[1]
                            broker = newPos[0]
                            person["ActualZone"] = broker["FogId"]
                            self.changeBroker(broker, person)
                            sensor["ActualPosition"] = newCoordinates
                            print("Changed fog node :", person["CodiceFiscale"], "New fog node: ", person["ActualZone"])

                        move = randint(0, 100)
                        if 0 <= move < 100:
                            lat = sensor["ActualPosition"]["Lat"]
                            long = sensor["ActualPosition"]["Long"]
                            randVal = randint(0, 100)
                            if 0 <= randVal < 1:
                                lat = lat + 1000
                                long = long + 1000
                            if 1 <= randVal < 20:
                                lat = lat + 100
                                long = long + 100
                            position = {"Lat": lat, "Long": long}
                            brokerId = self.connectorsList[person["CodiceFiscale"]].getActualBroker()
                            person["ActualZone"] = brokerId
                            nearestFog = getNearestFog(lat, long)
                            if nearestFog["FogId"] != person["ActualZone"]:
                                self.changeBroker(nearestFog, person)
                            sensor["ActualPosition"] = position
            time.sleep(self.interval)

    # genera una caduata del paziente
    def setMovementSensor(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        caduta = randint(0, 100)
                        if caduta == 0:
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
                        self.connectorsList[person["CodiceFiscale"]].sendData(data, self.name)
            time.sleep(self.interval)

    #genera i dati del sensore di pressione sanguigna
    def setBloodPressureSensor(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        value = randint(50, 170)
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": value,
                                "Position": getActualPosition(person)}

                        self.connectorsList[person["CodiceFiscale"]].sendData(data, self.name)
            time.sleep(self.interval)

    #genera i dati del sensore di ossigenazione sanguigna
    def setBloodOxygenSensor(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        value = randint(45, 140)
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": value,
                                "Position": getActualPosition(person)}
                        self.connectorsList[person["CodiceFiscale"]].sendData(data, self.name)
            time.sleep(self.interval)

    #genera i dati del battito cardiaco
    def setHearthBeatSensor(self):
        while True:
            for person in self.persons:
                for sensor in person["Sensors"]:
                    if sensor["SensorType"] == self.name:
                        data = {"Name": person["Name"],
                                "Surname": person["Surname"],
                                "CF": person["CodiceFiscale"],
                                "SensorType": self.name,
                                "Value": randint(50, 115),
                                "Position": getActualPosition(person)}
                        self.connectorsList[person["CodiceFiscale"]].sendData(data, self.name)
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
