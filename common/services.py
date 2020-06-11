import asyncio
import io
import typing
from functools import cached_property

import mode
from mode import get_logger
from mode.utils.types.trees import NodeT

import minio  # type: ignore
from aiokafka import AIOKafkaProducer  # type: ignore

logger = get_logger(__name__)


class BrokerService(mode.Service):
    def __init__(
        self,
        *,
        brokers: typing.Optional[typing.List[str]] = None,
        beacon: NodeT = None,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        self.brokers = brokers
        super().__init__(beacon=beacon, loop=loop)

    @cached_property
    def producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            loop=self.loop, bootstrap_servers=self.brokers, retry_backoff_ms=1000
        )

    async def on_start(self) -> None:
        self.log.info("Connect the producer")
        await self.producer.start()

    async def on_shutdown(self):
        self.log.info("Disconnect the producer")
        await self.producer.stop()

    async def emit(self, message: bytes):
        self.log.info("Emit message")
        await self.producer.send(topic="messages", value=message)
        self.log.info("message emitted")


class ObjectNotFound(Exception):
    pass


class ObjectStoreService(mode.Service):
    def __init__(
        self,
        *,
        server_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        beacon: NodeT = None,
        loop: asyncio.AbstractEventLoop = None,
    ):
        self.server_url = server_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name

        super().__init__(beacon=beacon, loop=loop)

    @cached_property
    def client(self):
        return minio.Minio(
            endpoint=self.server_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

    async def bucket_exists(self):
        return await self.loop.run_in_executor(
            None, self.client.bucket_exists, self.bucket_name
        )

    async def make_bucket(self):
        return await self.loop.run_in_executor(
            None, self.client.make_bucket, self.bucket_name
        )

    async def on_start(self) -> None:
        exists = await self.bucket_exists()
        if not exists:
            await self.make_bucket()

    async def store_object(self, object_name: str, content: bytes):
        return await self.loop.run_in_executor(
            None,
            self.client.put_object,
            self.bucket_name,
            object_name,
            io.BytesIO(content),
            len(content),
        )

    async def fetch_object(self, object_name: str):
        try:
            response = await self.loop.run_in_executor(
                None, self.client.get_object, self.bucket_name, object_name
            )
            return response.data
        except Exception:
            raise ObjectNotFound()
