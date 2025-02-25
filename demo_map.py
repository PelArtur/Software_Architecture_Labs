import hazelcast

if __name__ == "__main__":
    print("Connection...")
    client = hazelcast.HazelcastClient(
        cluster_name="dev", 
    ) 

    map = client.get_map("my-distributed-map").blocking() 

    print("Add data...")
    data = {i: i for i in range(1000)}
    map.put_all(data)

    client.shutdown()
    print("Done!")
