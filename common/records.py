import uuid

import faust


class MessageRecord(faust.Record, serializer="json", namespace="MessageRecord"):
    identifier: uuid.UUID
    email: str
    url: str
