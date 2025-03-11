from fastapi import FastAPI

message_service = FastAPI()

@message_service.get("/messages")
def send_message():
    return "Come back here later"