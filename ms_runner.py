import multiprocessing
import uvicorn
import config

from facade_service_utils.facade_service import facade_service
from config_server_utils.config_server import serve


def facade_service_runner():
    uvicorn.run(facade_service, host=config.HOST, port=config.FACADE_PORT)
        
    
def config_server_runner():
    serve(config.CONFIG_SERVER_PORT)

    
if __name__ == "__main__":
    proc1 = multiprocessing.Process(target=facade_service_runner)
    proc2 = multiprocessing.Process(target=config_server_runner)

    proc1.start()
    proc2.start()
    
    proc1.join()
    proc2.join()
