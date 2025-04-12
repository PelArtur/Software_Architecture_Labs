import uuid
import grpc
import requests
import config
from fastapi import FastAPI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from typing import List

import logging_service_utils.logging_pb2 as logging_pb2
import logging_service_utils.logging_pb2_grpc as logging_pb2_grpc
from config_server_utils.config_server import get_ips_from_config_server
from kafka_utils.kafka_hf import create_producer, create_topic
from kafka.errors import KafkaTimeoutError


facade_service = FastAPI()
create_topic(config.MS_QUEUE_TOPIC_NAME, 3, 3)
producer = create_producer()

class MessageRequest(BaseModel):
    message: str
    

def get_grpc_client(host: str) -> logging_pb2_grpc.LoggingServiceStub:
    channel = grpc.insecure_channel(host)
    return logging_pb2_grpc.LoggingServiceStub(channel)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_to_logging_service(uid: str, msg: str) -> str:
    logging_client_ip: List[str] = get_ips_from_config_server(config.CONFIG_SERVER_LOGGING).split(" ")
    if len(logging_client_ip) == 0 or logging_client_ip[0] == '':
        print(f"Facade Service {config.FACADE_PORT}. There are currently no active Logging services. Please start the Logging service and try again.")
        raise config.InactiveService("Logging service is inactive.")

    client = get_grpc_client(logging_client_ip[0])
    try:
        response = client.LogMessage(logging_pb2.LogRequest(uid=uid, msg=msg))
        return response.status
    except grpc.RpcError as e:
        print(f"Facade Service {config.FACADE_PORT}. Retry failed with error: {e.details()}")
        raise e
    

def send_to_messages_service(msg: str) -> str:
    try:
        producer.send(config.MS_QUEUE_TOPIC_NAME, value={"message": msg})
        producer.flush(config.PRODUCER_FLUSH_TIMEOUT_S)
    except KafkaTimeoutError as e:
        return "Broker is unreachable. Message not sent to Messages service."
    return "OK"


@facade_service.post("/send-msg")
def send_message(request: MessageRequest):
    uid = str(uuid.uuid4())
    result_message = dict()
    try:
        status = send_to_logging_service(uid=uid, msg=request.message)
        result_message = {"uuid": uid, "logging service status": status}
    except RetryError as e:
        return {"error": "Retry Error"}
    except Exception as e:
        return {"error": str(e)}
    
    result_message["messages queue status"] = send_to_messages_service(msg=request.message)
    return result_message


@facade_service.get("/get-msg")    
def get_message():
    logging_client_ip: List[str] = get_ips_from_config_server(config.CONFIG_SERVER_LOGGING).split(" ")
    if len(logging_client_ip) == 0 or logging_client_ip[0] == '':
        print(f"Facade Service {config.FACADE_PORT}. There are currently no active Logging services. Please start the Logging service and try again.")
        return {"error": "Logging service is inactive"}

    client: logging_pb2_grpc.LoggingServiceStub = get_grpc_client(logging_client_ip[0])
    logs = client.GetLogs(logging_pb2.Empty()).messages

    messages_client_ip: List[str] = get_ips_from_config_server(config.CONFIG_SERVER_MESSAGES).split(" ")
    if len(messages_client_ip) == 0 or messages_client_ip[0] == '':
        print(f"Facade Service {config.FACADE_PORT}. There are currently no active Messages services. Please start the Messages service and try again.")
        return {"error": "Messages service is inactive"}

    response = requests.get(f"http://{messages_client_ip[0]}/messages")
    messages_response = response.text.replace('"', '')
    return {"logs": logs, "messages_service": messages_response}
