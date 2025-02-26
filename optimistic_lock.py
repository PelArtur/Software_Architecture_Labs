import time
from threading import Thread
from hazelcast import HazelcastClient

from typing import List
from hazelcast.proxy.map import BlockingMap


def increment_map_value(distributed_map: BlockingMap, key: str, iterations: int):
    for _ in range(iterations):
        while True:
            value = distributed_map.get(key)
            if distributed_map.replace_if_same(key, value, value + 1):
                break


if __name__ == "__main__":
    cluster_name: str = "dev"
    map_name:     str = "distributed-optimistic-lock-map"
    key:          str = "key"

    iterations: int = 10000
    
    print("Connection...")
    client = HazelcastClient(cluster_name=cluster_name)
    distributed_map = client.get_map(map_name).blocking()
    distributed_map.put_if_absent(key, 0)
    client.shutdown()
    
    client1 = HazelcastClient(cluster_name=cluster_name)
    print("Client 1 connected")
    client2 = HazelcastClient(cluster_name=cluster_name)
    print("Client 2 connected")
    client3 = HazelcastClient(cluster_name=cluster_name)
    print("Client 3 connected")
    
    distributed_maps = [
        client1.get_map(map_name).blocking(),
        client2.get_map(map_name).blocking(),
        client3.get_map(map_name).blocking()
    ]

    threads: List[Thread] = []
    #------------------------------------------------#
    start_time = time.time()
    for dist_map in distributed_maps:
        thread = Thread(target=increment_map_value, args=(dist_map, key, iterations))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    end_time = time.time()
    #------------------------------------------------#

    print("\nDisconnection...")
    client1.shutdown()
    print("Client 1 disconnected")
    client2.shutdown()
    print("Client 2 disconnected")
    client3.shutdown()
    print("Client 3 disconnected")

    client = HazelcastClient(cluster_name=cluster_name)
    distributed_map = client.get_map(map_name).blocking()
    final_value = distributed_map.get(key)
    print(f"\nFinal value: {final_value}")
    print(f"Time taken: {end_time - start_time} seconds")
    client.shutdown()
    print("Done!")
    