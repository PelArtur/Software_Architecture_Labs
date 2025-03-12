import grpc
import random
import config
from concurrent import futures

import config_server_utils.config_server_pb2 as config_server_pb2
import config_server_utils.config_server_pb2_grpc as config_server_pb2_grpc

CONFIG_SERVER_HOST: str = f"{config.HOST}:{config.CONFIG_SERVER_PORT}"


class IPServiceServicer(config_server_pb2_grpc.IPServiceServicer):
    def __init__(self):
        self.services = {
                config.CONFIG_SERVER_LOGGING:  [],
                config.CONFIG_SERVER_MESSAGES: [f"{config.HOST}:{config.MESSAGES_PORT}"]
            }


    def AddIP(self, request, context):
        if request.service not in self.services:
            print(f"Config server {config.CONFIG_SERVER_PORT}. Service not found")
            return config_server_pb2.Response(message="Service not found")

        if request.ip not in self.services[request.service]:
            self.services[request.service].append(request.ip)
            print(f"Config server {config.CONFIG_SERVER_PORT}. IP {request.ip} added to {request.service}")
            return config_server_pb2.Response(message=f"IP {request.ip} added to {request.service}")
        
        print(f"Config server {config.CONFIG_SERVER_PORT}. IP {request.ip} already exists in {request.service}")
        return config_server_pb2.Response(message=f"IP {request.ip} already exists in {request.service}")


    def RemoveIP(self, request, context):
        if request.service not in self.services:
            print(f"Config server {config.CONFIG_SERVER_PORT}. Service not found")
            return config_server_pb2.Response(message="Service not found")

        if request.ip in self.services[request.service]:
            self.services[request.service].remove(request.ip)
            print(f"Config server {config.CONFIG_SERVER_PORT}. IP {request.ip} removed from {request.service}")
            return config_server_pb2.Response(message=f"IP {request.ip} removed from {request.service}")
        
        print(f"Config server {config.CONFIG_SERVER_PORT}. IP {request.ip} not found in {request.service}")
        return config_server_pb2.Response(message=f"IP {request.ip} not found in {request.service}")


    def GetIPs(self, request, context):
        if request.service not in self.services:
            return config_server_pb2.IPList(ips=[])

        shuffled_ips = self.services[request.service][:]
        random.shuffle(shuffled_ips)
        return config_server_pb2.IPList(ips=" ".join(shuffled_ips))


def get_config_server_client() -> config_server_pb2_grpc.IPServiceStub:
    channel = grpc.insecure_channel(CONFIG_SERVER_HOST)
    return config_server_pb2_grpc.IPServiceStub(channel)


def add_ip_to_config_server(service: str, ip: str) -> str:
    client = get_config_server_client()
    request = config_server_pb2.IPRequest(service=service, ip=ip)
    response = client.AddIP(request)
    return response.message


def remove_ip_from_config_server(service: str, ip: str) -> str:
    client = get_config_server_client()
    request = config_server_pb2.IPRequest(service=service, ip=ip)
    response = client.RemoveIP(request)
    return response.message


def get_ips_from_config_server(service: str) -> str:
    client = get_config_server_client()
    request = config_server_pb2.ServiceRequest(service=service)
    response = client.GetIPs(request)
    return response.ips
    

def serve(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    config_server_pb2_grpc.add_IPServiceServicer_to_server(IPServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()
