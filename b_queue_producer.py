from hazelcast import HazelcastClient
from hazelcast.proxy.queue import BlockingQueue

def add_elements_to_queue(queue: BlockingQueue, n: int, consumers: int):
    for i in range(1, n + 1):
        queue.put(i)
        print(f"Push: {i}")
    
    for i in range(consumers):
        queue.put(-1)


if __name__ == "__main__":
    cluster_name: str = "dev"
    queue_name:   str = "bounded_queue"

    consumers: int = 2
    n:         int = 100
    
    print("Connection...")
    client = HazelcastClient(cluster_name=cluster_name)
    print("Producer connected!\n")
    
    queue = client.get_queue(queue_name).blocking()
    add_elements_to_queue(queue, n, consumers)
    
    print("\nDisconnection...")
    client.shutdown()
    print("Producer disconnected!")
    