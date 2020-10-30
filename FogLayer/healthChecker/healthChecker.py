import json
import time
import requests
from flask import Flask, request

healthChecker = Flask(__name__)

"""
Servizio che analizza i dati ricevuti e se necessario, invia email o chiede al cloud di inviare un'ambulanza
"""


def readSensorValues():
    with open('sensorValues.json') as configFile:
        data = json.load(configFile)
        configFile.close()
        return data


sensorFile = readSensorValues()


# inserisce sul db il dato appena ottenuto (se il dato non è normale)
def writeOnDb(message):
    res = requests.post("http://dbconnector:7000/sendPendingPatient", json=message)
    numberHigh = json.loads(res.content)["numberHigh"]
    numberMedium = json.loads(res.content)["numberMedium"]
    return (numberHigh, numberMedium)


# invia l'email se non ne ho già inviata una negli ultimi 15 minuti
def sendEmail(message, priority="medium"):
    notified = requests.get("http://dbconnector:7000/getNotified", json=message)
    jsonData = json.loads(notified.content)

    if jsonData["Presence"] == True:
        requests.get("http://dbconnector:7000/updatePermissions", json=message)
    else:
        requests.get("http://dbconnector:7000/addToNotified", json=message)
    res = requests.get("http://dbconnector:7000/getPermissions", json=message)
    permissions = json.loads(res.content)
    updateData = {
        "CF": message["CF"],
        "priority": priority,
        "sensorType": message["Sensor"]
    }

    if permissions["mediumEmail"] is False and priority == "medium":
        requests.post("http://mailsender:4000/sendEmail", json=message)
        requests.post("http://dbconnector:7000/updateProcessed", json=updateData)
    if permissions["highEmail"] is False and priority == "high":
        requests.post("http://mailsender:4000/sendEmail", json=message)
        requests.post("http://dbconnector:7000/updateProcessed", json=updateData)
        sendToCloud(message)


# chiede al cloud di inviare un'ambulanza
def sendToCloud(message):
    requests.post("http://cloudconnector:6000/sendData", json=message)


def receive(jsonData):
    # se il sensore è di movimento, invia email
    if "movement" == jsonData["SensorType"]:
        if jsonData["Value"] == "True":
            emailRequest = [{"CF": jsonData["CF"]}]
            emailRes = requests.get("http://cloud-service.us-east-1.elasticbeanstalk.com/getemail", json=emailRequest)
            email = json.loads(emailRes.content)["Email"]
            message = {"ReceiverEmail": email,
                       "Name": jsonData["Name"],
                       "Surname": jsonData["Surname"],
                       "CF": jsonData["CF"],
                       "Sensor": jsonData["SensorType"],
                       "Value": "True",
                       "Position": jsonData["Position"]
                       }
            sendEmail(message)
    for sensor in sensorFile:
        if sensor["name"] == jsonData["SensorType"]:
            # se il sensore ha valori fuori dal normale, ma non totalmente anomali, invia email se ne ho ricevuti almeno 4 negli ultimi 2 minuti
            if sensor["minWarningValue"] <= jsonData["Value"] < sensor["minNormalValue"] or \
                    sensor["maxNormalValue"] < jsonData["Value"] <= sensor["maxWarningValue"]:

                emailRequest = [{"CF": jsonData["CF"]}]
                emailRes = requests.get("http://cloud-service.us-east-1.elasticbeanstalk.com/getemail",
                                        json=emailRequest)
                email = json.loads(emailRes.content)["Email"]
                message = {"ReceiverEmail": email,
                           "Name": jsonData["Name"],
                           "Surname": jsonData["Surname"],
                           "CF": jsonData["CF"],
                           "Sensor": jsonData["SensorType"],
                           "Value": jsonData["Value"],
                           "Gravity": "medium",
                           "Position": jsonData["Position"]
                           }
                res = writeOnDb(message)
                if res[1] > 3:
                    sendEmail(message)
            # se il sensori ha valori completamente anomali, invia email + ambulanza se ne ho ricevuti almeno 4 negli ultimi 2 minuti
            if sensor["maxWarningValue"] < jsonData["Value"] or \
                    jsonData["Value"] < sensor["minWarningValue"]:
                emailRequest = [{"CF": jsonData["CF"]}]
                emailRes = requests.get("http://cloud-service.us-east-1.elasticbeanstalk.com/getemail",
                                        json=emailRequest)
                email = json.loads(emailRes.content)["Email"]
                message = {"ReceiverEmail": email,
                           "Name": jsonData["Name"],
                           "Surname": jsonData["Surname"],
                           "CF": jsonData["CF"],
                           "Sensor": jsonData["SensorType"],
                           "Value": jsonData["Value"],
                           "Gravity": "high",
                           "Position": jsonData["Position"]
                           }
                res = writeOnDb(message)
                if res[0] > 3:
                    sendEmail(message, priority="high")


@healthChecker.route("/sendData", methods=['POST'])
def receiveData():
    now = time.time()
    data = request.json
    receive(data)
    later = time.time()
    difference = later - now
    return {"difference": difference * 1000}


if __name__ == "__main__":
    healthChecker.run(host='0.0.0.0', port=5000)
