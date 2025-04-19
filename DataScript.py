import sqlite3
import requests
import csv
from io import StringIO
import os

CSV_URL = "https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"

DB_PATH = os.path.join(os.path.dirname(__file__),'food_safety_montreal', 'db', 'violations.sqlite')


def create_database():
    if not os.path.exists(DB_PATH):
        print("testing")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        sql_path = os.path.join(os.path.dirname(__file__),'food_safety_montreal', 'db', 'db.sql')
        with open(sql_path, "r", encoding="utf-8") as f: cursor.executescript(f.read())

        conn.commit()
        conn.close()


def download_csv(url):
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text


def insert_data(csv_content):
    print(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    csv_reader = csv.reader(StringIO(csv_content), delimiter=',')
    header = next(csv_reader)
    for row in csv_reader:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO violations (
                id_poursuite, business_id, date, description, adresse,
                date_jugement, etablissement, montant, proprietaire, ville,
                statut, date_statut, categorie
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
        except Exception as e:
            print(f"Skipping row due to error: {e} | Row: {row}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    csv_data = download_csv(CSV_URL)
    insert_data(csv_data)
