import pytz
from datetime import datetime
import boto3
from flask import Flask, render_template, request
from Cloud import FoundHospital, ConnectionDB
import time
import threading

""" Questo codice implementa il Cloud , esponendo una pagina web per poter tener traccia dei pazienti
"""
tz = pytz.timezone('Europe/Rome')
initialTime = time.time()
application = Flask(__name__)
sem = threading.Semaphore(1)
aws_access_key_id = open("key.txt", "r").read()
aws_secret_access_key = open("secretkey.txt", "r").read()
client = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name='us-east-1')
hospital_table = client.Table('ospedali')
arrival_patient_table = client.Table('pazienti')
exit_patient_table = client.Table('pazientiuscita')
time_table = client.Table('tempi')
email_table = client.Table('email')
index = 0



def remove_element(patient):
    """
    :param patient: paziente presente nella tabella
    :return: null, permette di eliminare i pazienti che sono già arrivati
     in ospedale, liberando cosi le relative ambulanze
    """
    rome_now = datetime.now(tz)
    current_time = datetime.strftime(rome_now, "%H:%M:%S")
    timearrive = patient['TimeArrive']
    hour = timearrive[:2]
    minute = timearrive[3:5]
    seconds = timearrive[6:]
    hour1 = current_time[:2]
    minute1 = current_time[3:5]
    seconds1 = current_time[6:]
    if int(hour) == int(hour1):
        if int(minute) == int(minute1):
            if int(seconds) < int(seconds1):
                ConnectionDB.delete_patient(exit_patient_table, patient['Id'])
                ConnectionDB.update_item(hospital_table, patient['Hospital'], 1)
        elif int(minute) < int(minute1):
            ConnectionDB.delete_patient(exit_patient_table, patient['Id'])
            ConnectionDB.update_item(hospital_table, patient['Hospital'], 1)
    elif int(hour) < int(hour1):
        ConnectionDB.delete_patient(exit_patient_table, patient['Id'])
        ConnectionDB.update_item(hospital_table, patient['Hospital'], 1)
    return

@application.route('/getemail')
def getemail():
    """
    funzione che permette al fog per poter individuare le mail dei relativi pazienti
    :return: Email del paziente
    """
    cf = request.json
    print(cf)
    codeFisc = cf[0]['CF']
    pazienti_a = ConnectionDB.read_items(email_table)
    for paza in pazienti_a:
        if codeFisc == paza['CF']:
            return {"Email": paza['Email']}
    return {"Email": "NotFound"}


@application.route('/stat')
def statistics():
    """
    Permette di tener traccia dei tempi medi di risposta del Cloud
    :return: null
    """
    tempi_elaborazione = ConnectionDB.read_items(time_table)
    tempo = 0.0
    for elab_time in tempi_elaborazione:
        tempo = tempo + float(elab_time['Time'])
    if index == 0 or len(tempi_elaborazione) == 0:
        return "non è stato elaborato ancora nessun paziente"
    else:
        tempo = tempo / len(tempi_elaborazione)
        return "Il tempo medio di risposta è " + str(tempo) + " con un numero medio di pazienti al secondo pari a: " + \
               str(index / (time.time() - initialTime))


def control_patient(paz):
    """
    Funzione necessaria per individuare se un paziente è stato già servito nel breve periodo
    :param paz: Paziente
    :return: 1 o 0 per individuare la corrispondenza o no
    """
    pazienti_a = ConnectionDB.read_items(arrival_patient_table)
    pazienti_u = ConnectionDB.read_items(exit_patient_table)
    for paza in pazienti_a:
        if(paz['CF'] == paza['CF']):
            return 1
    for pazu in pazienti_u:
        if(paz['CF'] == pazu['CF']):
            return 1
    return 0


@application.route('/data', methods=['POST'])
def get_HTTPRequest():
    """
    Funzione che permette al Cloud di ricevere dati dei pazienti che hanno bisogno di soccorso
    :return: null
    """
    global index
    patient = request.json
    time1 = time.time()
    if patient is not None:
        paz = patient.__getitem__(0)
        if control_patient(paz) == 1:
            print("paziente già in servizio")
        else:
            print("inserisco paziente")
            print(ConnectionDB.put_patient(arrival_patient_table, paz['Name'], paz['Surname'], str(paz['Position']['Lat']),
                                           str(paz['Position']['Long']), paz['CF'], index))
            index += 1
            FoundHospital.startapp(hospital_table, arrival_patient_table, exit_patient_table, sem, time1, time_table)
    return "Request Send"


@application.route("/")
def hello():
    """
    Pagina web
    :return: Pagina web
    """
    controlloElem()
    rome_now = datetime.now(tz)
    day = datetime.strftime(rome_now, "%d/%m/%Y")
    ora = datetime.strftime(rome_now, "%H:%M:%S")
    hospital = ConnectionDB.read_items(hospital_table)
    patients = ConnectionDB.read_items(exit_patient_table)
    return render_template('page1.html', hospital=hospital, patient=patients, giorno=day, ora=ora)


def controlloElem():
    """
    Funzione per controllare se un ambulanza può essere liberata
    :return:
    """
    patients = ConnectionDB.read_items(exit_patient_table)
    if len(patients) >= 1:
        for patient in patients:
            remove_element(patient)


if __name__ == "__main__":
    application.run(port=5000, debug=True)
