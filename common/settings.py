from decouple import Csv, config  # type: ignore

DEBUG = config("DEBUG", cast=bool, default=False)
CONSUMER_GROUP_ID = config("CONSUMER_GROUP_ID", cast=str, default="consumer-1")
KAFKA_BROKERS = config("KAFKA_BROKERS", cast=Csv(), default="localhost")
OBJECT_STORE_URL = config("OBJECT_STORE_URL", cast=str, default="localhost:9000")

# openssl rand -hex 16
OBJECT_STORE_ACCESS_KEY = config(
    "OBJECT_STORE_ACCESS_KEY", cast=str, default="d1acb4f6d6c29c9971dcfb56"
)

# openssl rand -hex 32
OBJECT_STORE_SECRET_KEY = config(
    "OBJECT_STORE_SECRET_KEY",
    cast=str,
    default="b934f0aa93e3e7427912b4f0b78bfdbce43b5786e9200bf7",
)
OBJECT_STORE_BUCKET_NAME = config(
    "OBJECT_STORE_BUCKET_NAME", cast=str, default="screenshots"
)

BASE_PORT = config("BASE_PORT", cast=int, default=8001)
BASE_URL = config("BASE_URL", cast=str, default=f"http://localhost:{BASE_PORT}/")
