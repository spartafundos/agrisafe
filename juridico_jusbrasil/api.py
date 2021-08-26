import requests, json, os
import datetime as dt

headers = {
        'Content-Type':'application/json',
        'Authorization': os.environ['AUTH_JUSBRASIL']
    }

def listarRelatorios(endpoint=None):
    url = 'https://dossier-api.jusbrasil.com.br/v5/dossier'
    if endpoint:
        url+= '/'+endpoint

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def downloadfile(url):
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text

def gerarRelatorio(termos):
    if isinstance(termos, str):
        termos = termos.split(',')

    url = 'https://dossier-api.jusbrasil.com.br/v5/dossier'

    # DECISAO DE PROJETO: RESTRINGIR DT_FIM A DATA ATUAL E DT_INICIO A DT_FIM - 20 ANOS
    dt_fim = dt.datetime.utcnow()
    dt_inicio = dt_fim.replace(year=dt_fim.year-20)

    data = {
    "filter": termos,
    "kind": "LAWSUIT",
    "artifacts": [ "lawsuits" ],
    "from_date": dt_inicio.strftime("%d/%m/%Y"),
    "to_date": dt_fim.strftime("%d/%m/%Y"),
    "number_of_pages": 1000,
    "webhook_url": "http://webhook-url", # OPCAO DE WEBHOOK NAO UTILIZADA
    "courts": [
        "TJRJ",
        "TJBA",
        "STF",
        "STJ",
        "STM",
        "TJAC",
        "TJAL",
        "TJAM",
        "TJAP",
        "TJBA",
        "TJCE",
        "TJDF",
        "TJES",
        "TJGO",
        "TJMA",
        "TJMG",
        "TJMS",
        "TJMT",
        "TJPA",
        "TJPB",
        "TJPE",
        "TJPI",
        "TJPR",
        "TJRJ",
        "TJRN",
        "TJRO",
        "TJRR",
        "TJRS",
        "TJSC",
        "TJSE",
        "TJSP",
        "TJTO",
        "TRE-AC",
        "TRE-AL",
        "TRE-AM",
        "TRE-AP",
        "TRE-BA",
        "TRE-CE",
        "TRE-DF",
        "TRE-ES",
        "TRE-GO",
        "TRE-MA",
        "TRE-MG",
        "TRE-MS",
        "TRE-MT",
        "TRE-PA",
        "TRE-PB",
        "TRE-PE",
        "TRE-PI",
        "TRE-PR",
        "TRE-RJ",
        "TRE-RN",
        "TRE-RO",
        "TRE-RR",
        "TRE-RS",
        "TRE-SC",
        "TRE-SE",
        "TRE-SP",
        "TRE-TO",
        "TRF-1",
        "TRF-2",
        "TRF-3",
        "TRF-4",
        "TRF-5",
        "TRT-1",
        "TRT-2",
        "TRT-3",
        "TRT-4",
        "TRT-5",
        "TRT-6",
        "TRT-7",
        "TRT-8",
        "TRT-9",
        "TRT-10",
        "TRT-11",
        "TRT-12",
        "TRT-13",
        "TRT-14",
        "TRT-15",
        "TRT-16",
        "TRT-17",
        "TRT-18",
        "TRT-19",
        "TRT-20",
        "TRT-21",
        "TRT-22",
        "TRT-23",
        "TRT-24",
        "TSE",
        "TST"
    ]}

    r = requests.post(url, data = json.dumps(data), headers = headers)
    if r.status_code != 200:
        raise Exception(r.status_code, r.text)
    return r.text