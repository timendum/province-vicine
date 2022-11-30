import sqlite3


def main():
    con = sqlite3.connect("db.sqlite3")
    con.execute("DROP TABLE IF EXISTS capoluoghi")
    con.execute(
        """CREATE TABLE IF NOT EXISTS
    capoluoghi (
        id INT PRIMARY KEY,
        FOREIGN KEY (id) REFERENCES comuni (id)
    ) WITHOUT ROWID;"""
    )

    with open("data/capoluoghi.csv", mode="rt", encoding="utf8") as txtfile:
        for row in txtfile.readlines():
            row = row.strip()
            c = con.execute("SELECT id from comuni where nome = ?", [row])
            id = c.fetchone()
            if not id:
                print(f"Not found {row}")
            if c.fetchmany():
                print(f"Too many for {row}")
                id = None
            if id:
                con.execute(
                    "REPLACE INTO capoluoghi VALUES(?)",
                    id,
                )
    print(con.execute("SELECT COUNT(*) FROM capoluoghi").fetchone()[0])
    con.commit()


main()
