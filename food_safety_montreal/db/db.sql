CREATE TABLE IF NOT EXISTS violations (
    id_poursuite INTEGER PRIMARY KEY NOT NULL, 
    business_id INTEGER NOT NULL,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    adresse TEXT NOT NULL,
    date_jugement DATE NOT NULL,
    etablissement TEXT NOT NULL,
    montant INTEGER NOT NULL,
    proprietaire TEXT NOT NULL,
    ville TEXT NOT NULL,
    statut TEXT NOT NULL,
    date_statut DATE NOT NULL,
    categorie TEXT NOT NULL
);
