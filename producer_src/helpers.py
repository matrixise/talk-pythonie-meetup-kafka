from starlette.requests import Request

import pydantic


def get_identifier(request: Request) -> pydantic.UUID4:
    return request.state.identifier


def get_broker_service(request: Request):
    return request.app.state.broker_service


def get_object_store_service(request: Request):
    return request.app.state.object_store_service
