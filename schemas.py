import pydantic


class PayloadSchema(pydantic.BaseModel):
    email: pydantic.EmailStr
    url: pydantic.HttpUrl
