import requests
import os

from s3.put_file import upload
from secret import get_api_token

megasena = 'megasena'
lotofacil = 'lotofacil'
lotomania = 'lotomania'

loterias = [megasena, lotomania, lotofacil]

base_url = os.getenv('BASE_URL')


def lambda_handler(event, context):
    print(event, context)
    token = get_api_token()

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




