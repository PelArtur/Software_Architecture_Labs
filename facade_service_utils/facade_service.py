import uuid
import grpc
import requests
import config
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from typing import List

import logging_service_utils.logging_pb2 as logging_pb2
import logging_service_utils.logging_pb2_grpc as logging_pb2_grpc
from consul_service_utils.consul_service import get_service_address, register_service, deregister_service, get_key_value
from kafka_utils.kafka_hf import create_producer, create_topic
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

facade_service = FastAPI()
service_port: int = 0
service_id: str = ""
producer: KafkaProducer = None


class MessageRequest(BaseModel):
    message: str
    

def get_grpc_client(host: str) -> logging_pb2_grpc.LoggingServiceStub:
    channel = grpc.insecure_channel(host)
    return logging_pb2_grpc.LoggingServiceStub(channel)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_to_logging_service(uid: str, msg: str) -> str:
    logging_client_ip: List[str] = get_service_address(config.SERVICE_NAME_LOGGING)
    if len(logging_client_ip) == 0 or logging_client_ip[0] == '':
        print(f"Facade Service {service_port}. There are currently no active Logging services. Please start the Logging service and try again.")
        raise config.InactiveService("Logging service is inactive.")

    client = get_grpc_client(logging_client_ip[0])
    try:
        response = client.LogMessage(logging_pb2.LogRequest(uid=uid, msg=msg))
        return response.status
    except grpc.RpcError as e:
        print(f"Facade Service {service_port}. Retry failed with error: {e.details()}")
        raise e
    

def send_to_messages_service(msg: str) -> str:
    try:
        ms_queue_config = get_key_value(config.MESSAGES_QUEUE_CONFIG_KEY)
        producer.send(ms_queue_config["topic_name"], value={"message": msg})
        producer.flush(ms_queue_config["flush_timeout_ms"])
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
    logging_client_ip: List[str] = get_service_address(config.SERVICE_NAME_LOGGING)
    if len(logging_client_ip) == 0 or logging_client_ip[0] == '':
        print(f"Facade Service {service_port}. There are currently no active Logging services. Please start the Logging service and try again.")
        return {"error": "Logging service is inactive"}

    client: logging_pb2_grpc.LoggingServiceStub = get_grpc_client(logging_client_ip[0])
    logs = client.GetLogs(logging_pb2.Empty()).messages

    messages_client_ip: List[str] = get_service_address(config.SERVICE_NAME_MESSAGES)
    if len(messages_client_ip) == 0 or messages_client_ip[0] == '':
        print(f"Facade Service {service_port}. There are currently no active Messages services. Please start the Messages service and try again.")
        return {"error": "Messages service is inactive"}

    response = requests.get(f"http://{messages_client_ip[0]}/messages")
    messages_response = response.text.replace('"', '')
    return {"logs": logs, "messages_service": messages_response}


@facade_service.on_event("shutdown")
def on_shutdown():
    deregister_service(service_id)


def serve(port: int):
    global service_port, service_id, producer
    service_port = port
    service_id = config.SERVICE_NAME_FACADE + "-" + str(port)
    ms_queue_config = get_key_value(config.MESSAGES_QUEUE_CONFIG_KEY)
    
    create_topic(
        topic_name=ms_queue_config["topic_name"], 
        brokers=ms_queue_config["bootstrap_servers"],
        partitions=ms_queue_config["partitions"], 
        replication_factor=ms_queue_config["replication_factor"]
    )
    register_service(
        service_name=config.SERVICE_NAME_FACADE,
        service_id=service_id,
        service_address=config.HOST,
        service_port=port
    )
    
    producer = create_producer(ms_queue_config["bootstrap_servers"])
    uvicorn.run(facade_service, host=config.HOST, port=service_port)
