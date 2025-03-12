import multiprocessing
import os
import config

from logging_service_utils.logging_service import serve

def run_node():
    os.system(f".\\bin\\hz-start.bat")


def run_logging_service(port: int):
    serve(port)
    
    
if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else config.BASE_LOGGING_PORT

    proc1 = multiprocessing.Process(target=run_node)
    proc2 = multiprocessing.Process(target=run_logging_service, args=(port, ))
    
    proc1.start()
    proc2.start()

    proc1.join()
    proc2.join()   
