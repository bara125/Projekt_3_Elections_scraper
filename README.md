# Elections Scraper – Czech Parliamentary Elections 2017

Tento projekt slouží ke scrapování výsledků voleb do Poslanecké sněmovny České republiky z roku 2017 z oficiálního webu **volby.cz**.

Skript umožňuje stáhnout volební výsledky pro libovolný územní celek (okres) a uložit je do CSV souboru ve strukturovaném formátu.

---

## 📌 Popis projektu

Program:
- přijímá **URL územního celku** jako vstupní argument,
- projde všechny obce v daném územním celku,
- pro každou obec stáhne:
  - počet registrovaných voličů,
  - počet vydaných obálek,
  - počet platných hlasů,
  - hlasy pro jednotlivé politické strany,
- výstup uloží do **CSV souboru**.

Data jsou získávána přímo z webu:
https://www.volby.cz/pls/ps2017nss/

---

## ⚙️ Instalace

### 1️⃣ Klonování repozitáře
```bash
git clone https://github.com/<tvuj-github-ucet>/<nazev-repozitare>.git
cd <nazev-repozitare>
