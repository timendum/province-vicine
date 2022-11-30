import csv
import sqlite3


def main():
    con = sqlite3.connect("db.sqlite3")
    con.execute("DROP TABLE IF EXISTS coords")
    con.execute(
        """CREATE TABLE IF NOT EXISTS
    coords (
        id INT PRIMARY KEY,
        lat FLOAT NULL,
        long FLOAT NULL,
        FOREIGN KEY (id) REFERENCES comuni (id)
    ) WITHOUT ROWID;"""
    )

    for filename in ("data/geoname.csv", "data/v8JTFUv85eVKy7eQ9DgL.csv"):
        with open(filename, mode="rt", encoding="utf8", newline="") as csvfile:
            creader = csv.reader(csvfile, delimiter=";")
            if "geoname.csv" not in filename:
                next(creader)  # headers
            for row in creader:
                try:
                    crow = [row[0], float(row[1]), float(row[2])]
                except ValueError:
                    # KO del servizio di Geocoding
                    crow = None
                if crow and not (35 <= crow[1] <= 48):
                    # latidudine non valida per l'Italia
                    crow = None
                if crow and not (6 <= crow[2] <= 19):
                    # longintudine non valida per l'Italia
                    crow = None
                # CANICATTINI BAGNI SR Italy
                # Ignora nomi doppi separati da /
                name = " ".join(row[0].split(" ")[:-2]).split("/")[0]
                prov = row[0].split(" ")[-2]
                id = con.execute(
                    "SELECT id from comuni where nome = ? and provincia = ?",
                    (name, prov),
                ).fetchone()
                if not id:
                    print(f"Not found {name}, {prov}")
                    continue
                if not crow:
                    already = con.execute("select id from coords where id =?", id).fetchone()
                    if already:
                        pass
                    else:
                        print(f"Invalid coords: {row}")
                else:
                    crow[0] = id[0]
                    con.execute(
                        "REPLACE INTO coords VALUES(?, ?, ?)",
                        crow,
                    )
    print("Lines", con.execute("SELECT COUNT(*) FROM coords").fetchone()[0])
    print(
        "Missing",
        con.execute(
            "select count(*) from comuni where not exists (select id from coords where coords.id = comuni.id);"
        ).fetchone()[0],
    )
    con.commit()


main()
