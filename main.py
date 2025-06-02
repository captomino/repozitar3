"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Tomáš Čáp
email: tomas.cap@centrum.cz
"""

# KROK 1 - Import knihoven ----------------------------------------------------

import sys
import re
import requests
from bs4 import BeautifulSoup
import csv


# KROK 2 - Definice funkcí ----------------------------------------------------

def zkontroluj_argumenty() -> tuple[str, str]:
    """
    Zkontroluje argumenty příkazové řádky a vrátí je, pokud jsou platné.

    Skript musí být spuštěn se dvěma argumenty kromě názvu skriptu (main.py):
    1. URL začínající na "https://www.volby.cz/"
    2. Název výstupního CSV souboru končící na ".csv"

    Pokud nejsou podmínky splněny, funkce vypíše chybu a ukončí program.

    Returns:
        tuple[str, str]: Validovaná URL a název CSV souboru.
    """
    if len(sys.argv) != 3:
        print(
            "Chybné argumenty!",
            "Je třeba zadat: py[thon] main.py [URL] [vystup.csv]",
            sep = "\n"
            )
        sys.exit(1)

    url, output_file = sys.argv[1], sys.argv[2]

    url_pattern = r'^https://www\.volby\.cz/'
    csv_pattern = r'.+\.csv$'

    if not re.match(url_pattern, url):
        print(
            "Pozor chyba!",
            "První argument musí být platná URL (https://www.volby.cz/).",
            "Argument musí být zapsaný v uvozovkách (string).",
            sep = "\n"
            )
        sys.exit(1)

    if not re.match(csv_pattern, output_file, re.IGNORECASE):
        print(
            "Pozor chyba!",
            "Druhý argument musí být název CSV souboru (končí na .csv).",
            "Argument musí být zapsaný v uvozovkách (string).",
            sep = "\n"
            )        
        sys.exit(1)

    return url, output_file


def nacti_html(url: str) -> BeautifulSoup:
    """
    Načte HTML obsah z dané URL a vrátí ho jako objekt BeautifulSoup.

    Funkce provede HTTP GET požadavek na zadanou URL. Pokud server vrátí
    jiný stavový kód než 200, vypíše chybovou zprávu a ukončí program.

    Args:
        url (str): Adresa webové stránky, kterou chceme načíst.

    Returns:
        BeautifulSoup: Objekt reprezentující parsovaný HTML obsah stránky.
    """  
    response = requests.get(url)
    if response.status_code != 200:
        print(
            "Pozor chyba!",
            "Nepodařilo se načíst URL.",
            sep = "\n"
            )
        sys.exit(1)
    return BeautifulSoup(response.text, "html.parser")


def ziskej_odkazy_na_obce(base_url: str, soup: BeautifulSoup) -> list[str]:
    """
    Získá seznam odkazů na obce z HTML obsahu stránky.

    Funkce prohledá všechny tabulky v objektu BeautifulSoup, přeskočí
    první dva řádky každé tabulky (hlavičku) a z prvního sloupce každého
    řádku extrahuje relativní odkazy. Ty spojí s base_url a vrátí seznam
    kompletních URL odkazů.

    Args:
        base_url (str): Základní URL, ke které se připojují relativní odkazy.
        soup (BeautifulSoup): Parsovaný HTML obsah stránky.

    Returns:
        list[str]: Seznam úplných URL odkazů na jednotlivé obce.
    """
    links = []
    tables = soup.find_all("table")  # Najdi všechny tabulky

    for table in tables:
        for row in table.find_all("tr")[2:]:  # Přeskoč první dva řádky tabulky
            cells = row.find_all("td")
            if cells:
                link_tag = cells[0].find("a")
                if link_tag and "href" in link_tag.attrs:
                    relative_link = link_tag["href"]
                    links.append(base_url + relative_link)

    return links


def zpracuj_data_obce(soup: BeautifulSoup) -> dict[str, int | str | None]:
    """
    Extrahuje volební data a informace o obci z HTML obsahu stránky.

    Funkce získá název obce, její kód, základní statistiky o volbách
    (registrovaní, obálky, platné hlasy) a hlasy pro jednotlivé strany.
    Výsledkem je slovník s těmito údaji, kde klíče jsou názvy proměnných
    a názvy stran.

    Args:
        soup (BeautifulSoup): Parsovaný HTML obsah stránky obce.

    Returns:
        dict[str, int | str | None]: Slovník s informacemi o obci a výsledky
            voleb. Klíče zahrnují 'code', 'location', 'registered', 
            'envelopes', 'valid' a názvy stran s příslušnými počty hlasů.
    """
    # 1. Název obce
    location = ""
    for h3 in soup.find_all("h3"):
        if "Obec:" in h3.text:
            location = h3.text.replace("Obec:", "").strip()
            break

    # 2. Kód obce z odkazu
    code = None
    odkaz = soup.find("div", class_="tab_full_ps311").find("a")
    if odkaz and "xobec=" in odkaz["href"]:
        params = odkaz["href"].split("&")
        for p in params:
            if p.startswith("xobec="):
                code = p.split("=")[1]
                break

    # 3. Základní volební data
    registered = envelopes = valid = 0
    tabulka = soup.find("table", id="ps311_t1")
    radky = tabulka.find_all("tr")
    if len(radky) >= 3:
        bunky = radky[2].find_all("td")
        registered = int(bunky[3].text.replace('\xa0', '').replace(' ', ''))
        envelopes = int(bunky[4].text.replace('\xa0', '').replace(' ', ''))
        valid = int(bunky[7].text.replace('\xa0', '').replace(' ', ''))

    # 4. Hlasy pro strany (shromáždím je jako [(cislo, nazev, hlasy)])
    strany = []
    for tabulka_stran in soup.find_all("table", class_="table"):
        hlavicky = [th.text.strip() for th in tabulka_stran.find_all("th")]
        if "Strana" in hlavicky and "Platné hlasy" in hlavicky:
            for radek in tabulka_stran.find_all("tr")[2:]:
                bunky = radek.find_all("td")
                if len(bunky) >= 3:
                    cislo = bunky[0].text.strip()
                    nazev = bunky[1].text.strip()
                    hlasy = bunky[2].text.strip().replace('\xa0', '').replace(' ', '')
                    if cislo.isdigit():
                        try:
                            strany.append((int(cislo), nazev, int(hlasy)))
                        except ValueError:
                            strany.append((int(cislo), nazev, 0))

    # 5. Seřazení podle čísla strany
    strany_sorted = sorted(strany, key=lambda x: x[0])

    # 6. Vytvoření výsledného slovníku v požadovaném pořadí
    vysledky = {
        "code": code,
        "location": location,
        "registered": registered,
        "envelopes": envelopes,
        "valid": valid
    }

    # 7. Přidání stran v přesném pořadí podle čísla
    for _, nazev, hlasy in strany_sorted:
        vysledky[nazev] = hlasy

    return vysledky

def exportuj_vysledky_do_csv(
    vysledky_list: list[dict[str, int | str | None]],
    nazev_souboru: str
) -> None:
    """
    Exportuje seznam výsledků do CSV souboru se správným záhlavím.

    Funkce vytvoří CSV soubor, kde první sloupce jsou základní údaje o obci
    ("code", "location", "registered", "envelopes", "valid") a dále následují
    sloupce pro jednotlivé politické strany podle pořadí z prvního záznamu.

    Pokud je seznam výsledků prázdný, funkce pouze vypíše upozornění
    a CSV nevytvoří.

    Args:
        vysledky_list (list[dict]): Seznam slovníků s výsledky voleb
            pro jednotlivé obce.
        nazev_souboru (str): Název výstupního CSV souboru.

    Returns:
        None
    """
    if not vysledky_list:
        print("Žádná data k exportu.")
        return

    # 1. Získání záhlaví (fieldnames) v požadovaném pořadí
    zakladni_sloupce = ["code", "location", "registered", "envelopes", "valid"]

    # Získám všechny unikátní názvy stran a zachovám jejich pořadí podle první obce
    vsechny_strany = [k for k in vysledky_list[0].keys() if k not in zakladni_sloupce]

    fieldnames = zakladni_sloupce + vsechny_strany

    # 2. Zápis do CSV
    with open(nazev_souboru, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for obec in vysledky_list:
            writer.writerow(obec)


# KROK 3 - Hlavní funkce skriptu ----------------------------------------------

def hlavni() -> None:
    """
    Hlavní funkce skriptu pro stažení a zpracování volebních dat.

    Funkce zkontroluje argumenty, načte základní URL, získá odkazy na obce,
    postupně stáhne a zpracuje data jednotlivých obcí, seskupí názvy stran,
    a výsledky uloží do CSV souboru.

    Během zpracování vypisuje informace o průběhu a případné chyby.

    Returns:
        None
    """
    base_url, output_file = zkontroluj_argumenty()
    
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {base_url}")
    soup = nacti_html(base_url)
    links = ziskej_odkazy_na_obce(base_url.rsplit('/', 1)[0] + "/", soup)
    
    results = []
    all_parties = set()

    for link in links:
        try:
            mun_soup = nacti_html(link)
            data = zpracuj_data_obce(mun_soup)
            all_parties.update(
                data.keys() 
                - {
                    "code", 
                    "location", 
                    "registered", 
                    "envelopes", 
                    "valid"
                }
            )            
            results.append(data)
        except Exception as e:
            print(f"Chyba při zpracování odkazu: {link}")
            print(e)

    all_parties = sorted(all_parties)

    print(f"UKLÁDÁM DO SOUBORU: {output_file}")
    exportuj_vysledky_do_csv(results, output_file)
    
    print("UKONČUJI: main.py (webový scraper)")

# Spustí hlavní funkci pouze pokud je skript spuštěn přímo
if __name__ == "__main__":
    hlavni()
