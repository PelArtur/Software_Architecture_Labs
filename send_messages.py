import requests
import config
import sys
import time

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    endpoint = f"http://{config.HOST}:{config.BASE_FACADE_PORT}/send-msg"
    print(f"Sending {n} messages...")

    for i in range(1, n + 1):
        requests.post(endpoint, json={"message": f"msg{i}"})
        time.sleep(0.01)
    print("Done!")
