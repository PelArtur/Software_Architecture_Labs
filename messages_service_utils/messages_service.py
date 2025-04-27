import config
import uvicorn
from fastapi import FastAPI
from threading import Thread
from kafka_utils.kafka_hf import create_consumer
from consul_service_utils.consul_service import register_service, deregister_service
from typing import List

message_service = FastAPI()
messages: List[str] = []
service_port: int = 0
service_id: str = ""
consuming: bool = True

def consume_messages():
    consumer = create_consumer(topic=config.MS_QUEUE_TOPIC_NAME, group_id=config.MS_QUEUE_CONSUMER_GROUP)
    while consuming:
        records = consumer.poll(timeout_ms=config.CONSUMER_POLL_TIMEOUT_MS)
        for key in records:
            for message in records[key]:
                messages.append(message.value["message"])
                print(f"Messages Service {service_port}. Received message: {message.value['message']}")


@message_service.get("/messages")
def send_message():
    return messages


@message_service.on_event("shutdown")
def on_shutdown():
    global consuming
    print(f"Messages Service {service_port}. Cleaning up MessagesService {service_port}...")
    deregister_service(service_id)
    consuming = False
    print("Done!")


def serve(port: int):
    global service_port, service_id
    service_port = port
    service_id = config.SERVICE_NAME_MESSAGES + "-" + str(service_port)
    Thread(target=consume_messages, daemon=True).start()
    register_service(
        service_name=config.SERVICE_NAME_MESSAGES,
        service_id=service_id,
        service_address=config.HOST,
        service_port=service_port
    )
    uvicorn.run(message_service, host=config.HOST, port=service_port)
