import io

from starlette.responses import StreamingResponse, UJSONResponse

import pydantic
from common import settings
from common.records import MessageRecord
from common.services import BrokerService, ObjectNotFound, ObjectStoreService
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.routing import APIRouter
from producer_src.handlers import StartAndStopEventHandler
from producer_src.helpers import (
    get_broker_service,
    get_identifier,
    get_object_store_service,
)
from producer_src.middlewares import AddIdentifierMiddleWare
from producer_src.schemas import PayloadSchema

router = APIRouter()


def get_message(
    identifier: pydantic.UUID4 = Depends(get_identifier),
    payload: PayloadSchema = Body(..., embed=False),
) -> MessageRecord:
    return MessageRecord(identifier=identifier, email=payload.email, url=payload.url)


@router.post("/", response_class=UJSONResponse, status_code=status.HTTP_201_CREATED)
async def request_screenshot(
    response: UJSONResponse,
    broker_service: BrokerService = Depends(get_broker_service),
    message: MessageRecord = Depends(get_message),
):
    await broker_service.emit(message.dumps())
    response.headers["X-Identifier"] = str(message.identifier)
    return {"message": "🐍 is pretty cool!"}


@router.get("/{identifier}.png")
async def get_screenshot(
    identifier: str,
    object_store_service: ObjectStoreService = Depends(get_object_store_service),
):
    try:
        data = await object_store_service.fetch_object(f"{identifier}.png")
        document = io.BytesIO(data)
        return StreamingResponse(document, media_type="image/png")
    except ObjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.DEBUG)
    app.include_router(router)

    handler = StartAndStopEventHandler(app)
    app.add_event_handler("startup", handler.on_startup)
    app.add_event_handler("shutdown", handler.on_shutdown)
    app.add_middleware(AddIdentifierMiddleWare)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
