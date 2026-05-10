from pydantic import BaseModel, Field


class AdvertisementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    owner: str = Field(min_length=1, max_length=100)


class AdvertisementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    owner: str | None = Field(default=None, min_length=1, max_length=100)
