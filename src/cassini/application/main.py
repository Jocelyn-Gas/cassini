import io
from datetime import timedelta
from io import BytesIO

import pandas
import requests
import streamlit

from cassini.models.route import Route
from cassini.readers.route import read_routes_from_csv, read_routes_from_excel


def compute_column_widths(dataframe: pandas.DataFrame, ratio: float = 1.25) -> list[float]:
    index_array = dataframe.index.astype(str)
    column_widths = [max((len(item) for item in index_array))]
    value_array = dataframe.values.astype(str)
    num_columns = value_array.shape[1]
    column_widths.extend(
        [max(len(item) for item in value_array[:, i]) for i in range(num_columns)]
    )
    label_widths = [0] + [len(label) for label in dataframe.columns]

    return [
        max(label_width, column_width) * ratio
        for label_width, column_width in zip(label_widths, column_widths)
    ]


def compute_row_heights(dataframe: pandas.DataFrame, ratio: float = 1.0) -> list[int]:
    row_heights = []
    for row in dataframe.itertuples():
        line_count = max(str(item).count("\n") for item in row)
        row_heights.append((line_count + 1) * 20 * ratio)
    return row_heights

def write_dataframes_to_buffer(
    dataframes: dict[str, pandas.DataFrame], startrows: dict[str, int]
) -> BytesIO:
    buffer = io.BytesIO()
    with pandas.ExcelWriter(
        buffer, engine="xlsxwriter"
    ) as writer:
        for sheet_name, dataframe in dataframes.items():
            dataframe.to_excel(writer, sheet_name, startrow=startrows[sheet_name])
            column_widths = compute_column_widths(dataframe)
            for column_index, column_width in enumerate(column_widths):
                writer.sheets[sheet_name].set_column(
                    column_index, column_index, column_width
                )
            row_heights = compute_row_heights(dataframe)
            for row_index, row_height in enumerate(row_heights):
                writer.sheets[sheet_name].set_row(row_index, row_height)

    return buffer

def set_decoration_color() -> None:
    streamlit.markdown(
        """
        <style>
        div[data-testid="stDecoration"] {
            background-image: linear-gradient(90deg, #1A2D75, #62AE2B);
        }

        header {
            background: none !important;
        }

        div[data-testid="stForm"] {
            padding: 2em;
        }
        .st-bk {
           border-bottom-width: 2px;
        }
        .st-bi {
           border-top-width: 2px;
        }
        .st-bj {
           border-right-width: 2px;
        }
        .st-bh {
           border-left-width: 2px;
        }

        button {
            border-width: 2px !important;
        }
        svg {
            color: #074A59;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


set_decoration_color()


def read_routes_from_file() -> None:
    file = streamlit.session_state.input_file
    if file is None:
        del streamlit.session_state.routes
        del streamlit.session_state.results
        return

    if file.name.endswith("csv"):

        streamlit.session_state.routes = read_routes_from_csv(file)
        return

    elif file.name.endswith("xls") or file.name.endswith("xlsx"):
        streamlit.session_state.raw_routes = pandas.read_excel(
            streamlit.session_state.input_file
        )
        streamlit.session_state.routes = read_routes_from_excel(file)
        return

    raise ValueError("Le format du fichier n'est pas le bon.")


def get_coordinates(label: str) -> tuple[float, float]:
    response = requests.get(
        f"https://api-search.mappy.net/search/1.1/find?q={label}&f=places&max_results=130&language=FRE&favorite_country=250&clientid=mappy&mid=928041933138&screensize=GE&abtest=NA&tagid=SPD_RESPONSE_SEARCH",
        headers={
            "apikey": "f2wjQp1eFdTe26YcAP3K92m7d9cV8x1Z",
            "referer": "https://fr.mappy.com/",
        },
    )

    return response.json()["addresses"]["features"][0]["geometry"]["geometries"][0][
        "coordinates"
    ]


def compute_route(
    origin_label: str, destination_label: str
) -> tuple[tuple[float, float], tuple[float, float], float]:
    origin = get_coordinates(origin_label)
    destination = get_coordinates(destination_label)
    request = requests.get(
        f"https://api-iti.mappy.net/multipath/7.0/routes?from={origin[0]},{origin[1]}&to={destination[0]},{destination[1]}&lang=fr_FR&providers=car&simplified=false&qid=348577cf-a377-4937-a0a1-da93672941b4&address_from=-&address_to=-&clientid=mappy&mid=876539520637&screensize=GE&abtest=NA&departure=true&vehicle=lt122",
        headers={
            "apikey": "f2wjQp1eFdTe26YcAP3K92m7d9cV8x1Z",
            "referer": "https://fr.mappy.com/",
        },
    )
    print(request.json()["routes"][0]["time"]["value"])
    return origin, destination, request.json()["routes"][0]["time"]["value"]


streamlit.title("Cassini")

streamlit.write(
    "Dans cette interface, vous pouvez calculer des durées de trajets en camion."
)
streamlit.file_uploader(
    "Trajets à calculer",
    ["csv", "xls", "xlsx"],
    accept_multiple_files=False,
    key="input_file",
    on_change=read_routes_from_file,
)

if "routes" in streamlit.session_state:
    if streamlit.button("Calculer les durées"):
        routes: list[Route] = streamlit.session_state.routes
        records = []
        if "results" not in streamlit.session_state:
            for route in routes:
                data = compute_route(route.origin, route.destination)
                records.append(
                    {
                        "Origine": route.origin,
                        "Destination": route.destination,
                        "Longitude origine": data[0][0],
                        "Latitude origine": data[0][1],
                        "Longitude destination": data[1][0],
                        "Latitude destination": data[1][1],
                        "Durée": str(timedelta(seconds=data[2])),
                    }
                )
            streamlit.session_state.results = pandas.DataFrame(records)

        streamlit.dataframe(streamlit.session_state.results, use_container_width=True)
        buffer = write_dataframes_to_buffer(
                    {"Resultats": streamlit.session_state.results},
                    {"Resultats": 0},
                )

        streamlit.download_button(
            "Télécharger le fichier",
            buffer,
            file_name=f"resultas.xlsx",
            mime="application/vnd.ms-excel",
        )
