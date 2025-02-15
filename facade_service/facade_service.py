import uuid
import grpc
import requests
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed

import logging_service.logging_pb2 as logging_pb2
import logging_service.logging_pb2_grpc as logging_pb2_grpc

LOGGING_SERVICE_HOST = "localhost:50051"
MESSAGES_SERVICE_URL = "http://localhost:8001/messages"


facade_service = FastAPI()


class MessageRequest(BaseModel):
    message: str
    

def get_grpc_client() -> logging_pb2_grpc.LoggingServiceStub:
    channel = grpc.insecure_channel(LOGGING_SERVICE_HOST)
    return logging_pb2_grpc.LoggingServiceStub(channel)


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
def send_to_logging_service(uid: str, msg: str) -> str:
    client = get_grpc_client()
    response = client.LogMessage(logging_pb2.LogRequest(uid=uid, msg=msg))
    return response.status


@facade_service.post("/send-msg")
def send_message(request: MessageRequest):
    uid = str(uuid.uuid4())
    try:
        status = send_to_logging_service(uid=uid, msg=request.message)
        return {"uuid": uid, "status": status}
    except Exception as e:
        return {"error": str(e)}


@facade_service.get("/get-msg")    
def get_message():
    client: logging_pb2_grpc.LoggingServiceStub = get_grpc_client()
    logs = client.GetLogs(logging_pb2.Empty()).messages

    response = requests.get(MESSAGES_SERVICE_URL)
    messages_response = response.text
    return {"logs": logs, "messages_service": messages_response}
