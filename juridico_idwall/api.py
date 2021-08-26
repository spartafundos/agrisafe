import requests, json, os

headers = {
    'Content-Type':'application/json',
    'Authorization': os.environ['AUTH_IDWALL']
}

def consultarRelatorio(numero, endpoint='/dados'):
    url = f'https://api-v2.idwall.co/relatorios/{numero}'+endpoint
    
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def gerarRelatorio(data):
    url = 'https://api-v2.idwall.co/relatorios'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def listarRelatorios(endpoint='/pendentes'):
    url = 'https://api-v2.idwall.co/relatorios'
    if endpoint:
        url+= endpoint
    
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text