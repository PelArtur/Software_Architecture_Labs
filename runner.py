import multiprocessing
import uvicorn

from facade_service.facade_service import facade_service
from messages_service.messages_service import message_service
from logging_service.logging_service import serve


host = "127.0.0.1"

def facade_service_runner():
    uvicorn.run(facade_service, host=host, port=8000)
    

def messages_service_runner():
    uvicorn.run(message_service, host=host, port=8001)
    
    
def logging_service_runner():
    serve(50051)
    
    
if __name__ == "__main__":
    proc1 = multiprocessing.Process(target=facade_service_runner)
    proc2 = multiprocessing.Process(target=messages_service_runner)
    proc3 = multiprocessing.Process(target=logging_service_runner)
    
    proc1.start()
    proc2.start()
    proc3.start()
    
    proc1.join()
    proc2.join()
    proc3.join()
