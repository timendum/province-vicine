import csv
import requests
import os
from time import sleep

API_KEY = os.getenv("GEOAPIFY_KEY")


def main() -> None:
    with open("data/geoname.csv", mode="rt", encoding="utf8", newline="") as csvfile:
        creader = csv.reader(csvfile, delimiter=";")
        oks = []
        todo = []
        for row in creader:
            if len(row) > 1:
                oks.append(row)
            else:
                todo.append(row[0])

    for name in todo:
        url = "https://api.geoapify.com/v1/geocode/search"
        data = {"text": name, "format": "json", "apiKey": API_KEY}
        response = requests.get(url, params=data).json()
        oks.append([name, response["results"][0]["lat"], response["results"][0]["lon"]])
        sleep(1 / 5)  # Up to 5 requests/second

    with open("data/geoname.csv", mode="w", encoding="utf8", newline="") as csvfile:
        cwriter = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        cwriter.writerows(oks)


if __name__ == "__main__":
    main()
