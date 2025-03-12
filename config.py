#Main data
HOST: str = "127.0.0.1"

#Microservices ports
FACADE_PORT: int = 8000
MESSAGES_PORT: int = 8001
CONFIG_SERVER_PORT: int = 8002
BASE_LOGGING_PORT: int = 50051

#Hazelcast
HZ_CLUSTER_NAME: str = "dev"
HZ_MESSAGES_MAP_NAME: str = "messages_map"

#Config server keys
CONFIG_SERVER_LOGGING: str = "logging_service"
CONFIG_SERVER_MESSAGES: str = "messages_service"

#Exceptions
class InactiveService(Exception):
    """The microservice is inactive."""
    pass
