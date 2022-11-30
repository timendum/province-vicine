import sqlite3
from collections import namedtuple
from geopy import distance, Point


Citta = namedtuple("Citta", ["id", "point"])


def get_capoluoghi(con: sqlite3.Connection) -> list[Citta]:
    id_capoluoghi = [row[0] for row in con.execute("select id from capoluoghi").fetchall()]
    capoluoghi = []
    for id in id_capoluoghi:
        coords = con.execute("select lat, long from coords where id = ?", [id]).fetchone()
        if not coords:
            print(f"Coords not found for {id}")
        capoluoghi.append(Citta(id, Point(*coords)))
    return capoluoghi


def near_capoluoghi(comune: Citta, capoluoghi: list[Citta]) -> list[Citta]:
    distances = []
    for capoluogo in capoluoghi:
        distances.append(distance.distance(comune.point, capoluogo.point))
    cut_dist = min(distances) * 1.35
    return [capo for dist, capo in zip(distances, capoluoghi) if dist <= cut_dist]


def main():
    con = sqlite3.connect("./db.sqlite3")
    con.execute(
        """CREATE TABLE IF NOT EXISTS
    distances (
        distance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        comune INTEGER NOT NULL,
        capoluogo INTEGER NOT NULL,
        walk FLOAT,
        car FLOAT,
        walk_rsp TEXT,
        car_rsp TEXT,
        UNIQUE(comune, capoluogo),
        FOREIGN KEY (comune) REFERENCES comuni (id),
        FOREIGN KEY (capoluogo) REFERENCES capoluoghi (id)
    );"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS
    matches (
        comune INTEGER PRIMARY KEY NOT NULL,
        capoluogo INTEGER NOT NULL,
        FOREIGN KEY (comune) REFERENCES comuni (id),
        FOREIGN KEY (capoluogo) REFERENCES capoluoghi (id)
    ) WITHOUT ROWID;"""
    )
    capoluoghi = get_capoluoghi(con)
    for row in con.execute(
        """SELECT id, lat, long
        FROM coords
        WHERE NOT EXISTS (
            SELECT comune FROM matches WHERE matches.comune=id
        )"""
    ):
        comune = Citta(row[0], Point(*row[1:3]))
        near = near_capoluoghi(comune, capoluoghi)
        if len(near) == 1:
            con.execute(
                "INSERT OR REPLACE INTO matches(comune, capoluogo) VALUES(?, ?)",
                [comune.id, near[0].id],
            )
        else:
            for n in near:
                con.execute(
                    "INSERT OR IGNORE INTO distances(comune, capoluogo) VALUES(?, ?)",
                    [comune.id, n.id],
                )
    print(
        "TODO Distances",
        con.execute("SELECT COUNT(*) FROM distances where walk is null").fetchone()[0],
    )
    print(
        "OK",
        con.execute("SELECT COUNT(*) FROM matches").fetchone()[0],
    )
    con.commit()


if __name__ == "__main__":
    main()
