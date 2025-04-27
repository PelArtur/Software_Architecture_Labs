import consul
import random
from typing import List

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