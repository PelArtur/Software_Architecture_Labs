from typing import List

#Main data
HOST: str = "127.0.0.1"

#Microservices ports
FACADE_PORT: int = 8000
MESSAGES_PORT: int = 8001
CONFIG_SERVER_PORT: int = 8002
BASE_LOGGING_PORT: int = 50051
BASE_MESSAGING_PORT: int = 51000

#Hazelcast
HZ_CLUSTER_NAME: str = "dev"
HZ_MESSAGES_MAP_NAME: str = "messages_map"

#Config server keys
CONFIG_SERVER_LOGGING: str = "logging_service"
CONFIG_SERVER_MESSAGES: str = "messages_service"

#Kafka
BOOTSTRAP_SERVERS: List[str] = [
    "localhost:19092",
    "localhost:19093",
    "localhost:19094"
]
MS_QUEUE_TOPIC_NAME: str = "messages_queue"
MS_QUEUE_CONSUMER_GROUP: str = "messages_service_group"
CONSUMER_POLL_TIMEOUT_MS: int = 10
PRODUCER_FLUSH_TIMEOUT_S: int = 10

#Exceptions
class InactiveService(Exception):
    """The microservice is inactive."""
    pass
