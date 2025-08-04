from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# -------------------------------
# Configuration Selenium
# -------------------------------
chromedriver_path = 'C:/WebDriver/bin/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# -------------------------------
# Fonction pour scroller la page
# -------------------------------
def scroll_page():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# -------------------------------
# Extraction annonces page principale
# -------------------------------
def extract_annonces_main_page(soup):
    annonces = soup.find_all('a', class_='sc-1jge648-0 jZXrfL')
    list_annonces = []

    for annonce in annonces:
        titre_element = annonce.find('p', class_='sc-1x0vz2r-0 iHApav')
        prix_element = annonce.find('p', class_='sc-1x0vz2r-0 dJAfqm sc-b57yxx-3 eTHoJR')

        titre = titre_element.text.strip() if titre_element else None
        prix_main = prix_element.text.strip() if prix_element else None
        url_annonce = annonce['href'] if 'href' in annonce.attrs else None

        if url_annonce and not url_annonce.startswith('http'):
            url_annonce = 'https://www.avito.ma' + url_annonce

        if titre and url_annonce:
            list_annonces.append({
                'titre_page_principale': titre,
                'prix_page_principale': prix_main,
                'url_annonce': url_annonce
            })

    return list_annonces

# -------------------------------
# Extraction détails page annonce
# -------------------------------
def scrape_details_page(url_annonce):
    try:
        driver.get(url_annonce)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Récupération des détails dans l'ordre donné
        labels = [
            'Catégorie', 'Année/Modèle', 'Boîte de vitesse', 'Type de carburant',
            'Kilométrage', 'Marque', 'Modèle', 'Nombre de portes',
            'Origine', 'Première main', 'Puissance fiscale', 'État'
        ]

        values_spans = soup.find_all('span', class_='fjZBup')
        values = [span.text.strip() for span in values_spans[:len(labels)]]

        details = dict(zip(labels, values))

        return details

    except Exception as e:
        print(f"⚠️ Erreur sur {url_annonce} : {e}")
        return {}

# -------------------------------
# Scraper toutes les pages
# -------------------------------
url_base = "https://www.avito.ma/fr/maroc/voitures?o={}"
final_data = []

for page in range(1, 4):  # Change 4 pour plus de pages
    url_page = url_base.format(page)
    print(f"\n📄 Scraping page {page}: {url_page}")
    driver.get(url_page)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-1jge648-0")))
    scroll_page()

    soup_main = BeautifulSoup(driver.page_source, 'html.parser')
    annonces_list = extract_annonces_main_page(soup_main)
    print(f"✅ {len(annonces_list)} annonces trouvées sur la page {page}")

    for i, annonce in enumerate(annonces_list, start=1):
        print(f"➡ Scraping annonce {i}/{len(annonces_list)} : {annonce['url_annonce']}")
        details = scrape_details_page(annonce['url_annonce'])
        annonce_filtered = {
            'titre_page_principale': annonce.get('titre_page_principale'),
            'prix_page_principale': annonce.get('prix_page_principale')
        }
        annonce_complet = {**annonce_filtered, **details}
        final_data.append(annonce_complet)
        time.sleep(random.uniform(1.5, 2.5))

driver.quit()

# -------------------------------
# Sauvegarde des résultats
# -------------------------------
df = pd.DataFrame(final_data)
if df.empty:
    print("⚠️ Le DataFrame est vide. Vérifie les sélecteurs CSS.")
else:
    print(f"\n✅ {len(df)} annonces extraites au total.")
    print(df.head())
    df.to_csv('avito_voitures.csv', index=False, encoding='utf-8')
    print("✅ Données sauvegardées dans 'avito_voitures.csv'")
