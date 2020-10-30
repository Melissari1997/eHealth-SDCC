from boto3.dynamodb.conditions import Key, Attr
""" Insieme di funzione per potersi connettere al DataBase e eseguire Query alle varie tabelle
"""
def read_items(table):
    items = table.scan(
        FilterExpression=Attr('Id').gte(0)
    )
    return items['Items']


def delete_patient(table, index):
    response = table.delete_item(
        Key={
            'Id': index
        }
    )
    return response



def put_patient(table, name, surname, lat, long, cf ,indice):
    response = table.put_item(
        Item={
            'Id': indice,
            'Name': name,
            'Surname': surname,
            'CF': cf,
            'Position': {
                'Lat': lat,
                'Long': long
            }
        }
    )
    return response

def put_time(table,indice,time1):
    response = table.put_item(
        Item={
            'Id': indice,
            'Time': time1
        }
    )
    return response


def read_item(table, id_hospital):
    item = table.query(
        KeyConditionExpression=Key('Id').eq(id_hospital)
    )
    return item['Items']



def update_item(table, id_hospital, value):
    # value rappresenta se devo decrementare o incrementare
    # 0 decremento
    # 1 incremento
    item = read_item(table, id_hospital)
    if value == 0:
        item.__getitem__(0)['NumA'] = item.__getitem__(0)['NumA'] - 1
    else:
        item.__getitem__(0)['NumA'] = item.__getitem__(0)['NumA'] + 1
    na = item.__getitem__(0)['NumA']
    table.update_item(
        Key={'Id': id_hospital},
        UpdateExpression='SET NumA = :val1',
        ExpressionAttributeValues={
            ':val1': na
        }
    )


def put_patient_exit(table, patient):
    print(patient)
    response = table.put_item(
        Item={
            'Id': patient['Id'],
            'Name': patient['Name'],
            'Surname': patient['Surname'],
            'Hospital': patient['Hospital'],
            'CF': patient['CF'],
            'Time': patient['Time'],
            'TimeSend': patient['TimeSend'],
            'TimeArrive': patient['TimeArrive']
        }
    )
    return response