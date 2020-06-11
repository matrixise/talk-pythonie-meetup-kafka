import typing

import faust

from common import settings
from common.services import ObjectStoreService


class ConsumerApp(faust.App):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.object_store_service = self.service(
            ObjectStoreService(  # type:ignore   # noqa
                server_url=settings.OBJECT_STORE_URL,
                access_key=settings.OBJECT_STORE_ACCESS_KEY,
                secret_key=settings.OBJECT_STORE_SECRET_KEY,
                bucket_name=settings.OBJECT_STORE_BUCKET_NAME,
            )
        )


def create_app():
    return ConsumerApp(settings.CONSUMER_GROUP_ID, autodiscover=["consumer_src.agents"])
