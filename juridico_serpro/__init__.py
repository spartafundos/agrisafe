import pandas as pd
import azure.functions as func
from shared import fcnsql
from . import api # CONTEM FUNCOES DE CONSULTA A API EXTERNA

DATABASE_SCHEMA = 'juridico'
DATABASE_SP = 'serpro{0}_update'

def executa_processo_A(param):
    sql = fcnsql.SQL(param['user'])
    param = param['data']

    svc = param.get('servico') # CNPJ ou CND ou DividaAtiva
    ident = param.get('numero') # CNPJ
    if svc is None or ident is None:
        raise Exception("Invalid parameters")
    ident = str(ident).replace(".","").replace(" ","").replace("/","").replace("-","")

    update = param.get('update') # IGNORE IF DATA IS ALREADY AVALIABLE IN DATABASE
    if update is None:
        update = False
    
    # f = funcao para processar dados para exibicao
    # g = funcao para obter dados consultando api Serpro
    if svc == 'CNPJ':
        funcao_consulta = api.consultacnpj
    elif svc == 'CND':
        funcao_consulta = api.consultacnd
    elif svc == 'DividaAtiva':
        funcao_consulta = api.consultadividaativa
    else:
        raise Exception("Invalid option")

    # Faz consulta nova a API se dado nao existe ou update = True
    if not update:
        data,_ = sql.execute(DATABASE_SCHEMA, DATABASE_SP.format(svc), {'acao':'S','st_CNPJ':ident})
        if data: # data[0][0] é um JSON
            return data[0][0]
    
    # Faz consulta externa e salva no sql
    relatorio = funcao_consulta(ident) # Consulta externa
    sql.execute(DATABASE_SCHEMA, DATABASE_SP.format(svc), {
        'st_CNPJ': ident,
        'dt_Data': pd.to_datetime('today').utcnow(),
        'st_JSON': data
    })

    return relatorio

def main(msg: func.QueueMessage, logtable: func.Out[str]):
    # Esses imports estao aqui para evitar carregamento deles na chamada HTTP
    import traceback
    from shared import fcnlog
    log = fcnlog.LOG()
    param = msg.get_json()

    try:
        log.handle_success(logtable,param,executa_processo_A(param))
    except:
        log.handle_fail(logtable,param,traceback.format_exc())

    return
