from multiprocessing import Process
from typing import List
from hazelcast import HazelcastClient

def increment_map_value(client_id: int, map_name: str, key: str, iterations: int):
    client = HazelcastClient(cluster_name="dev")
    print(f"Client {client_id} connected")
    distributed_map = client.get_map(map_name).blocking()

    for _ in range(iterations):
        value = distributed_map.get(key)
        value += 1
        distributed_map.put(key, value)

    client.shutdown()
    print(f"Client {client_id} disconnected")


if __name__ == "__main__":
    cluster_name: str = "dev"
    map_name:     str = "distributed-no-lock-map"
    key:          str = "key"

    iterations: int = 10000
    clients:    int = 3
    
    print("Connection...")
    client = HazelcastClient(cluster_name=cluster_name)
    distributed_map = client.get_map(map_name).blocking()
    distributed_map.put_if_absent(key, 0)
    client.shutdown()

    processes: List[Process] = []
    for i in range(clients):
        process = Process(target=increment_map_value, args=(f"{i + 1}", map_name, key, iterations))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    client = HazelcastClient(cluster_name=cluster_name)
    distributed_map = client.get_map(map_name).blocking()
    final_value = distributed_map.get(key)
    print(f"Final value: {final_value}")
    client.shutdown()
    print("Done!")
    