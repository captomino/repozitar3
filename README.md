# Třetí projekt – Webový scraper volebních dat (Engeto Online Python Akademie)

## Popis projektu

Tento skript (`main.py`) slouží k automatizovanému stažení a zpracování dat z volebních výsledků publikovaných na webu https://www.volby.cz/. Pomocí HTML scrapingu skript získává volební výsledky pro jednotlivé obce, tyto výsledky strukturuje a ukládá do CSV souboru.

Projekt byl vytvořen jako třetí úkol v rámci **Engeto Online Python Akademie**.

---

## Autor

- **Jméno:** Tomáš Čáp  
- **Email:** tomas.cap@centrum.cz

---

## Požadavky

- Python 3.10+
- Knihovny:
  - `requests`
  - `beautifulsoup4`

---

## Instalace požadovaných knihoven

Seznam knihoven použitých při tvorbě projektu je uložen v souboru *requirements.txt*. V novém virtuálním prostředí se spouští pomocí manažeru:

pip install -r requirements.txt

---

## Spuštění skriptu

Skript se spouští z příkazové řádky se dvěma argumenty:

python main.py "https://www.volby.cz/pls/ps2017nss/..." "vysledky.csv"

Argumenty:
  1. URL – odkaz na hlavní stránku s přehledem volebních výsledků (musí začínat na https://www.volby.cz/)
  2. vysledky.csv – název výstupního souboru, kam budou uloženy výsledky (musí končit na .csv)

---

## Co skript dělá
 
Skript provádí tyto úkony:

  1. Validuje vstupy - kontroluje správný formát URL a názvu CSV.
  2. Stáhne hlavní stránku a najde odkazy na jednotlivé obce.
  3. Pro každou obec:
      - Stáhne HTML stránku.
      - Vytáhne název obce, kód, počet registrovaných voličů, vydaných obálek, platných hlasů a počty hlasů pro jednotlivé strany.
  4. Výsledky uloží do výstupního CSV souboru se záhlavím.

---

## Struktura výstupního CSV

Každý řádek představuje jednu obec. Sloupce:
  - code – kód obce
  - location – název obce
  - registered – počet registrovaných voličů
  - envelopes – počet vydaných obálek
  - valid – počet platných hlasů
  – sloupce pro jednotlivé politické strany s počtem hlasů

---

## Ošetření chyb

Skript ukončí běh, pokud nejsou argumenty ve správném formátu.
Při chybě ve stahování nebo zpracování dat konkrétní obce vypíše chybovou zprávu, ale pokračuje dále.

---

## Ukázka projektu

Výsledky hlasování pro okres Olomouc:

  1. argument: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7102
  2. argument: vysledky_olomouc.csv

### Spuštění programu:

py main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7102" "vysledky_olomouc.csv"

### Průběh programu:

STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7102
UKLÁDÁM DO SOUBORU: vysledky_olomouc.csv
UKONČUJI: main.py (webový scraper)

### Částečný výstup:

code,location,registered,envelopes,valid,Občanská demokratická strana,Řád národa - Vlastenecká unie,[...]
552356,Babice,370,256,254,13,0,0,10,0,18,25,1,5,2,1,0,17,0,5,79,0,0,9,0,0,2,0,66,1
500526,Bělkovice-Lašťany,1801,1079,1069,97,0,0,83,1,44,81,18,6,15,1,1,104,0,32,333,1,2,75,0,6,8,1,153,7
[...]

---

## Poznámky

Ujistěte se, že zadaná URL opravdu směřuje na stránku s přehledem obcí.