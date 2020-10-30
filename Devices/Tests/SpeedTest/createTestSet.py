from codicefiscale import codicefiscale
from random import randint
import json


def getSensorList():
    with open('../../settings/sensorTypes.json') as configFile:
        data = json.load(configFile)
        for sensor in data:
            sensor.pop("interval", None)
            sensor["SensorType"] = sensor.pop("name", None)
        configFile.close()
        return data


NameList = [("Alessio", "M"), ("Andrea", "M"), ("Giuseppe", "M"), ("Maria", "F"), ("Roberto", "M"), ("Luca", "M"),
            ("Giovanni", "M"),
            ("Paolo", "M"), ("Anna", "F"), ('Valeria', "F"), ("Zoe", "F"), ("Mario", "M"), ("Monica", "F"),
            ("Davide", "M"), ("Gabriele", "M"),
            ("Mirko", "M"), ("Alessandro", "M"), ("Francesco", "M"), ("Giulia", "F"), ("Ilaria", "F"),
            ("Valentina", "F"), ("Sara", "F"),
            ("Leonardo", "M"), ("Daniele", "M"), ("Claudio", "M"), ("Salvatore", "M"), ("Elisabetta", "F"),
            ("Sonia", "F"), ("Veronica", "F"),
            ("Mattia", "M"), ("Enrico", "M"), ("Tommaso", "M"), ("Beatrice", "F"), ("Camilla", "F")]
SurnameList = ["Rossi", "Bianchi", "Verdi", "Tummolo", "Melissari", "Amici", "Russo", "Mancini", "Totti",
               "De Rossi", "Moretti", "Fontana", "De Angelis", "Palumbo", "Gatti", "Caputo", "Belotti"]

BirthPlace = ["Roma", "Milano", "Napoli", "Bologna", "Parma", "Firenze"]

BirthDayList = ["04/04/1997", "01/01/2000", "25/12/2010", "09/05/1992"]
SensorList = getSensorList()


def getFogList():
    with open("../../settings/fogDiscovery.json") as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


def selectSensors(actualZone):
    sensors = []
    for sensor in SensorList:
        if sensor["SensorType"] != "position":
                sensors.append(sensor)
    if {"SensorType": "position"} not in sensors:
        sensors.append({
            "SensorType": "position",
            "ActualPosition": setActualPosition(actualZone)
        })
    return sensors


def setActualPosition(actualZone):
    # zoneSelector = randint(0, len(fogList) - 1)
    Lat = fogList[actualZone]["Latitude"]
    Long = fogList[actualZone]["Longitude"]
    latPos = str(Lat)
    latPosFirstPart = latPos[:2]
    latPosSecondPart = latPos[3:]
    latPos = latPosFirstPart + latPosSecondPart
    latPos = int(latPos)

    longPos = str(Long)
    longPosFirstPart = longPos[:2]
    longPosSecondPart = longPos[3:]
    longPos = longPosFirstPart + longPosSecondPart
    longPos = int(longPos)

    return {
        "Lat": Lat,
        "Long": Long
    }


def getPeople():
    cfList = []
    people = []
    i = 0
    for name in NameList:
        for surname in SurnameList:
            for city in BirthPlace:
                for birthDay in BirthDayList:
                    sensors = selectSensors(0)
                    cf = codicefiscale.encode(name=name[0], surname=surname, birthdate=birthDay,
                                              birthplace=city, sex=name[1])
                    if cf not in cfList:
                        cfList.append(cf)
                        addperson = {
                            "Id": i,
                            "Name": name[0],
                            "Surname": surname,
                            "BirthPlace": city,
                            "Sex": name[1],
                            "BirthDate": birthDay,
                            "CodiceFiscale": cf,
                            "Sensors": sensors,
                            "ActualZone": 0
                        }
                        i += 1
                        people.append(addperson)
    personList = []
    for person in people:
        personList.append(person["CodiceFiscale"])
    personSet = set(personList)
    # controllo se per sbaglio ci sono CF uguali
    return people


def createSmallDataset():
    print("Creating small dataset...")
    with open("small.json", "w") as smallDataset:
        smallList = []
        for i in range(0, 10):
            smallList.append(people[i])
        json.dump(smallList, smallDataset)
    print("Created small dataset. Size: ", len(smallList))
    print()


def createMediumDataset():
    print("Creating medium dataset...")
    with open("medium.json", "w") as mediumDataset:
        mediumList = []
        for i in range(0, 100):
            mediumList.append(people[i])
        json.dump(mediumList, mediumDataset)
    print("Created medium dataset. Size: ", len(mediumList))
    print()


def createHighDataset():
    print("Creating big dataset...")
    with open("big.json", "w") as bigDataset:
        bigList = []
        for i in range(0, 1000):
            bigList.append(people[i])
        json.dump(bigList, bigDataset)
    print("Created bug dataset. Size: ", len(bigList))
    print()



people = []
fogList = []
if __name__ == "__main__":
    fogList = getFogList()
    people = getPeople()
    createSmallDataset()
    createMediumDataset()
    createHighDataset()
