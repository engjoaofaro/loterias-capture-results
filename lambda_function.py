import requests
import os

from s3.put_file import upload

megasena = 'megasena'
lotofacil = 'lotofacil'
lotomania = 'lotomania'

loterias = [megasena, lotomania, lotofacil]

base_url = os.getenv('BASE_URL')
token = os.getenv('TOKEN')


def lambda_handler(event, context):
    print(event, context)

    for loteria in loterias:
        print("Obtendo último resultado: ", loteria)
        payload = {'loteria': loteria, 'token': token}
        response = requests.get(base_url, payload)
        r = response.json()
        dezenas_sorteadas = r['dezenas']
        concurso = r['numero_concurso']
        print("Concurso: ", concurso)
        print("Dezenas sorteadas: ", dezenas_sorteadas)
        data = {
            'dezenas': dezenas_sorteadas
        }
        key_object = str(concurso)+"_"+str(loteria)
        upload(key_object, data)




