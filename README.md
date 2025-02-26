# Hazelcast

Author: Artur Pelcharskyi

## Getting Started

The laboratory work was performed and tested on the following configuration:

- **OS**: Windows 11
- **Python**: 3.10.0
- **Hazelcast**: 5.3.0
- **Hazelcast Management Center**: 5.3.0


Before running the Python scripts, install all required libraries:
```
pip install -r requirements.txt
```

## Tasks
### **1. Installing and configuring Hazelcast**
This lab utilizes Hazelcast 5.3.0 and Hazelcast Management Center 5.3.0 running in Docker. Below are the installed images:

![alttext](images/image1.png)


### **2. Starting a cluster of three nodes**

**Creating new Docker Network command**
```
docker network create hazelcast-network
```

**Starting new nodes of cluster named `dev` commands:**
- node1
    ```
    docker run -it --name hz-node1 --network hazelcast-network --rm -e HZ_NETWORK_PUBLICADDRESS=172.18.0.1:5701 -e HZ_CLUSTERNAME=dev -p 5701:5701 hazelcast/hazelcast:5.3.0
    ```
- node2
    ```
    docker run -it --name hz-node2 --network hazelcast-network --rm -e HZ_NETWORK_PUBLICADDRESS=172.18.0.1:5702 -e HZ_CLUSTERNAME=dev -p 5702:5701 hazelcast/hazelcast:5.3.0
    ```
- node3 
    ```
    docker run -it --name hz-node3 --network hazelcast-network --rm -e HZ_NETWORK_PUBLICADDRESS=172.18.0.1:5703 -e HZ_CLUSTERNAME=dev -p 5703:5701 hazelcast/hazelcast:5.3.0
    ```


**Hazelcast Management Center**

```
docker run -d -p 8080:8080 --name hz-mancenter --network hazelcast-network -e HZ_CLUSTERNAME=dev hazelcast/management-center:5.3.0
```

From the `hz-node3` terminal, you can see that the three-node cluster has been successfully created.

![alttext](images/image2.png)

The same result is reflected in the Management Center:

![alttext](images/image3.png)


### **3. Distributed Map**

By running the `demo_map.py` script, 1000 new entries will be added to the system simultaneously. In the Management Center, we will observe the following resource distribution:

![alttext](images/image4.png)

We can see that the entries were divided approximately equally among the nodes. However, the data was recorded(Puts) through a single node because the operation was performed as one batch rather than multiple individual operations.

#### **3a. Disabling of one node**

Let’s check the distribution after disabling `hz-node3`:

![alttext](images/image5.png)

As we can see, the data has now been redistributed between `hz-node1` and `hz-node2`, with no data loss occurring.

#### **3b. Disabling of two nodes sequentially**

Now, let’s disable `hz-node2` after having previously disabled `hz-node3` in the earlier experiment:

![alttext](images/image6.png)

Once again, no data loss occurred, and all entries are now stored in `hz-node1`.

#### **3c. Disabling of two nodes simultaneously**

After disabling `hz-node2` and `hz-node3` simultaneously:

![alttext](images/image7.png)

This time, some data was lost. It is likely that all the lost data was stored on one of the disabled nodes, as replication was only able to preserve the data from one node on `hz-node1`.

#### **3d. How to prevent data loss?**
To prevent data loss in Hazelcast, you can adjust certain settings of the data structures. One option is to modify the number of backups. In the `config/hazelcast.xml` file, you can change the following value:

```xml
<hazelcast>
    <map name="my-distributed-map">
        <backup-count>1</backup-count>
    </map>
</hazelcast>
```

When using 3 nodes, as in our case, this value should be set to 2. Since the default value was 1, the backup for `hz-node2` was stored on `hz-node1`, and the backup for `hz-node3` was stored on `hz-node2`. As a result, the data from `hz-node3` was lost because both the node itself and its backup node(`hz-node2`) were disabled. However, the data from `hz-node2` was preserved on `hz-node1`. By setting the number of backups to 2, each node would have backups on the other two nodes, ensuring that all data could be preserved on `hz-node1` even in such a scenario.


### **4. Distributed Map without locks**

Using `no_lock.py`, three clients are launched. Each client retrieves the value of the key "key", increments it by 1, and writes the result back. There are 3 such clients, and each performs 10,000 iterations. After execution, the following results were obtained:

![alttext](images/image8.png)

Also, in the Management Center:

![alttext](images/image9.png)

We observe that the final value is 13188, despite the expected value of 30000. At the same time, we can see that 30000 operations were performed:

![alttext](images/image10.png)

During this experiment, a classic multi-threaded/multi-process error occurred — a data race. This happens when one client reads the value before another client writes it back, causing the current client to overwrite the previous result with its own.


### **5-7. Distributed Map with locks**

Pessimistic and optimistic locking are implemented in `pessimistic_lock.py` and `optimistic_lock.py`, respectively. Both scripts run 3 threads with different clients, performing the same operations as in `no_lock.py`. Let’s examine the final value of the "key" key for both methods, as well as their execution times:

![alttext](images/image11.png)

So, we can observe that this time there was no data loss, and both methods produced the correct result of 30000. It is also evident that pessimistic locking performs slower than optimistic locking. On the other hand, pessimistic locking requires fewer accesses to the map compared to optimistic locking:

- distributed-pessimistic-lock-map
    ![alttext](images/image12.png)
- distributed-optimistic-lock-map
    ![alttext](images/image13.png)

Finally, to confirm the results in terms of execution time, let’s run both scripts again:

![alttext](images/image14.png)


### **8. Bounded queue**

In `b_queue_producer.py`, a script is implemented to run a client that adds values to the bounded queue, while `b_queue_consumer.py` runs two clients that retrieve values from the queue. Since the queue has a maximum capacity of 10 elements, the following configuration should be added to `hazelcast.xml`:

```xml
<queue name="bounded_queue">
        <max-size>10</max-size>
</queue>
```

The node will then be restarted to apply the changes:
```
docker run -it --name hz-node1 --network hazelcast-network --rm -v "${PWD}/hazelcast.xml:/opt/hazelcast/hazelcast.xml" -e HAZELCAST_CONFIG=hazelcast.xml -e HZ_NETWORK_PUBLICADDRESS=172.18.0.1:5701 -e HZ_CLUSTERNAME=dev -p 5701:5701 hazelcast/hazelcast:5.3.0
```

Now, we can run both scripts in two different terminals and observe the following result:

![alttext](images/image15.png)

The producer sequentially adds values to the queue, and the consumers sequentially retrieve them in the same order. Additionally, the consumers follow an alternating pattern: the i-th element is taken by Consumer 1, the (i + 1)-th by Consumer 2, the (i + 2)-th by Consumer 1, and so on.

Now, let’s run only the producer script to verify that the queue size is limited to 10:

![alttext](images/image16.png)

We can see that the producer added numbers from 1 to 10 and then blocked, waiting for the queue size to decrease below 10. This confirms that the queue configuration was applied successfully.
