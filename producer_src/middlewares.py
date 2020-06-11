import uuid

from starlette.middleware.base import BaseHTTPMiddleware


class AddIdentifierMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.identifier = uuid.uuid4()
        return await call_next(request)
