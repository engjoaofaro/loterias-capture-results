import boto3
import os
import json

client = boto3.client('s3')
bucket = os.getenv('BUCKET')


def upload(key_object, data):
    print("Recebendo dados: ", data)
    file_name = key_object+".json"
    with open('/tmp/' + file_name, 'w+t') as outfile:
        json.dump(data, outfile)
        print('temp:', outfile)
    path = "/tmp/" + file_name
    client.upload_file(path, bucket, "results/"+file_name)
    print("Upload feito com sucesso.")



