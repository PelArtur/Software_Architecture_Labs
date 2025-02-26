from threading import Thread
from hazelcast import HazelcastClient

from typing import List
from hazelcast.proxy.queue import BlockingQueue


def get_elements_from_queue(client_id: int, queue: BlockingQueue):
    while True:
        value: int = queue.take()
        if value == -1:
            break
        
        print(f"Consumer {client_id} received: {value}")
        

if __name__ == "__main__":
    cluster_name: str = "dev"
    queue_name:   str = "bounded_queue"
    key:          str = "key"

    print("Connection...")
    client1 = HazelcastClient(cluster_name=cluster_name)
    print("Client 1 connected")
    client2 = HazelcastClient(cluster_name=cluster_name)
    print("Client 2 connected\n")
    
    queues = [
        client1.get_queue(queue_name).blocking(),
        client2.get_queue(queue_name).blocking(),
    ]

    threads: List[Thread] = []
    for i in range(len(queues)):
        thread = Thread(target=get_elements_from_queue, args=(i + 1, queues[i]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\nDisconnection...")
    client1.shutdown()
    print("Client 1 disconnected")
    client2.shutdown()
    print("Client 2 disconnected")
    print("Done!")
    