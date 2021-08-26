import json
import pandas as pd
import azure.functions as func
from shared import fcnsql
from . import api # CONTEM FUNCOES DE CONSULTA A API EXTERNA

DATABASE_SCHEMA = 'juridico'
DATABASE_SP = 'jusbrasil_update'

# A MODE: RETRIEVE REPORT FROM DATABASE OR REQUEST NEW REPORT FROM JUSBRASIL API
def executa_processo_A(param):
    sql = fcnsql.SQL(param['user'])
    param = param['data']

    termo = param.get('termo') # Nome ou razao social
    if termo is None:
        raise Exception("Invalid Parameters")
    else:
        termo = termo.strip()

    processo = param.get('processo')

    update = param.get('update') # IGNORE IF DATA IS ALREADY AVALIABLE IN DATABASE
    if update is None:
        update = False

    # Faz consulta nova a API se dado nao existe ou update = True
    if not update:
        if not processo: # Se processo nao existe, entao é consulta a dossier
            data,cols = sql.execute(DATABASE_SCHEMA, DATABASE_SP, {'acao':'S','st_Termo':termo})
            if data: # data[0][0] é um JSON
                return data[0][0]
        else: # Caso de consulta a processo
            data,_ = sql.execute(DATABASE_SCHEMA, DATABASE_SP, {'acao':'S','st_Termo':termo,'st_LawsuitID':processo})
            if data: # data[0][0] é um JSON
                return data[0][0]
    
    # Faz consulta externa e salva no sql
    relatorio = api.gerarRelatorio(termo)
    numero = json.loads(relatorio)['dossier_id']

    sql.execute('Juridico','JusBrasil.Dossier_Update', {
        'st_DossierID': numero,
        'st_Termo': termo,
        'dt_Data': pd.to_datetime('today').date(),
        'st_JSON': relatorio,
        'st_Email': param.get('email') # Se usuario mandou email, entao quando concluido, sera disparado email de alerta
    })

    return relatorio

# B MODE: CHECK FOR FINISHED REPORTS IN JUSBRASIL API
def executa_processo_B(param):
    sql = fcnsql.SQL(param['user'])

    # CHECK FOR UNFINISHED REPORTS IN DATABASE
    data,cols = sql.execute(DATABASE_SCHEMA, DATABASE_SP, {'acao':'SU'}, False)
    if not data:
        return
    # VERIFY WHICH UNFINISHED REPORTS ARE FINISHED
    df = pd.DataFrame.from_records(data,columns=cols)
    aux = pd.DataFrame.from_dict(json.loads(api.listarRelatorios())['results'])
    aux = aux[aux['status']=='FINISHED']
    df = pd.merge(df,aux,left_on='st_DossierID',right_on='_id',how='left')
    
    # UPDATE FINISHED REPORTS IN DATABASE
    for index,row in df.iterrows():
        dossier = api.listarRelatorios(row['st_DossierID'])
        sql.execute(DATABASE_SCHEMA, DATABASE_SP,{
            'st_DossierID': row['st_DossierID'],
            'st_Termo': row['st_Termo'],
            'dt_Data': row['dt_Data'],
            'st_JSON': dossier,
            'bl_Terminado': 1,
        })

        # GET LAWSUITS FOR REPORT
        files = json.loads(api.listarRelatorios(row['st_DossierID']+'/files?protocol=https'))['files']
        for url in files:
            lawsuit = api.downloadfile(url)
            sql.execute(DATABASE_SCHEMA, DATABASE_SP,{
                'st_LawsuitID': url.split('/')[-1]
                ,'st_DossierID': row['st_DossierID']
                ,'st_JSON': lawsuit
            })
    
    return None

def main(msg: func.QueueMessage, logtable: func.Out[str]) -> None:
    # Esses imports estao aqui para evitar carregamento deles na chamada HTTP
    import traceback
    from shared import fcnlog
    log = fcnlog.LOG()
    param = msg.get_json()

    try:
        # Na chamada automatica (api_taskcreator) param['data'] = {}
        if param['data']:
            message = executa_processo_A(param)
        else:
            message = executa_processo_B(param)
        log.handle_success(logtable,param,message)
    except:
        log.handle_fail(logtable,param,traceback.format_exc())

    return
