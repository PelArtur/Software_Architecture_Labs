import grpc
import atexit
import hazelcast
import config
from concurrent import futures

import logging_service_utils.logging_pb2 as logging_pb2
import logging_service_utils.logging_pb2_grpc as logging_pb2_grpc
from consul_service_utils.consul_service import register_service, deregister_service, get_key_value


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self, port: int):
        self.__port = port
        self.__service_id = config.SERVICE_NAME_LOGGING + "-" + str(self.__port)
        
        hz_config = get_key_value(config.HAZELCAST_CONFIG_KEY)
        self.client = hazelcast.HazelcastClient(cluster_name=hz_config["cluster_name"])
        self.messages_map = self.client.get_map(name=hz_config["messages_map_name"]).blocking()

        register_service(
            service_name=config.SERVICE_NAME_LOGGING,
            service_id=self.__service_id,
            service_address=config.HOST,
            service_port=self.__port
        )
        atexit.register(self.cleanup)
        

    def LogMessage(self, request, context):
        self.messages_map.put(request.uid, request.msg)
        print(f"Logging Service {self.__port}. Received message: {request.msg}. Message saved with uid: {request.uid}")
        return logging_pb2.LogResponse(status="OK")
    

    def GetLogs(self, request, context):
        print(f"Logging Service {self.__port}. Sent all messages")
        return logging_pb2.LogList(messages=", ".join(self.messages_map.values()))

    
    def cleanup(self):
        print(f"Logging Service {self.__port}. Cleaning up LoggingService {self.__port}...")
        deregister_service(self.__service_id)
        self.client.shutdown()


#run gRPC server
def serve(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(port=port), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()
