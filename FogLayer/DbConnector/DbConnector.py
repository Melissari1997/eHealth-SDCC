import time

from flask import Flask, request
from flask_api import status
import mysql.connector
import requests

time.sleep(5)
DbConnector = Flask(__name__)
config = {
    "host": "mysql",
    "user": "root",
    "passwd": "password",
    'port': '3306',
    'database': 'patient'
}
while True:
    try:
        connection = mysql.connector.connect(**config)
        break
    except:
        print("Retry...")
        time.sleep(5)
        continue


def getAllPending():
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM pending WHERE sendDate > NOW() - INTERVAL 2 MINUTE")
    res = cursor.fetchall()
    cursor.close()
    return res


def getAllNotified():
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM notified WHERE sendDate > NOW() - INTERVAL 45 MINUTE")
    res = cursor.fetchall()
    cursor.close()
    return res


@DbConnector.route("/getPending", methods=["GET"])
def getPending():
    list = getAllPending()
    print("Pending: ", list)
    return "ok"

"""
@app.route("/getNotified", methods=["GET"])
def getNotified():
    list = getAllNotified()
    print("Notified ", list)
    return "ok"
"""


# aggiorna la tabella contenente i pazienti già notificati, prima di processarne uno nuovo.
def setProcessed():
    processedPatient = request.json
    CF = processedPatient['CF']
    priority = processedPatient["priority"]
    sensorType = processedPatient["sensorType"]
    cursor = connection.cursor(buffered=True)
    if priority == "high":
        updateHighQuery = "UPDATE  notified " \
                          "SET  highEmail = IF( sendDate > (NOW() - INTERVAL 45 MINUTE), 1, highEmail), " \
                          "cloud = IF( sendDate > (NOW() - INTERVAL 45 MINUTE), 1, cloud) " \
                          "WHERE CF = %s and sensorType = %s"
        cursor.execute(updateHighQuery, (CF, sensorType))
    if priority == "medium" or priority == "high":
        updateMediumQuery = "UPDATE  notified " \
                            "SET mediumEmail = TRUE WHERE CF = %s and sensorType = %s"
        cursor.execute(updateMediumQuery, (CF, sensorType))
    cursor.close()
    return 'updated'

#aggiorna la tabella dei pazienti già notificati.
@DbConnector.route("/updatePermissions", methods=["GET"])
def updatePermissions():
    processedPatient = request.json
    CF = processedPatient['CF']
    SensorType = processedPatient["Sensor"]
    cursor = connection.cursor(buffered=True)
    # aggiorna i dati nel caso in cui sono passati almeno 15 minuti dall'ultima notifica
    updateMediumQuery = "UPDATE notified " \
                        "SET mediumEmail = CASE " \
                        "WHEN sendDate > (NOW() -  INTERVAL 15 MINUTE) THEN 1 " \
                        "ELSE 0 " \
                        "END " \
                        "WHERE CF = %s and sensorType = %s"
    cursor.execute(updateMediumQuery, (CF, SensorType))

    # aggiorna i dati nel caso in cui sono passati almeno 45 minuti dall'ultima ambulanza chiamata
    updateHighQuery = "UPDATE notified " \
                      "SET highEmail = CASE " \
                      "WHEN sendDate > (NOW() -  INTERVAL 45 MINUTE) THEN 1 " \
                      "ELSE 0 " \
                      "END " \
                      "WHERE CF = %s"
    cursor.execute(updateHighQuery, (CF,))

    updateCloudQuery = "UPDATE notified " \
                       "SET cloud = CASE " \
                       "WHEN sendDate > (NOW() -  INTERVAL 45 MINUTE) THEN 1 " \
                       "ELSE 0 " \
                       "END " \
                       "WHERE CF = %s"
    cursor.execute(updateCloudQuery, (CF,))
    cursor.close()
    return "updated"

