import psycopg2
import pandas as pd

# Charger le df
df = pd.read_csv('clean_step5_normalized.csv')
cols = ['prix_page_principale', 'Marque_Audi', 'Marque_BMW', 'Boîte de vitesse_Inconnu', 'Boîte de vitesse_Manuelle']
df_subset = df[cols]

conn = psycopg2.connect(dbname="avito_db", user="postgres", password="jamal", host="localhost", port=5432)
cur = conn.cursor()

# Création table (exemple simple, adapter types)
cur.execute("""
CREATE TABLE IF NOT EXISTS voitures_avito_subset (
    prix_page_principale FLOAT,
    Marque_Audi INT,
    Marque_BMW INT,
    Boite_de_vitesse_Manuelle INT,
    Boite_de_vitesse_Inconnu INT
);
""")

conn.commit()

# Insérer les données ligne par ligne
insert_query = """
INSERT INTO voitures_avito_subset (prix_page_principale, Marque_Audi, Marque_BMW, Boite_de_vitesse_Manuelle, Boite_de_vitesse_Inconnu)
VALUES (%s, %s, %s, %s, %s)
"""

for row in df_subset.itertuples(index=False):
    cur.execute(insert_query, row)

conn.commit()
cur.close()
conn.close()
