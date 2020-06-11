from common import settings
from common.services import BrokerService, ObjectStoreService
from fastapi import FastAPI


class StartAndStopEventHandler:
    def __init__(self, app: FastAPI):
        self.app = app

    async def on_startup(self):
        self.app.state.broker_service = BrokerService(brokers=settings.KAFKA_BROKERS)
        await self.app.state.broker_service.start()

        self.app.state.object_store_service = ObjectStoreService(
            server_url=settings.OBJECT_STORE_URL,
            access_key=settings.OBJECT_STORE_ACCESS_KEY,
            secret_key=settings.OBJECT_STORE_SECRET_KEY,
            bucket_name=settings.OBJECT_STORE_BUCKET_NAME,
        )

        await self.app.state.object_store_service.start()

    async def on_shutdown(self):
        await self.app.state.broker_service.stop()
