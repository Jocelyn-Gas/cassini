from pydantic import BaseModel


class Coordinates(BaseModel):
    longitude: float
    latitude: float
