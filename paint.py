import json
import sqlite3
from math import cos, radians
import sys

import matplotlib.pyplot as plt
from shapely.geometry import shape as makeShape

# matplotlib.style.use("fivethirtyeight")
# plt.rcParams["figure.constrained_layout.use"] = True
# plt.rcParams["lines.markersize"] = 6
plt.rcParams["figure.dpi"] = 400
colori = [
    ["#b2df8a", "#33a02c", "#195016"],
    ["#cab2d6", "#6a3d9a", "#351e4d"],
    ["#a6cee3", "#1f78b4", "#0f3c59"],
    ["#fdbf6f", "#b15928", "#582c14"],
    ["#fb9a99", "#e31a1c", "#710c0e"],
    ["#ffff99", "#df7f00", "#bb3f00"],
]

prov_col = {
  "TO": 0,
  "VC": 4,
  "NO": 0,
  "CN": 4,
  "AT": 3,
  "AL": 1,
  "BI": 3,
  "VB": 2,
  "AO": 1,
  "VA": 1,
  "CO": 4,
  "SO": 2,
  "MI": 3,
  "BG": 0,
  "BS": 4,
  "PV": 2,
  "CR": 2,
  "MN": 1,
  "LC": 3,
  "LO": 1,
  "MB": 2,
  "BZ": 1,
  "TN": 0,
  "VR": 3,
  "VI": 4,
  "BL": 2,
  "TV": 3,
  "VE": 4,
  "PD": 0,
  "RO": 2,
  "UD": 1,
  "GO": 4,
  "TS": 0,
  "PN": 0,
  "IM": 1,
  "SV": 0,
  "GE": 4,
  "SP": 2,
  "PC": 0,
  "PR": 3,
  "RE": 0,
  "MO": 3,
  "BO": 4,
  "FE": 0,
  "RA": 2,
  "FC": 1,
  "RN": 0,
  "MS": 4,
  "LU": 2,
  "PT": 1,
  "FI": 3,
  "LI": 2,
  "PI": 0,
  "AR": 4,
  "SI": 1,
  "GR": 4,
  "PO": 0,
  "PG": 0,
  "TR": 2,
  "PU": 2,
  "AN": 1,
  "MC": 3,
  "AP": 1,
  "FM": 4,
  "VT": 3,
  "RI": 4,
  "RM": 1,
  "LT": 3,
  "FR": 2,
  "AQ": 0,
  "TE": 3,
  "PE": 4,
  "CH": 1,
  "CB": 2,
  "IS": 3,
  "CE": 0,
  "BN": 1,
  "NA": 3,
  "AV": 4,
  "SA": 1,
  "FG": 0,
  "BA": 4,
  "TA": 1,
  "BR": 2,
  "LE": 3,
  "BT": 3,
  "PZ": 2,
  "MT": 0,
  "CS": 4,
  "CZ": 3,
  "RC": 1,
  "KR": 2,
  "VV": 2,
  "TP": 1,
  "PA": 3,
  "ME": 4,
  "AG": 0,
  "CL": 1,
  "EN": 2,
  "CT": 3,
  "RG": 0,
  "SR": 4,
  "SS": 1,
  "NU": 4,
  "CA": 3,
  "OR": 0,
  "SU": 2
}



def main():
    solid = not ("-c" in sys.argv)
    old = "-o" in sys.argv
    con = sqlite3.connect("./db.sqlite3")
    fig, ax = plt.subplots(figsize=(10, 10), constrained_layout=True)
    with open("./data/limits_IT_municipalities.geo.json", "r") as fo:
        geojson = json.load(fo)
    geocomuni = geojson["features"]
    geoprovincie = {}
    for geocomune in geocomuni:
        istat = geocomune["properties"]["com_istat_code"]
        curs = con.execute(
            """SELECT d.provincia, d.provincia=c.provincia, comune=d.id, c.provincia
            FROM matches
            LEFT JOIN comuni as c ON comune=c.id
            LEFT JOIN comuni as d ON capoluogo=d.id
            WHERE c.istat = ?
            """,
            (istat,),
        )
        prov = curs.fetchone()
        if not prov:
            print(f"Not found {istat}")
            continue
        cidx = 1
        if not solid and prov[2]:
            cidx = 2
        elif not solid and prov[1]:
            cidx = 0
        g_prov = prov[3] if old else prov[0]
        c = colori[prov_col[g_prov]][cidx]
        if geocomune["geometry"]["type"] == "Polygon":
            # Convert Polygon to MultiPolygon
            geocomune["geometry"]["coordinates"] = [geocomune["geometry"]["coordinates"]]
            geocomune["geometry"]["type"] = "MultiPolygon"
            #print(geocomune)
            #raise ValueError("TODO Polygon")
        for coordinates in geocomune["geometry"]["coordinates"]:
            x, y = zip(*coordinates[0])
            ax.fill(x, y, facecolor=c, edgecolor="none", linewidth=1)
        if g_prov in geoprovincie:
            geoprovincie[g_prov]["coordinates"].extend(geocomune["geometry"]["coordinates"])
        else:
            geoprovincie[g_prov] = geocomune["geometry"]
    for k, geoprovincia in geoprovincie.items():
        pshape = makeShape(geoprovincia)
        fontsize = 7
        if pshape.area < 0.2:
            fontsize = 6
        ax.annotate(k, (pshape.centroid.x - 0.1, pshape.centroid.y - 0.07), fontsize=fontsize)
    # distorzione per la proiezione di Mercatore
    ax.set_aspect(1 / cos(radians(42)))
    ax.axis("off")
    fig.savefig(f"./data/province-{'o' if old else 'n'}{'s' if solid else 'c'}.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
