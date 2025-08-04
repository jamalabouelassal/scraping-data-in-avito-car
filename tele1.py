import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import numpy as np

# -------------------------------
# 1. Charger les données brutes
# -------------------------------
df = pd.read_csv('avito_voitures.csv')
print(f"✅ Données chargées : {df.shape}")
print("Colonnes :", df.columns.tolist())

# Sauvegarde initiale
df.to_csv('clean_step0_original.csv', index=False, encoding='utf-8')
print("💾 Données originales sauvegardées : clean_step0_original.csv")

# -------------------------------
# 2. Supprimer colonnes inutiles
# (aucune en plus car tu as déjà supprimé url_annonce, titre_detail, prix_detail)
# -------------------------------
# On garde : titre_page_principale, prix_page_principale, Catégorie, Année/Modèle, Boîte de vitesse,
# Type de carburant, Kilométrage, Marque, Modèle, Nombre de portes, Origine, Première main, Puissance fiscale, État
df = df[['titre_page_principale', 'prix_page_principale', 'Catégorie', 'Année/Modèle', 'Boîte de vitesse',
         'Type de carburant', 'Kilométrage', 'Marque', 'Modèle', 'Nombre de portes',
         'Origine', 'Première main', 'Puissance fiscale', 'État']]

df.to_csv('clean_step1_selected_columns.csv', index=False, encoding='utf-8')
print("💾 Après suppression des colonnes inutiles : clean_step1_selected_columns.csv")

# -------------------------------
# 3. Nettoyage des valeurs numériques
# -------------------------------
# Convertir prix_page_principale et Kilométrage en numériques
df['prix_page_principale'] = df['prix_page_principale'].str.replace(r'[^\d]', '', regex=True).replace('', np.nan).astype(float)
df['Kilométrage'] = df['Kilométrage'].str.replace(r'[^\d]', '', regex=True).replace('', np.nan).astype(float)
df['Année/Modèle'] = pd.to_numeric(df['Année/Modèle'], errors='coerce')

df.to_csv('clean_step2_numeric_conversion.csv', index=False, encoding='utf-8')
print("💾 Après conversion des colonnes numériques : clean_step2_numeric_conversion.csv")

# -------------------------------
# 4. Gestion des valeurs manquantes
# -------------------------------
# Imputation pour les colonnes numériques
num_cols = ['prix_page_principale', 'Kilométrage', 'Année/Modèle']
imputer_num = SimpleImputer(strategy='median')
df[num_cols] = imputer_num.fit_transform(df[num_cols])

# Imputation pour les colonnes catégorielles
cat_cols = [col for col in df.columns if col not in num_cols]
for col in cat_cols:
    df[col].fillna('Inconnu', inplace=True)

df.to_csv('clean_step3_missing_values.csv', index=False, encoding='utf-8')
print("💾 Après traitement des valeurs manquantes : clean_step3_missing_values.csv")

# -------------------------------
# 5. Encodage des variables catégorielles (OneHot)
# -------------------------------
encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
encoded_data = encoder.fit_transform(df[cat_cols])
encoded_cols = encoder.get_feature_names_out(cat_cols)

df_encoded = pd.DataFrame(encoded_data, columns=encoded_cols)
df_final = pd.concat([df[num_cols].reset_index(drop=True), df_encoded.reset_index(drop=True)], axis=1)

df_final.to_csv('clean_step4_encoded.csv', index=False, encoding='utf-8')
print("💾 Après encodage OneHot : clean_step4_encoded.csv")

# -------------------------------
# 6. Normalisation des données numériques
# -------------------------------
scaler = StandardScaler()
df_final[num_cols] = scaler.fit_transform(df_final[num_cols])

df_final.to_csv('clean_step5_normalized.csv', index=False, encoding='utf-8')
print("💾 Après normalisation : clean_step5_normalized.csv")

print("✅ Nettoyage terminé !")
print(df_final.head())
