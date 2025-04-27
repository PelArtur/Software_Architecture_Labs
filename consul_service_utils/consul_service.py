import consul
import random
import json
from typing import List, Dict

def register_service(service_name: str, service_id: str, service_address: str, service_port: int) -> None:
    client = consul.Consul()
    client.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=service_address,
        port=service_port
    )
    print(f"Service {service_name} registered with ID {service_id}.")
    
    
def deregister_service(service_id: str) -> None:
    client = consul.Consul()
    client.agent.service.deregister(service_id)
    print(f"Service with ID {service_id} deregistered.")


def get_service_address(service_name: str) -> List[str]:
    client = consul.Consul()
    services = client.health.service(service_name, passing=True)[1]
    if not services:
        return []

    service_ips: List[str] = []
    for service in services:
        serv = service['Service']  
        service_ips.append(f"{serv['Address']}:{serv['Port']}")

    random.shuffle(service_ips)
    return service_ips


def add_key_value(key: str, value: str) -> None:
    client = consul.Consul()
    client.kv.put(key, value)


def get_key_value(key: str) -> Dict:
    client = consul.Consul()
    _, data = client.kv.get(key)
    if data is None:
        return None

    data = data['Value'].decode('utf-8')
    return json.loads(data)
