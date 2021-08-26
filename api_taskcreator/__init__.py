import json, os
import azure.functions as func

# Run every 10 minutes for now because there is no need to run every minute yet
def main(mytimer: func.TimerRequest, context: func.Context,
# Queue for each service
jusbrasil: func.Out[str],
idwall: func.Out[str]
) -> None:
    
    # CREATE PARAM VARIABLE WITH SHARED PARAMETERS
    param = {'user':os.environ['SQL_USER'],'id':context.invocation_id} #context id to avoid importing uuid

    # RUN JURIDICO_IDWALL EXECUTA_PROCESSO_B
    param['service'] = 'juridico-idwall'
    param['data'] = {}
    idwall.set(json.dumps(param))

    # RUN JURIDICO_JUSBRASIL EXECUTA_PROCESSO_B
    param['service'] = 'juridico-jusbrasil'
    param['data'] = {}
    jusbrasil.set(json.dumps(param))

    return
