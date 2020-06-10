import io

from starlette import status
from starlette.responses import StreamingResponse, UJSONResponse

import pydantic
import settings
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.routing import APIRouter
from handlers import StartAndStopEventHandler
from helpers import (
    get_broker_service,
    get_identifier,
    get_object_store_service,
)
from middlewares import AddIdentifierMiddleWare
from records import MessageRecord
from schemas import PayloadSchema
from services import BrokerService, ObjectNotFound, ObjectStoreService

router = APIRouter()


@router.post("/", response_class=UJSONResponse)
async def request_screenshot(
    response: UJSONResponse,
    payload: PayloadSchema = Body(..., embed=False),
    broker_service: BrokerService = Depends(get_broker_service),
    identifier: pydantic.UUID4 = Depends(get_identifier),
):
    message = MessageRecord(identifier=identifier, email=payload.email, url=payload.url)

    await broker_service.emit(message.dumps())
    response.headers["X-Identifier"] = str(message.identifier)
    return {"message": "🐍 is pretty cool!"}


@router.get("/{identifier}.png")
async def get_screenshot(
    identifier: str,
    object_store_service: ObjectStoreService = Depends(get_object_store_service),
):
    try:
        data = await object_store_service.fetch_image(f"{identifier}.png")
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
