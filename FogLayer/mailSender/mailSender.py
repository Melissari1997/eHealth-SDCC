from flask import Flask, request
import yagmail

mailSender = Flask(__name__)
"""
Invia l'email
"""

def sendEmail(infoMessage):
    # infoMessage = json.loads(data)

    receiver = infoMessage["ReceiverEmail"]

    body = \
        "Hello from ehealth\n" \
        "This email is for patient: " + infoMessage["Name"] + " " + infoMessage["Surname"] + " ( " + infoMessage[
            "CF"] + ") \n" + \
        "We observed an abnormal value for sensor: " + infoMessage["Sensor"] + "\n" + \
        "The patient is in position:\n Lat: " + str(infoMessage["Position"]["Lat"]) + ";\n Long: " + str(
            infoMessage["Position"]["Long"]) + "\n"
    if "Gravity" in infoMessage:
        if infoMessage["Gravity"] == "high":
            body += "We have called an ambulance"

    yag = yagmail.SMTP(user='service.ehealth@gmail.com', password="melissaritummolo", host="smtp.gmail.com")
    yag.send(to=receiver, subject="Notification", contents=body
             )


@mailSender.route("/sendEmail", methods=["POST"])
def send():
    data = request.json
    sendEmail(data)
    return data


if __name__ == "__main__":
    # sendEmail()
    mailSender.run(host='0.0.0.0', port=4000)
