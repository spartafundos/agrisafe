import requests, json, os

def get_token():
    url = 'https://gateway.apiserpro.serpro.gov.br/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + os.environ['AUTH_SERPRO']
        }
    data = { "grant_type": "client_credentials" }
    r = requests.post(url, data = data, headers = headers)

    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    data = json.loads(r.text)
    return data['token_type'],data['access_token']

def consultacnpj(cnpj):
    token = get_token()

    url = 'https://gateway.apiserpro.serpro.gov.br/consulta-cnpj-df/v2/empresa/{}'.format(cnpj)
    headers = {
        'Accept':'application/json',
        'Authorization': f'{token[0]} {token[1]}'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def consultacnd(ident):
    token = get_token()

    if len(ident) == 14:
        tipo = 1
    elif len(ident) == 11:
        tipo = 2
    else:
        tipo = 3

    url = 'https://gateway.apiserpro.serpro.gov.br/consulta-cnd/v1/certidao'
    headers = {
        'Accept':'application/json',
        'Authorization': f'{token[0]} {token[1]}'
    }
    data = {
        'TipoContribuinte':tipo,
        'ContribuinteConsulta':ident,
        'CodigoIdentificacao':str(9000+tipo)
    }
    r = requests.post(url, data = data, headers = headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def consultadividaativa(cnpj):
    token = get_token()

    url = 'https://gateway.apiserpro.serpro.gov.br/consulta-divida-ativa-df/api/v1/devedor/{}'.format(cnpj)
    headers = {
        'Accept':'application/json',
        'Authorization': f'{token[0]} {token[1]}'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text