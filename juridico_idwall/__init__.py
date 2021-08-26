import pandas as pd
import json
import azure.functions as func
from shared import fcnsql
from . import api # CONTEM FUNCOES DE CONSULTA A API EXTERNA

DATABASE_SCHEMA = 'juridico'
DATABASE_SP = 'idwall_update'

# A MODE: RETRIEVE REPORT FROM DATABASE OR REQUEST NEW REPORT FROM IDWALL API
def executa_processo_A(param):
    sql = fcnsql.SQL(param['user'])
    param = param['data']

    ident = param.get('numero') # CPF ou CNPJ
    if ident is None:
        raise Exception("Invalid parameters")
    ident = str(ident).replace(".","").replace(" ","").replace("/","").replace("-","")

    update = param.get('update') # IGNORE IF DATA IS ALREADY AVALIABLE IN DATABASE
    if update is None:
        update = False

    # Verifica se ident é CNPJ ou CPF
    tipo = 1 if len(ident)==14 else 2
    if tipo == 1:
        data = {"matriz": "sparta_bgc_pj","parametros": {"cnpj_numero": ident}}
    elif tipo == 2:
        data = {"matriz": "sparta_bgc_pf","parametros": {"cpf_numero": ident}}
        estados = param.get("estados")
        if estados:
            data['opcoes'] = {'estados_consultados':json.loads(estados)}
    else:
        raise Exception("Invalid parameters")

    # Faz consulta nova a API se dado nao existe ou update = True
    if not update:
        dados,_ = sql.execute(DATABASE_SCHEMA, DATABASE_SP, {'acao':'S','st_CNPJ':ident})
        if dados:
            return dados[0][0]

    # Faz consulta externa e salva no sql
    relatorio = api.gerarRelatorio(data)
    numero = json.loads(relatorio)['result']['numero']

    sql.execute(DATABASE_SCHEMA, DATABASE_SP, {
        'st_RelatorioID': numero,
        'st_CNPJ': ident,
        'dt_Data': pd.to_datetime('today').date(),
        'st_JSON': relatorio
    })

    return relatorio

# B MODE: CHECK FOR FINISHED REPORTS IN IDWALL DATABASE
def executa_processo_B(param):
    sql = fcnsql.SQL(param['user'])

    # CHECK FOR UNFINISHED REPORTS IN DATABASE
    data,cols = sql.execute(DATABASE_SCHEMA, DATABASE_SP, {'acao':'SU'}, False)
    if not data:
        return
    # VERIFY WHICH UNFINISHED REPORTS ARE FINISHED
    df = pd.DataFrame.from_records(data,columns=cols)
    aux = pd.DataFrame.from_dict(json.loads(api.listarRelatorios())['result']['itens'])
    df = pd.merge(df,aux,left_on='st_RelatorioID',right_on='numero',how='left')
    
    # UPDATE FINISHED REPORTS IN DATABASE
    for index,row in df[df['numero'].isnull()].iterrows():
        relatorio = api.consultarRelatorio(row['st_RelatorioID'])
        sql.execute(DATABASE_SCHEMA, DATABASE_SP, {
            'st_RelatorioID': row['st_RelatorioID'],
            'st_CNPJ': row['st_CNPJ'],
            'dt_Data': row['dt_Data'],
            'st_JSON': relatorio,
            'bl_Terminado': 1
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