#ritorna se posso mandare un'email o inviare un'ambulanza per quel paziente
@DbConnector.route("/getPermissions", methods=["GET"])
def getPermissions():
    processedPatient = request.json
    CF = processedPatient['CF']
    SensorType = processedPatient["Sensor"]
    cursor = connection.cursor(buffered=True)
    # ritora se posso mandare email o mandare al cloud
    searchQuery = "SELECT * FROM notified WHERE CF = %s AND sensorType = %s"
    cursor.execute(searchQuery, (CF, SensorType))
    res = cursor.fetchall()
    mediumEmail = False
    highEmail = False
    cloudSend = False
    if res[0][4] == 1:
        mediumEmail = True
    if res[0][5] == 1:
        highEmail = True
    if res[0][6] == 1:
        cloudSend = True
    cursor.close()
    return {"mediumEmail": mediumEmail, "highEmail": highEmail, "cloudSend": cloudSend}


@DbConnector.route("/getNotified", methods=[
    'GET'])  # meglio chiamarla add to processed e mettere come valore di ritorno se la riga era presente o no
def getProcessed():
    processedPatient = request.json
    CF = processedPatient['CF']
    SensorType = processedPatient["Sensor"]
    cursor = connection.cursor(buffered=True)
    searchQuery = "SELECT * FROM notified WHERE CF = %s AND sensorType = %s"
    cursor.execute(searchQuery, (CF, SensorType))
    res = cursor.fetchall()
    if res:
        result = {
            "Presence": True
        }
    else:
        result = {
            "Presence": False
        }
    cursor.close()
    return result

#aggiunge il paziente alla lista di quelli notificati per email
@DbConnector.route("/addToNotified", methods=["GET"])
def addToProcessed():
    processedPatient = request.json
    CF = processedPatient['CF']
    Name = processedPatient["Name"]
    Surname = processedPatient["Surname"]
    SensorType = processedPatient["Sensor"]
    cursor = connection.cursor(buffered=True)
    insertQuery = "INSERT INTO notified (CF,patientName, patientSurname, sensorType, mediumEmail, highEmail, cloud, sendDate) " \
                  "VALUES (%s, %s, %s, %s, FALSE,FALSE,FALSE,NOW())"
    cursor.execute(insertQuery, (CF, Name, Surname, SensorType))
    cursor.close()
    return "inserted"


@DbConnector.route("/sendPendingPatient", methods=['POST'])
def sendPending():
    pendingPatient = request.json
    CF = pendingPatient['CF']
    Name = pendingPatient["Name"]
    Surname = pendingPatient["Surname"]
    SensorType = pendingPatient["Sensor"]
    Gravity = pendingPatient["Gravity"]
    cursor = connection.cursor(buffered=True)


    #inserire solo se non c'è già (gestione doppioni)

    try:
        insertQuery = "INSERT INTO pending (CF,patientName, patientSurname,sensorType, gravity, sendDate)" \
                      " VALUES (%s,%s,%s,%s,%s,NOW())"
        cursor.execute(insertQuery, (CF, Name, Surname, SensorType, Gravity))
    except:
        pass
    readQuery = "SELECT CF, COUNT(*) FROM pending WHERE CF = %s AND Gravity = %s AND sendDate > NOW() - INTERVAL 2 MINUTE"
    cursor.execute(readQuery, (CF, "high"))
    highGravity = cursor.fetchall()
    readQuery = "SELECT CF, COUNT(*) FROM pending WHERE CF = %s AND (Gravity = %s OR Gravity = %s) AND sendDate > NOW() - INTERVAL 2 MINUTE"
    cursor.execute(readQuery, (CF, "medium", "high"))
    mediumGravity = cursor.fetchall()

    cursor.close()
    return {"numberHigh": highGravity[0][1], "numberMedium": mediumGravity[0][1]}


if __name__ == "__main__":
    DbConnector.run(port=7000, host="0.0.0.0")
