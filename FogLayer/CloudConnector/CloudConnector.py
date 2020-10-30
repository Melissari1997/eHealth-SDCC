import json

import requests
from flask import Flask, request

CloudConnector = Flask(__name__)


def process(message):
    requests.post("http://dbconnector:7000/Processed", json=message)

def sendToCloud(message):
    message.pop("ReceiverEmail", None)
    message.pop("Sensor", None)
    message.pop("Gravity", None)
    message.pop("Value", None)
    message.pop("SensorType", None)
    latPos = str(message["Position"]["Lat"])
    latPosFirstPart = latPos[:2]
    latPosSecondPart = latPos[2:]
    latPos = latPosFirstPart + "." + latPosSecondPart
    latPos = float(latPos)
    message["Position"]["Lat"] = latPos

    longPos = str(message["Position"]["Long"])
    longPosFirstPart = longPos[:2]
    longPosSecondPart = longPos[3:]
    longPos = longPosFirstPart + "." + longPosSecondPart
    longPos = float(longPos)
    message["Position"]["Long"] = longPos
    data = [message]
    res = requests.post("http://cloud-service.us-east-1.elasticbeanstalk.com/data", json=data)

@CloudConnector.route("/sendProcessed", methods=["POST"])
def sendProcessed():
    data = request.json
    process(data)

@CloudConnector.route("/sendData", methods=["POST"])
def sendMessage():
    data = request.json
    sendToCloud(data)
    return data


if __name__ == "__main__":
    CloudConnector.run(host='0.0.0.0', port=6000)
