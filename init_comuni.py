import csv
import sqlite3


def main():
    con = sqlite3.connect("db.sqlite3")
    # Case insisitive su nome e provincia
    con.execute(
        """CREATE TABLE IF NOT EXISTS
    comuni (
        id INT PRIMARY KEY,
        nome TEXT NOT NULL COLLATE NOCASE,
        provincia TEXT COLLATE NOCASE,
        elettorale INT,
        istat TEXT,
        belfiore TEXT
    ) WITHOUT ROWID;
    """
    )
    # Indice univoco nome+provincia
    # Putroppo solo nome non è univoco
    con.execute(
        """CREATE UNIQUE INDEX nome_prv
on comuni (nome, provincia);
    """
    )

    with open("data/comuni.csv", mode="rt", encoding="utf8", newline="") as csvfile:
        creader = csv.reader(csvfile, delimiter="\t")
        for row in creader:
            # converto id e codice elettorale in numerico
            # prendo solo il primo se il comune ha due nomi (es: BOLZANO/BOZEN)
            con.execute(
                "INSERT INTO comuni VALUES(?, ?, ?, ?, ?, ?)",
                [int(row[0]), row[1].split("/")[0], row[2], int(row[3]), row[4], row[5]],
            )
    print(con.execute("SELECT COUNT(*) FROM comuni").fetchone()[0])
    con.commit()


main()
