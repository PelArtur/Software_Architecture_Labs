import config
import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, InvalidReplicationFactorError
from typing import List


def get_available_brokers(all_brockers: List[str]) -> List[str]:
    available_brokers = []
    for broker in all_brockers:
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=broker)
            available_brokers.append(broker)
            admin_client.close()
        except Exception as e:
            continue
    return available_brokers


def create_topic(topic_name: str, partitions: int = 1, replication_factor: int = 1) -> None:
    brokers = get_available_brokers(config.BOOTSTRAP_SERVERS)
    if len(brokers) == 0:
        print("No available brokers found. Please check your Kafka cluster.")
        return
    
    admin_client = KafkaAdminClient(bootstrap_servers=brokers)
    try:
        topic = NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)
        admin_client.create_topics([topic])
    except TopicAlreadyExistsError as e:
        print(f"Topic {topic_name} already exists.")
    except InvalidReplicationFactorError as e:
        print(f"Invalid replication factor. Replication factor: {replication_factor}, number of brokers: {len(brokers)}.")
    admin_client.close()


def create_producer(brokers: List[str] = []) -> KafkaProducer:
    if len(brokers) == 0:
        brokers = get_available_brokers(config.BOOTSTRAP_SERVERS)
    return KafkaProducer(bootstrap_servers=brokers, 
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    

def create_consumer(topic: str, brokers: List[str] = [], group_id: str = "mq-group") -> KafkaConsumer:
    if len(brokers) == 0:
        brokers = get_available_brokers(config.BOOTSTRAP_SERVERS)
    return KafkaConsumer(
        topic,
        bootstrap_servers=brokers,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )