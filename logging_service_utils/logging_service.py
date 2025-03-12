import grpc
import atexit
import hazelcast
import config

from concurrent import futures

import logging_service_utils.logging_pb2 as logging_pb2
import logging_service_utils.logging_pb2_grpc as logging_pb2_grpc
from config_server_utils.config_server import add_ip_to_config_server, remove_ip_from_config_server


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self, port: int):
        self.port = port
        self.client = hazelcast.HazelcastClient(cluster_name=config.HZ_CLUSTER_NAME)
        self.messages_map = self.client.get_map(config.HZ_MESSAGES_MAP_NAME).blocking()
        add_ip_to_config_server(config.CONFIG_SERVER_LOGGING, f"{config.HOST}:{self.port}")
        atexit.register(self.cleanup)
        

    def LogMessage(self, request, context):
        self.messages_map.put(request.uid, request.msg)
        print(f"Logging Service {self.port}. Received message: {request.msg}. Message saved with uid: {request.uid}")
        return logging_pb2.LogResponse(status="OK")
    

    def GetLogs(self, request, context):
        print(f"Logging Service {self.port}. Sent all messages")
        return logging_pb2.LogList(messages=", ".join(self.messages_map.values()))

    
    def cleanup(self):
        print(f"Logging Service {self.port}. Cleaning up LoggingService {self.port}...")
        remove_ip_from_config_server(config.CONFIG_SERVER_LOGGING, f"{config.HOST}:{self.port}")
        self.client.shutdown()


#run gRPC server
def serve(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(port=port), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()
