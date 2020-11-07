import json
from random import randint

from codicefiscale import codicefiscale
from Devices.dataThread import SensorThread
from Devices.mqttClient import MqttClient

mqttConnectorsDict = {}


def getSensorInterval(sensorsList, sensorType):
    for sensor in sensorsList:
        if sensor["name"] == sensorType:
            return sensor["interval"]


def getFogList():
    with open("settings/fogDiscovery.json") as configFile:
        data = json.load(configFile)
        configFile.close()
        fogList = []
        for fogNode in data:
            fogList.append(fogNode)
        return fogList


def getPersonList(filename):
    with open(filename) as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


def getSensorList():
    with open('settings/sensorTypes.json') as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


def computeFiscalCode():
    with open('settings/attributes.json') as configFile:
        personList = json.load(configFile)
    for person in personList:
        if "CodiceFiscale" not in person:
            cf = codicefiscale.encode(name=person["Name"], surname=person["Surname"], birthdate=person["BirthDate"],
                                      birthplace=person["BirthPlace"], sex=person["Sex"])
            person["CodiceFiscale"] = cf
    with open('settings/attributes.json', "w") as configFile:
        json.dump(personList, configFile)
        configFile.close()


def startSim(filename):
    print()
    print()
    print()
    print("SIMULATION STARTED")
    sensors = getSensorList()
    fogList = getFogList()
    # computeFiscalCode()
    personList = getPersonList(filename)
    for person in personList:
        connector = MqttClient(person["CodiceFiscale"])
        fogNode = fogList[person["ActualZone"]]
        connector.connect("localhost", fogNode["port"], fogNode["FogId"])
        mqttConnectorsDict[person["CodiceFiscale"]] = connector
    thread = False
    #preferibile la modalità senza thread, altrimenti potrebbe bloccarsi la macchina virtuale
    if not thread:
        for sensor in sensors:
            thread = SensorThread(sensor, mqttConnectorsDict, personList)
            thread.start()
    if thread:
        i = 0
        persons = []
        for person in personList:
            i += 1
            persons.append(person)
            if i == 5:
                print(persons)
                for p in persons:
                    for sensor in p["Sensors"]:
                        interval = getSensorInterval(sensors, sensor["SensorType"])
                        if interval is not None:
                            s = {
                                "name": sensor["SensorType"],
                                "interval": getSensorInterval(sensors, sensor["SensorType"])
                            }
                            thread = SensorThread(s, mqttConnectorsDict, persons)
                            thread.start()
                persons = []
                i = 0

