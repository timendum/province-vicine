import sqlite3
import json


def main():
    con = sqlite3.connect("./db.sqlite3")
    with open("./data/limits_IT_municipalities.topo.json", mode="r", encoding="utf8") as jfile:
        topofile = json.load(jfile)
    for comune in topofile["objects"]["comuni"]["geometries"]:
        istat = comune["properties"]["com_istat_code"]
        rows = con.execute(
            """SELECT d.provincia, d.provincia=c.provincia, comune=d.id, comune, capoluogo
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
        comune["properties"] = {
            "n": comune["properties"]['name'],
            "op": comune["properties"]['prov_acr'],
            "np": rows[0][0],
            "c": bool(rows[0][1]),
            "p": bool(rows[0][2]),
        }
    with open("./gh-pages/capoluoghi.topo.json", mode="w", encoding="utf8") as jfile:
        json.dump(topofile, jfile, separators=(",", ":"))


if __name__ == "__main__":
    main()
