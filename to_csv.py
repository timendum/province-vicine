import sqlite3
import csv

from paint import prov_col


def main():
    con = sqlite3.connect("./db.sqlite3")
    curs = con.execute(
        """SELECT c.istat, c.nome, d.provincia, c.provincia, d.provincia=c.provincia, comune=d.id
        FROM matches
        LEFT JOIN comuni as c ON comune=c.id
        LEFT JOIN comuni as d ON capoluogo=d.id
        """
    )
    with open("data/output.csv", mode="w", encoding="utf8", newline="") as csvfile:
        cwriter = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        cwriter.writerow(
            ("ISTAT", "NOME", "new_prov", "old_prov", "changed_prov", "is_capoluogo", "color")
        )
        for row in curs:
            cwriter.writerow(list(row) + ["ABCDEFG"[prov_col[row[2]]]])


if __name__ == "__main__":
    main()
