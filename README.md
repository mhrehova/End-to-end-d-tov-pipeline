# E-commerce Data Pipeline: SQL + Python + Power BI

End-to-end analytický pipeline nad relačným e-commerce datasetom — od surových dát cez SQLite databázu a SQL analýzu až po vizualizácie v Pythone a dashboard v Power BI.

Projekt nadväzuje na [Power BI dashboard portfólio](#) — rovnaký dataset, ale výpočty (marže, zľavy, return rate), ktoré boli pôvodne robené v Exceli/DAX, sú tu presunuté do SQL a Pythonu, aby dashboard mohol byť napojený priamo na databázu namiesto statického Excel súboru.

## Prečo tento projekt

Cieľom bolo ukázať celý dátový tok, nie izolovaný skript:

1. **Python** – načítanie a čistenie surových dát z Excelu
2. **SQL** – relačná schéma + analytické dopyty (JOIN-y, CTE, window funkcie)
3. **Python** – vizualizácia výsledkov a automatické zhrnutie zistení
4. **Power BI** – interaktívny dashboard nad rovnakými dátami

## Dátový model

Šesť tabuliek v hviezdicovej schéme:

| Tabuľka | Popis |
|---|---|
| `orders` | 200 objednávok — dátum, zákazník, status, celkové tržby a marža |
| `order_details` | 393 riadkov objednávok — cena, zľava, náklady, marža, dôvod vrátenia |
| `products` | 50 produktov s kategóriou, cenou a nákladom |
| `customers` | 80 zákazníkov — segment, krajina |
| `categories` | 8 produktových kategórií |
| `date_dim` | Kalendárna tabuľka (546 dní) |

Cudzie kľúče prepájajú `order_details` → `orders`/`products`, a `products` → `categories`.

## Štruktúra repozitára

```
ecommerce-data-pipeline/
├── data/
│   └── ecommerce_relational.xlsx   # zdrojové dáta
├── db/
│   └── ecommerce.db                # SQLite databáza (výstup load_to_db.py)
├── sql/
│   ├── schema.sql                  # DDL: tabuľky, PK/FK, indexy
│   └── queries/
│       ├── margin_by_category.sql       # CTE + window funkcie
│       ├── top_customers.sql            # JOIN + agregácia
│       ├── return_rate.sql              # CASE + percentuálny výpočet
│       └── discount_impact_on_margin.sql # bucketing podľa výšky zľavy
├── python/
│   ├── load_to_db.py                # čistenie dát + import do SQLite
│   └── analysis.py                  # spustenie SQL dopytov + grafy + zistenia
└── output/
    ├── margin_by_category.png
    ├── top_customers.png
    ├── return_rate.png
    └── discount_impact_on_margin.png
```

## Ako to spustiť

```bash
pip install pandas openpyxl matplotlib

# 1. Import dát do SQLite
python python/load_to_db.py

# 2. Spustenie analýzy + generovanie grafov
python python/analysis.py
```

## Kľúčové zistenia

**1. Elektronika ťahá objem, nie efektivitu.**
Elektronika generuje najvyššie tržby (11 302 €) aj najvyššiu maržu v absolútnych číslach (4 956 €), ale jej percentuálna marža (43.9 %) je jediná výrazne pod priemerom všetkých kategórií (56.0 %) — o 12.2 percentuálneho bodu nižšie. Kategórie ako Záhrada či Kozmetika majú nižší objem, ale vyššiu ziskovosť na jednotku tržieb (~59–60 %).

![Marža podľa kategórie](output/margin_by_category.png)

**2. Frekvencia nákupov ≠ hodnota zákazníka.**
Zákazník s najvyššími tržbami (Michal Marek, 1 061 €) mal len 3 objednávky. Naopak zákazník s najviac objednávkami (Marek Hudák, 6 objednávok) mal priemernú hodnotu objednávky len 151 € — menej ako polovica priemeru top zákazníkov. Pri cielení marketingu na "verných" zákazníkov má zmysel pozerať sa aj na priemernú hodnotu objednávky, nie len na počet nákupov.

![Top zákazníci](output/top_customers.png)

**3. Return rate je nízky, ale nerovnomerný.**
Celkový počet vrátení je malý (7 z 393 riadkov), čo obmedzuje štatistickú váhu záverov. Napriek tomu Knihy a hry majú najvyšší podiel vrátení (5.4 %), zatiaľ čo Elektronika má nižšie % (2.2 %), ale najvyšší finančný dopad vrátení (260 €) vzhľadom na vyššie ceny produktov.

![Return rate podľa kategórie](output/return_rate.png)

**4. Hlbšie zľavy neťahajú objem hore — len znižujú maržu.**
Marža klesá takmer lineárne s hĺbkou zľavy: 60.1 % (bez zľavy) → 57.1 % (1–10 %) → 52.3 % (11–20 %) → 46.9 % (20 %+), teda pokles o 13.2 p.b. Zároveň objem predaných kusov v pásme 20 %+ klesá spolu s maržou (len 25 kusov oproti 340 bez zľavy) — zľavy v tomto datasete teda neslúžia na zvýšenie objemu, len znižujú ziskovosť.

![Dopad zľavy na maržu](output/discount_impact_on_margin.png)

## Použité technológie a zručnosti

- **Python**: pandas (čistenie a transformácia dát), matplotlib (vizualizácia), sqlite3
- **SQL**: DDL (tabuľky, PK/FK, indexy), JOIN, GROUP BY, CTE, window funkcie (`AVG() OVER()`, `RANK() OVER()`), CASE-based bucketing
- **Power BI**: DAX mierky, dátový model, dashboard (pozri samostatné portfólio)

