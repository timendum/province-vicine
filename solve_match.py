import sqlite3


def main():
    con = sqlite3.connect("db.sqlite3")
    for row in con.execute("select comune, min(walk) from distances group by comune"):
        comune = row[0]
        solution = con.execute(
            "select capoluogo from distances where comune=? and walk=?", row
        ).fetchall()
        if len(solution) == 1:
            con.execute(
                "INSERT OR REPLACE INTO matches(comune, capoluogo) VALUES(?, ?)",
                [comune, solution[0][0]],
            )
        else:
            print("Not unique", row)
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
