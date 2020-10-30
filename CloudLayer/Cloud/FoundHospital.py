import threading
from geopy.distance import geodesic
from threading import Thread
from datetime import datetime
import pytz
from Cloud import ConnectionDB
import time
""" Questo insieme di metodi implementa la logica effettiva del Cloud
"""
vel_ambVP = 0.01388  # Km/s corrispondente a 50 km/h
vel_ambVO = 0.01388  # Km/s corrispondente a 50 km/h
tz = pytz.timezone('Europe/Rome')


def calculate_arrive_time(tempo):
    """
    Funzione che permette di calcolare il tempo di arrivo all'ospedale del Paziente
    :param tempo: tempo arrivo della richiesta
    :return: tempo di arrivo stimato
    """
    rome_now = datetime.now(tz)
    minute = datetime.strftime(rome_now, "%M")
    hours = datetime.strftime(rome_now, "%H")
    h = (int(hours) + int((int(minute) + tempo) / 60)) % 24
    m = (int(minute) + tempo) % 60

    if m > 9:
        if h > 9:
            return str(h) + ":" + str(m) + ":" + datetime.strftime(rome_now, "%S")
        else:
            return "0" + str(h) + ":" + str(m) + ":" + datetime.strftime(rome_now, "%S")
    else:
        if h > 9:
            return str(h) + ":" + "0" + str(m) + ":" + datetime.strftime(rome_now, "%S")
        else:
            return "0" + str(h) + ":" + "0" + str(m) + ":" + datetime.strftime(rome_now, "%S")
        return str(h) + ":" + "0" + str(m) + ":" + datetime.strftime(rome_now, "%S")


def create_json(patient, tempo, id_hospital):
    """
    Funzione per calcolare il file JSON del paziente in servizio
    :param patient: paziente servito
    :param tempo: tempo stimato del trasporto in ospedale
    :param id_hospital: ospedale di ricovero
    :return: JSON
    """
    data = [{
        "Id": 0,
        "Name": "Paolo",
        "Surname": "Melissari",
        "CF": "eeee",
        "Hospital": 0,
        "Time": 0,
        "TimeSend": "da stabilire",
        "TimeArrive": "da stabilire"
    }
    ]
    calculate_arrive_time(int(tempo / 60))
    data.__getitem__(0)['Id'] = patient.__getitem__(0)['Id']
    data.__getitem__(0)['Name'] = patient.__getitem__(0)['Name']
    data.__getitem__(0)['Surname'] = patient.__getitem__(0)['Surname']
    data.__getitem__(0)['Hospital'] = id_hospital
    data.__getitem__(0)['Time'] = int(tempo / 60)
    data.__getitem__(0)['CF'] = patient.__getitem__(0)['CF']
    rome_now = datetime.now(tz)
    data.__getitem__(0)['TimeSend'] = datetime.strftime(rome_now, "%H:%M:%S")
    data.__getitem__(0)['TimeArrive'] = calculate_arrive_time(int(tempo / 60))
    return data


def SingleData(patient, tabella, tabellaPazientiArrivo, tabellaPazientiUscita, sem, time1, tempi):
    """
    Logica del Cloud
    :param patient: paziente in servizio
    :param tabella: tabella ospedali
    :param tabellaPazientiArrivo: tabella pazienti in attesa di servizio
    :param tabellaPazientiUscita: tabella pazienti in servizio
    :param sem: semaforo
    :param time1: tempo di arrivo della richiesta di soccorso
    :param tempi: tabella dei tempi di elaborazione
    :return: Null
    """
    sem.acquire()
    km = calculate_distance(patient, tabella, tabellaPazientiArrivo, tabellaPazientiUscita, time1, tempi)
    sem.release()
    if km is None:
        time.sleep(30)
        time2 = time.time()
        thread = MainThread(tabella, tabellaPazientiArrivo, tabellaPazientiUscita, sem, time2, tempi)
        thread.start()
        return
    else:
        return


def calculate_distance(current_patient, tabella, tabellaPazientiArrivo, tabellaPazientiUscita, timeArr, tempi):
    """
    Calcolo effettivo dell'ospedale più vicino al paziente in richiesta
    :param current_patient: paziente corrente
    :param tabella: tabella ospedali
    :param tabellaPazientiArrivo: tabella pazienti in attesa di servizio
    :param tabellaPazientiUscita: tabella pazienti in servizio
    :param timeArr: tempo arrivo richiesta
    :param tempi: tabella tempi di elaborazione
    :return: distanza del paziente dall'ospedale espresso in Kilometri
    """
    first = 0
    km = 0
    coord_patient = (current_patient.__getitem__(0)['Position']['Lat'],
                     current_patient.__getitem__(0)['Position']['Long'])
    hospital = ConnectionDB.read_items(tabella)
    for current_Hospital in hospital:
        if current_Hospital['NumA'] != 0:
            coord_ambulance = (current_Hospital['Lat'], current_Hospital['Long'])
            current_km = geodesic(coord_patient, coord_ambulance).kilometers
            if first == 0:
                first = 1
                km = current_km
                id_hospital = current_Hospital['Id']
            elif km > current_km:
                km = current_km
                id_hospital = current_Hospital['Id']
    print(km)
    if first != 0:
        ConnectionDB.update_item(tabella, id_hospital, 0)
        tempo = calculate_time(km)
        patient = create_json(current_patient, tempo, id_hospital)
        ConnectionDB.delete_patient(tabellaPazientiArrivo, patient.__getitem__(0)['Id'])
        ConnectionDB.put_patient_exit(tabellaPazientiUscita, patient.__getitem__(0))
        ConnectionDB.put_time(tempi, patient.__getitem__(0)['Id'], str(time.time() - timeArr))
    if first == 0:
        return None
    return km


def calculate_time(km):
    """
    Calcolo del tempo di soccorso espresso in secondi
    :param km: kilometri
    :return: tempo di soccorso
    """
    tempo = km / vel_ambVP + km / vel_ambVO
    return tempo


class MainThread(Thread):
    tabella = {}
    tabellaPazientiArrivo = {}
    tabellaPazientiUscita = {}
    tempi = {}
    time1 = time.time()
    sem = threading.Semaphore(1)

    def __init__(self, tabella, tabellaPazientiArrivo, tabellaPazientiUscita, sem, time1, tempi):
        Thread.__init__(self)
        self.tabella = tabella
        self.tabellaPazientiArrivo = tabellaPazientiArrivo
        self.tabellaPazientiUscita = tabellaPazientiUscita
        self.sem = sem
        self.time1 = time1
        self.tempi = tempi

    def run(self):
        patient = ConnectionDB.read_items(self.tabellaPazientiArrivo)
        print(patient)
        if len(patient) >= 1:
            SingleData(patient, self.tabella, self.tabellaPazientiArrivo, self.tabellaPazientiUscita, self.sem,
                       self.time1, self.tempi)
            return
        return


def startapp(tabella, tabellaPazientiArrivo, tabellaPazientiUscita, sem, time1, tempi):
    thread = MainThread(tabella, tabellaPazientiArrivo, tabellaPazientiUscita, sem, time1, tempi)
    thread.start()
    return