import csv
import json
import sqlite3
from collections import namedtuple

import pyproj
from shapely.geometry import shape as makeShape
from shapely.ops import transform

Prov = namedtuple("Prov", ["id", "nome", "sig"])


def get_capoluoghi(con: sqlite3.Connection) -> dict[str, dict]:
    capoluoghi = {}
    for row in con.execute(
        "select comuni.id, nome, provincia from capoluoghi left join comuni on capoluoghi.id=comuni.id;"
    ):
        capoluoghi[row[2]] = {
            "id": Prov(*row),
            "area": 0,
            "num": 0,
            "nplus": 0,
            "nminus": 0,
            "aplus": 0,
            "aminus": 0,
            "lminus": [],
            "lplus": [],
        }
    return capoluoghi


def main():
    con = sqlite3.connect("./db.sqlite3")
    capoluoghi = get_capoluoghi(con)
    wgs84 = pyproj.CRS("EPSG:4326")
    itproj = pyproj.CRS("EPSG:6875")
    project = pyproj.Transformer.from_crs(wgs84, itproj, always_xy=True).transform
    with open("./data/_limits_IT_municipalities.geo.json", "r") as fo:
        geojson = json.load(fo)
    for geocomune in geojson["features"]:
        istat = geocomune["properties"]["com_istat_code"]
        rows = con.execute(
            """SELECT d.provincia, c.provincia, c.nome
            FROM matches
            LEFT JOIN comuni as c ON comune=c.id
            LEFT JOIN comuni as d ON capoluogo=d.id
            WHERE c.istat = ?
            """,
            (istat,),
        ).fetchall()
        if not rows:
            print(f"Non trovato {istat}")
            continue
        if len(rows) > 1:
            print(f"Troppi {istat}")
            continue
        area = transform(project, makeShape(geocomune["geometry"])).area
        data = rows[0]
        capoluoghi[data[1]]["area"] += area
        capoluoghi[data[1]]["num"] += 1
        if data[0] != data[1]:
            capoluoghi[data[1]]["aminus"] += area
            capoluoghi[data[1]]["nminus"] += 1
            capoluoghi[data[1]]["lminus"].append(data[2])
            capoluoghi[data[0]]["aplus"] += area
            capoluoghi[data[0]]["nplus"] += 1
            capoluoghi[data[0]]["lplus"].append(data[2])
    with open("data/stats.csv", mode="w", encoding="utf8", newline="") as csvfile:
        cwriter = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        cwriter.writerow(
            (
                "PROV",
                "NOME",
                "Area",
                "Numero comuni",
                "Area guadagnata",
                "Area persa",
                "N Comuni guadagnati",
                "N Comuni persi",
                "Elenco comuni guadagnati",
                "Elenco comuni persi",
            )
        )
        for row in capoluoghi.values():
            cwriter.writerow(
                (
                    row["id"].sig,
                    row["id"].nome,
                    str(row["area"] / 1000 / 1000).replace(".", ","),
                    row["num"],
                    str(row["aplus"] / 1000 / 1000).replace(".", ","),
                    str(row["aminus"] / 1000 / 1000).replace(".", ","),
                    row["nplus"],
                    row["nminus"],
                    ", ".join(row["lplus"]),
                    ", ".join(row["lminus"]),
                )
            )


if __name__ == "__main__":
    main()
