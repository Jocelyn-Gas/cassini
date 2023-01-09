from pydantic import BaseModel


class Location(BaseModel):
    longitude: float
    latitude: float
    label: str


class Route(BaseModel):
    origin: Location
    destination: Location
    duration: float
    length: float
