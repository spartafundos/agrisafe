import traceback, json
import azure.functions as func
from shared import fcnlog

def autenticar(req, tokens):
    client = req.headers['client_id']
    token = req.headers['access_token']

    for elem in tokens:
        if elem['RowKey']==client:
            if elem['Token']==token:
                return client, elem['Level']
    raise

def main(req: func.HttpRequest, context: func.Context, tokens: str, logtable: func.Out[str]) -> func.HttpResponse:
    try:
        client, level = autenticar(req, json.loads(tokens))
    except:
        return func.HttpResponse("Access Denied",status_code=401)
    
    param={'user': client, 'level': level, 'id': context.invocation_id}
    try: #Verifica se corpo é json valido
        param['data'] = req.get_json()
    except:
        return func.HttpResponse("Bad Request",status_code=400)

    param['service'] = req.route_params.get('service')
    log = fcnlog.LOG()
    try:
        exec(f"from {param['service'].replace('-','_')} import executa_processo_A")
        message = eval('executa_processo_A(param)')
        log.handle_success(logtable,param)
    except:
        log.handle_fail(logtable,param,traceback.format_exc())
        message = 'Erro'

    return func.HttpResponse(message, status_code=200)
