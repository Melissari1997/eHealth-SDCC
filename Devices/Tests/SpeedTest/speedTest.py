import ast
import json
import time
from codicefiscale import codicefiscale
from Devices.dataThread import SensorThread
from Devices.mqttClient import MqttClient

mqttConnectorsDict = {}
chosenResultsFile = None


def on_message(mqttClient, userdata, message):
    message = (message.payload.decode("utf-8"))
    #print("message received from sensor", json.loads(repr(ast.literal_eval(strmessage))))

    chosenResultsFile.write(message)
    chosenResultsFile.write("\n")
    chosenResultsFile.flush()



def getSensorInterval(sensorsList, sensorType):
    for sensor in sensorsList:
        if sensor["name"] == sensorType:
            return sensor["interval"]


def getFogList():
    with open("../../settings/fogDiscovery.json") as configFile:
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
    with open('../../settings/sensorTypes.json') as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


def computeFiscalCode():
    with open('../../settings/attributes.json') as configFile:
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
        # connector._port = fogNode["port"]
        connector.connect("localhost", fogNode["port"])
        connector.client.subscribe("/speedTest")
        connector.client.on_message = on_message
        mqttConnectorsDict[person["CodiceFiscale"]] = connector
    for sensor in sensors:
        thread = SensorThread(sensor, mqttConnectorsDict, personList)
        thread.daemon = True
        thread.start()
    while True:
        time.sleep(180)
        chosenResultsFile.close()
        break
    print("Exit")
    exit(0)

"""
    i = 0
    if filename.__contains__("huge"):
        threadPool = 100
    else:
        threadPool = 5
    persons = []
    threadList = []
    for person in personList:
        i += 1
        persons.append(person)
        if i == threadPool:
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
                        thread.daemon = True
                        thread.start()
                        threadList.append(thread)
            persons = []
            i = 0
    now = time.time()
    while True:
        time.sleep(180)
        late = time.time()
        difference = late - now
        if difference > 180:
            smallResults.close()
            exit(0)

"""
"""
if __name__ == "__main__":
    startSim("settings/attributes.json")
"""

if __name__ == "__main__":
    print()
    print()
    print("What simulation do you want?")
    print("1) Small number of people")
    print("2) Medium number of people")
    print("3) High number of people")
    simType = ''
    while simType.lower() not in {"1", "2", "3"}:
        simType = input("Please enter 1, 2 or 3: ")
    if simType == "1":
        print("SELECTED SIMULATION TYPE: Small number of people")
        chosenResultsFile =  open("results/smallResults", "w")
        file = "small.json"
    if simType == "2":
        print("SELECTED SIMULATION TYPE: Medium number of people")
        chosenResultsFile = open("results/mediumResults", "w")
        file = "medium.json"
    if simType == "3":
        print("SELECTED SIMULATION TYPE: High number of people")
        chosenResultsFile = open("results/highResults", "w")
        file = "big.json"
    startSim(file)
