import sqlite3
from collections import namedtuple
import os
from time import sleep
import requests
import json

API_KEY = os.getenv("GEOAPIFY_KEY")

Citta = namedtuple("Citta", ["id", "coords"])


def route(comune: Citta, capoluogo: list[float], mode="drive") -> tuple[float, str]:
    url = "https://api.geoapify.com/v1/routing"
    data = {
        "waypoints": f"{comune.coords[0]},{comune.coords[1]}|{capoluogo[0]},{capoluogo[1]}",
        "mode": mode,
        "apiKey": API_KEY,
    }
    response = requests.get(url, params=data).json()
    try:
        response["features"][0]
    except KeyError:
        print(comune.coords, capoluogo, response)
        raise ValueError("API Error")
    print(comune.coords, capoluogo, response["features"][0]["properties"]["distance"])
    sleep(1 / 5)  # Up to 5 requests/second
    return response["features"][0]["properties"]["distance"], json.dumps(response)


def get_capoluoghi(con: sqlite3.Connection) -> dict[int, list[float]]:
    id_capoluoghi = [row[0] for row in con.execute("select id from capoluoghi").fetchall()]
    capoluoghi = {}
    for id in id_capoluoghi:
        coords = con.execute("select lat, long from coords where id = ?", [id]).fetchone()
        if not coords:
            print(f"Coords not found for {id}")
        capoluoghi[id] = coords
    return capoluoghi


def main():
    con = sqlite3.connect("db.sqlite3")
    capoluoghi = get_capoluoghi(con)
    for row in con.execute(
        """select comune, lat, long, capoluogo
        from distances
        join coords on coords.id=distances.comune
        where walk is null"""
    ):
        comune = Citta(row[0], row[1:3])
        capoluogo = capoluoghi[row[3]]
        r, j = route(comune, capoluogo, "walk")
        con.execute(
            "UPDATE distances SET walk=?, walk_rsp=? WHERE comune = ? AND capoluogo=?",
            (r, j, row[0], row[3]),
        )
        con.commit()


if __name__ == "__main__":
    main()
