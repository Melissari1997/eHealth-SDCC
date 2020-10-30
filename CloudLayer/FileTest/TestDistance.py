import time

import boto3

from Cloud import ConnectionDB, FoundHospital

client = boto3.resource('dynamodb', aws_access_key_id="******",
                        aws_secret_access_key="******",
                        region_name='us-east-1')
tabella = client.Table('ospedali')
tabellaPazientiArrivo = client.Table('pazienti1')
tabellaPazientiUscita = client.Table('pazientiuscita')
tempi = client.Table('tempi')
pazienti = ConnectionDB.read_items(tabellaPazientiUscita)
current_patient1 = [
    {
        "Id": 0,
        "Name": "Prova",
        "Surname": "1",
        "CF": "0",
        "Position": {
            "Lat": 41.9233802,
            "Long": 12.5215356
        }
    }
]

current_patient2 = [
    {
        "Id": 1,
        "Name": "Prova",
        "Surname": "2",
        "CF": "1",
        "Position": {
            "Lat": 41.9143363,
            "Long": 12.411015
        }
    }
]

current_patient3 = [
    {
        "Id": 2,
        "Name": "Prova",
        "Surname": "3",
        "CF": "3",
        "Position": {
            "Lat": 41.8686745,
            "Long": 12.6288151
        }
    }
]
"""
sono stati presi in considerazione 3 posizioni
"""

km0, id_hospital0 = FoundHospital.calculate_distance(current_patient1, tabella, tabellaPazientiArrivo,
                                             tabellaPazientiUscita, time.time(), tempi)

km1, id_hospital1 = FoundHospital.calculate_distance(current_patient2, tabella, tabellaPazientiArrivo,
                                             tabellaPazientiUscita, time.time(), tempi)

km2, id_hospital2 = FoundHospital.calculate_distance(current_patient3, tabella, tabellaPazientiArrivo,
                                             tabellaPazientiUscita, time.time(), tempi)
print(id_hospital0,id_hospital1, id_hospital2)
if id_hospital0 == 8 and id_hospital1 == 3 and id_hospital2 == 11:
    print("test passato")
else:
    print("test non passato")
