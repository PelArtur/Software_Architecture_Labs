import grpc
from concurrent import futures
import logging_service.logging_pb2 as logging_pb2
import logging_service.logging_pb2_grpc as logging_pb2_grpc


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self):
        self.messages_dict = dict()
        

    def LogMessage(self, request, context):
        if request.uid not in self.messages_dict:
            self.messages_dict[request.uid] = request.msg
            print(f"Received message: {request.msg}. Message saved with uid: {request.uid}")
        return logging_pb2.LogResponse(status="OK")
    

    def GetLogs(self, request, context):
        return logging_pb2.LogList(messages=", ".join(self.messages_dict.values()))
    
#run gRPC server
def serve(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))                 # create server
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)  #add LoggingService to server
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()
    