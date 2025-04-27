import config
from facade_service_utils.facade_service import serve


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else config.BASE_FACADE_PORT
    serve(port)

