import time,json

class LOG: # Registro de log no azure tables
    def __init__(self) -> None:
        self.starttime = time.time() # Registro do tempo de execucao

    def handle_fail(self, log, param, message):
        self._insert_log(log, param, message, 'F')

    def handle_success(self, log, param, message=''):
        self._insert_log(log, param, message, 'S')
        
    def _insert_log(self, log, param, message, status):
        log.set(json.dumps({
            'PartitionKey': param['service'],
            'RowKey': param['id'],
            'User': param['user'],
            'Param': json.dumps(param['data'],separators=(',', ':')),
            'Status': status,
            'Output': message,
            'Time': time.time()-self.starttime,
            'Service': param['service'].split("-")[0]
        }))
