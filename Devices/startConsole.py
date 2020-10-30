import json
import Devices.deviceCreator as deviceCreator

file = 'settings/medium.json'


def handlesimtype():
    global file
    print()
    print()
    print("What simulation do you want?")
    print("1) Small number of people")
    print("2) Medium number of people")
    print("3) High number of people")
    print("4) Huge dataset")
    simType = ''
    while simType.lower() not in {"1", "2", "3"}:
        simType = input("Please enter 1, 2 or 3: ")
    if simType == "1":
        print("SELECTED SIMULATION TYPE: Small number of people")
        file = "settings/small.json"
    if simType == "2":
        print("SELECTED SIMULATION TYPE: Medium number of people")
        file = "settings/medium.json"
    if simType == "3":
        print("SELECTED SIMULATION TYPE: High number of people")
        file = "settings/big.json"

    askAction()


def askAction():
    print("What do you need?")
    print("1) Select simulation type (default: medium number of people)")
    print("2) Start simulation")
    print(file)
    response = ''
    while response.lower() not in {"1", "2", "3"}:
        response = input("Please enter 1, 2 or 3: ")

    if response.lower() == "1":
        handlesimtype()

    if response.lower() == "2":
        deviceCreator.startSim(file)


if __name__ == "__main__":
    askAction()
