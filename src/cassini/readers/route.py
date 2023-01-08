from io import BytesIO

import pandas

from cassini.models.route import Route


def read_routes_from_csv(file: str | BytesIO) -> list[Route]:
    return [
        Route(origin=record["Origine"], destination=record["Destination"])
        for _, record in pandas.read_csv(
            file, usecols=["Origine", "Destination"], dtype=str
        ).iterrows()
    ]

def read_routes_from_excel(file: str | BytesIO) -> list[Route]:
    return [
        Route(origin=record["Origine"], destination=record["Destination"])
        for _, record in pandas.read_excel(
            file, usecols=["Origine", "Destination"], dtype=str
        ).iterrows()
    ]
