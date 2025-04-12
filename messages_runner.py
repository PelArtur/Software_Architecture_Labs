import config
from messages_service_utils.messages_service import serve


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else config.BASE_MESSAGING_PORT
    serve(port)

