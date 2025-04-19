import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'violations.sqlite')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def search_violations_between_dates(date_debut, date_fin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT * FROM violations
    WHERE date BETWEEN ? AND ?
    """
    cursor.execute(query, (date_debut, date_fin))

    resultats = [
        dict(zip([column[0] for column in cursor.description], row))
        for row in cursor.fetchall()
    ]

    conn.close()
    print(f"Results: {resultats}")
    return resultats


def search_violations(etablissement=None, proprietaire=None, rue=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM violations WHERE 1=1"
    params = []

    if etablissement:
        query += " AND etablissement LIKE ?"
        params.append(f"%{etablissement}%")
    if proprietaire:
        query += " AND proprietaire LIKE ?"
        params.append(f"%{proprietaire}%")
    if rue:
        query += " AND adresse LIKE ?"
        params.append(f"%{rue}%")

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results


def get_all_establishments():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT etablissement FROM violations ORDER BY etablissement")
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_violations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT etablissement FROM violations")
    return cursor.fetchall()
