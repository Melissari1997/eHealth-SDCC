import time

import mysql.connector
"""
Crea il database
"""
time.sleep(5)
def create():
    try:
        config = {
            "host": "mysql",
            "user": "root",
            "passwd": "password",
            'port': '3306'
        }
        while True:
            try:
                db = mysql.connector.connect(**config)
                break
            except:
                print("Retry")
                time.sleep(5)
                continue
        cursor = db.cursor(buffered=True)
        cursor.execute("CREATE DATABASE IF NOT EXISTS patient")
        cursor.close()
        db.close()
        config = {
            "host": "mysql",
            "user": "root",
            "passwd": "password",
            'port': '3306',
            'database': 'patient'
        }

        db = mysql.connector.connect(**config)
        cursor = db.cursor(buffered=True)

        cursor.execute("SET @@session.time_zone = '+02:00' ")
        cursor.execute("SET GLOBAL event_scheduler  = ON")
        cursor.execute("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO'")
        cursor.execute("SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED")
        #  "DELETE FROM pending WHERE TIMESTAMPDIFF(MINUTE,sendDate, NOW()) > 1 ; " \
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS pending (CF VARCHAR(100), patientName VARCHAR(100), patientSurname VARCHAR(100), sensorType VARCHAR(100), gravity VARCHAR(100), sendDate TIMESTAMP , PRIMARY KEY (CF,sendDate,sensorType))")
        cursor.execute("CREATE INDEX timestampidx ON pending(sendDate)")
        """
               deletePendingTable = "CREATE EVENT IF NOT EXISTS deletePendingPatient " \
                "ON SCHEDULE EVERY 24 HOUR  " \
                "ON COMPLETION PRESERVE " \
                "DO BEGIN " \
                "DELETE FROM pending WHERE sendDate < NOW() - INTERVAL 10 HOUR ; " \
                "END;"
        cursor.execute(deletePendingTable)  
        """
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS notified (CF VARCHAR(100), patientName VARCHAR(100), patientSurname VARCHAR(100), sensorType VARCHAR(100), mediumEmail BOOLEAN ,highEmail BOOLEAN, cloud BOOLEAN , sendDate TIMESTAMP,PRIMARY KEY (CF,sensorType))")
        cursor.close()
        db.commit()
        return 0

    except mysql.connector.Error as err:
        print(str(err), flush=True)
        exit(-1)


if __name__ == "__main__":
    create()
