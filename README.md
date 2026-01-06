# Engeto-Projekt-3-Elections-scraper

## Popis projektu
Projekt scrapuje (extrahuje) výsledky parlamentních voleb z roku 2017. 
Projde všechny obce v zadaném územním celku a pro každou stáhne:
  - počet registrovaných voličů,
  - počet vydaných obálek,
  - počet platných hlasů,
  - hlasy pro jednotlivé politické strany,
- výstup uloží do CSV souboru

Data jsou získávána z webu:
https://www.volby.cz/pls/ps2017nss/

## Instalace knihoven třetích stran 
Projekt využívá knihovny třetích stran. Tyto nejsou součástí standartní kníhovny Pythonu a je nutné je doinstalovat. K jejich instalaci je doporučeno vytvoření nového virtuálního prostředí. 
Všechny potřebné knihovny jsou uvedeny v souboru `requirements.txt`.
Knihovny lze naisntalovat pomocí příkazů níže: 

```bash
pip3 --version            # ověření verze pip
pip3 install -r requirements.txt   # instalace knihoven třetích stran
```
## Spuštění projektu

Spuštění skriptu `main.py` z příkazové řádky vyžaduje **dva povinné argumenty**:

1. odkaz na územní celek (okres),
2. název výstupního CSV souboru.

## Ukázka průběhu pro okres Benešov 

**1. argument (odkaz na územní celek):**https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101
**2. argument (výstupní CSV soubor):** vysledky_benesov.csv


### Spuštění programu

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky_benesov.csv
```
### Průběh stahování

```text
Saved: vysledky_benesov.csv
```
### Částečný výstup
code,location,registered,envelopes,valid,ANO 2011,Dobrá volba 2016,Dělnic.str.sociální spravedl.,Křesť.demokr.unie-Čs.str.lid.,REALISTÉ,Referendum o Evropské unii,SPORTOVCI,SPR-Republ.str.Čsl. M.Sládka,Strana Práv Občanů,Svob.a př.dem.-T.Okamura (SPD),TOP 09,Unie H.A.V.E.L.,Česká strana národně sociální
529303,Benešov,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5
532568,Bernartice,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5
530743,Bílkovice,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5
532380,Blažejovice,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5
532096,Borovnice,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5
532924,Bukovany,13104,8485,8437,2577,3,16,314,58,6,17,21,10,682,414,3,5