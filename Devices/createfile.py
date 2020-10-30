import json
import os
"""
Invia gli indirizzi email al cloud, per fare in modo che poi i fog layer possano richiederli
"""
file = {
    "email": [

    ]
}

with open("settings/big.json") as reader:
    data = json.load(reader)
    reader.close()

i = 0
for index in range(0, len(data)):
    item = {
        "PutRequest": {
            "Item": {
                "Id": {"N": str(data[index]['Id'])},
                "CF": {"S": data[index]['CodiceFiscale']},
                "Email": {"S": data[index]['Email']}
            }
        }
    }
    file['email'].append(item)
    i = i + 1
    if i == 25 or index == len(data):
        print(i)
        print("index: "+str(index))
        i = 0

        with open("email", "w") as emailDataset:
            json.dump(file, emailDataset)
            emailDataset.close()
            os.system("aws dynamodb batch-write-item --request-items file://email")
            file = {
                "email": [

                ]
            }
