from hazelcast import HazelcastClient


if __name__ == "__main__":
    print("Connection...")
    client = HazelcastClient(
        cluster_name="dev", 
    ) 

    map = client.get_map("my-distributed-map").blocking() 

    print("Add data...")
    data = {i: i for i in range(1000)}
    map.put_all(data)

    print("\nReceiving data...")
    for key, value in map.entry_set():
        print(f"{key}: {value}")
    client.shutdown()
    print("Done!")
