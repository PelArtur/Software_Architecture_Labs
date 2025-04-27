#Main data
HOST: str = "127.0.0.1"

#Microservices base ports
BASE_FACADE_PORT: int = 8000
BASE_LOGGING_PORT: int = 50051
BASE_MESSAGING_PORT: int = 51000
CONSUL_PORT: int = 8500

#Microservices names
SERVICE_NAME_LOGGING: str = "logging_service"
SERVICE_NAME_MESSAGES: str = "messages_service"
SERVICE_NAME_FACADE: str = "facade_service"

#Config files and data keys
MESSAGES_QUEUE_CONFIG_PATH: str = "./config_files/messages_queue_config.json"
MESSAGES_QUEUE_CONFIG_KEY: str = "messages_queue_config"
HAZELCAST_CONFIG_PATH: str = "./config_files/hazelcast_config.json"
HAZELCAST_CONFIG_KEY: str = "hazelcast_config"

#Exceptions
class InactiveService(Exception):
    """The microservice is inactive."""
    pass
