from flask import Flask, render_template, request, jsonify, Response
from apscheduler.schedulers.background import BackgroundScheduler
from database import search_violations, search_violations_between_dates
from database import get_all_establishments, get_all_violations
from datetime import datetime
from collections import Counter
from jsonschema import validate, ValidationError
import subprocess
import os
import atexit
import dicttoxml
import json

app = Flask(__name__, static_url_path="", static_folder="static")


def update_database():
    script_path = os.path.join(os.path.dirname(__file__),'..', "DataScript.py")
    subprocess.run(['python', script_path])


update_database()
scheduler = BackgroundScheduler()
scheduler.add_job(update_database, 'cron', hour=0, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        etablissement = request.form.get("etablissement")
        proprietaire = request.form.get("proprietaire")
        rue = request.form.get("rue")
        results = search_violations(etablissement, proprietaire, rue)
        return render_template("results.html", results=results)

    etablissements = get_all_establishments()
    return render_template("index.html", etablissements=etablissements)


@app.route("/contrevenants", methods=["GET"])
def contrevenants():
    date_debut = request.args.get("du")
    date_fin = request.args.get("au")
    try:
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d").strftime("%Y%m"
                                                                        "%d")
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d").strftime("%Y%m%d")
    except ValueError:
        return jsonify({"erreur": "Les dates doivent être au format ISO 8601 "
                        "(YYYY-MM-DD)"}), 400

    resultats = search_violations_between_dates(date_debut, date_fin)
    etablissements = [violation["etablissement"] for violation in resultats]
    counts = Counter(etablissements)
    response_data = [{"etablissement": etab, "nombre_contraventions": count}
                     for etab, count in counts.items()]
    return jsonify(response_data)


@app.route("/infractions", methods=["GET"])
def infractions_par_etablissements():
    nom_etablissement = request.args.get("etablissement")
    if not nom_etablissement:
        return jsonify({"erreur": "Le nom de l'établissement est requis"}), 400

    resultats = search_violations(nom_etablissement, None, None)
    return jsonify([dict(row) for row in resultats])


@app.route("/etablissements", methods=["GET"])
def etablissements_contraventions():
    violations = get_all_violations()
    from collections import Counter
    etablissements = [v["etablissement"] for v in violations]
    counter = Counter(etablissements)

    sorted_etabs = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    response_data = [{"etablissement": name, "nombre_infractions": count}
                     for name, count in sorted_etabs]
    return jsonify(response_data)


@app.route("/etablissementsxml", methods=["GET"])
def etablissements_contraventions_xml():
    violations = get_all_violations()
    etablissements = [v["etablissement"] for v in violations]
    counter = Counter(etablissements)
    sorted_etabs = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    response_data = [{"etablissement": name, "nombre_infractions": count}
                     for name, count in sorted_etabs]
    xml_data = dicttoxml.dicttoxml(response_data,
                                   custom_root='etablissements', ids=False)
    return Response(xml_data, mimetype="application/xml",
                    content_type="application/xml; charset=utf-8")


@app.route("/demande-inspection", methods=["POST"])
def demande_inspection():
    try:
        data = request.get_json()
        with open("static/demande_inspection.json", "r") as f:
            schema = json.load(f)
        validate(instance=data, schema=schema)
        print("Plainte reçue :", data)
        return jsonify({"message": "Demande d'inspection reçue"}), 201

    except ValidationError as e:
        return jsonify({"error": "Validation JSON échouée",
                        "details": e.message}), 400
    except Exception as e:
        return jsonify({"error": "Erreur serveur", "details": str(e)}), 500


@app.route("/plainte")
def page_plainte():
    return render_template("plainte.html")


@app.route("/doc", methods=["GET"])
def documentation():
    with open("static/doc.raml", "r", encoding="utf-8") as file:
        raml_content = file.read()
    return render_template("doc.html", raml=raml_content)


if __name__ == "__main__":
    app.run(debug=True)
