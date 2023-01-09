import asyncio
import time
from typing import Iterable

import aiohttp

from cassini.models.route import Location, Route


async def get_coordinates(label: str, session: aiohttp.ClientSession)-> Location:
    async with session.get(url=f"https://api-search.mappy.net/search/1.1/find?q={label}&f=places&max_results=130&language=FRE&favorite_country=250&clientid=mappy&mid=928041933138&screensize=GE&abtest=NA&tagid=SPD_RESPONSE_SEARCH", headers={
                "apikey": "f2wjQp1eFdTe26YcAP3K92m7d9cV8x1Z",
                "referer": "https://fr.mappy.com/",
            }) as response:
        json_data = await response.json()
        raw_coordinates = json_data["addresses"]["features"][0]["geometry"]["geometries"][0]["coordinates"]
        return Location(longitude=raw_coordinates[0],latitude=raw_coordinates[1], label=label)



async def gather_coordinates(labels: Iterable[str]) -> list[Location]:
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get_coordinates(label, session) for label in labels])

    return ret

async def get_route(origin: Location, destination: Location, session: aiohttp.ClientSession):
    async with session.get(
        url=f"https://api-iti.mappy.net/multipath/7.0/routes?from={origin.longitude},{origin.latitude}&to={destination.longitude},{destination.latitude}&lang=fr_FR&providers=car&simplified=false&qid=348577cf-a377-4937-a0a1-da93672941b4&address_from=-&address_to=-&clientid=mappy&mid=876539520637&screensize=GE&abtest=NA&departure=true&vehicle=lt122",
        headers={
                "apikey": "f2wjQp1eFdTe26YcAP3K92m7d9cV8x1Z",
                "referer": "https://fr.mappy.com/",
            }) as response:
        json_data = await response.json()

        return Route(origin=origin,destination=destination,duration= json_data["routes"][0]["time"]["value"], length=round(json_data["routes"][0]["length"]["value"] / 1000, 2))

async def gather_routes(points: list[tuple[Location,Location]]) -> list[Route]:
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get_route(origin, destination, session) for origin, destination in points])

    return ret

