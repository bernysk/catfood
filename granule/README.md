# Granule pre mačky — veterinárne diéty

**161 granúl · 19 ručne overených (GI diéty) + všetky suché veterinárne diéty Royal Canin, Hill's, Brit, Farmina, Calibra, Virbac HPM, Trovet a všetky granule Pro Plan (CZ, SK, UK) · dáta zo stránok výrobcov · v1.3, október 2026**

📄 **[Dokument prieskumu](./Prieskum_granule_GI.md)** — metodika, štúdie, výsledky, kontrola prilepeného zoznamu, Kitten vs. Adult
📊 **[Interaktívna tabuľka](https://bernysk.github.io/catfood/granule/)** — triedenie, filtre, pôvodný text etikety pri každom produkte

> **⚠️** Nie je to veterinárne odporúčanie. Veterinárne diéty sa podávajú po konzultácii
> s veterinárom, ktorý najprv zistí príčinu ťažkostí. Bez známky A–E — diéty sa porovnávajú
> podľa účelu, všetko na 1000 kcal.

## Štruktúra

```
README.md                 tento prehľad
Prieskum_granule_GI.md    dokument prieskumu
raw_data/gi_dry.json      ručne overené produkty: doslovný text + nezaradené produkty s dôvodom
raw_data/proplan_dry.json automaticky stiahnuté granule Pro Plan (CZ, SK, UK; EU = chyba servera)
raw_data/royalcanin_vet.json  automaticky stiahnuté veterinárne diéty Royal Canin (SK, CZ)
raw_data/others_vet.json  automaticky stiahnuté diéty Brit, Farmina, Virbac HPM, Trovet
raw_data/hills_vet.json   diéty Hill's (CZ) – načítané vstavaným prehliadačom (stránka blokuje skripty)
raw_data/calibra_vet.json diéty Calibra (SK) – načítané vstavaným prehliadačom
scrape_proplan.py         sťahovanie Pro Plan (výpisy ?page=N + produktové stránky)
scrape_royalcanin.py      sťahovanie Royal Canin (sitemap + produktové stránky)
scrape_others.py          sťahovanie Brit, Farmina, Virbac HPM, Trovet
scraped.py                prevod stiahnutých stránok do tabuľky (kategórie, vláknina)
build_dataset.py          raw_data → dataset.json + index.html
index.template.html       šablóna tabuľky (dáta sa vkladajú pri builde)
index.html                vygenerovaná tabuľka (otvorí sa aj lokálne)
dataset.json              prepočítané hodnoty
```

## Prebuildovanie

```bash
python granule/scrape_proplan.py      # voliteľné — znovu stiahne Pro Plan
python granule/scrape_royalcanin.py   # voliteľné — znovu stiahne Royal Canin
python granule/scrape_others.py       # voliteľné — Brit, Farmina, Virbac, Trovet
python granule/build_dataset.py
```

## Rozdiely oproti prieskumu mokrého krmiva

| | Mokré krmivo | Granule (GI diéty) |
|---|---|---|
| Hodnotenie | rámec A–E | bez známky, porovnanie podľa účelu |
| Základ porovnania | sušina | 1000 kcal |
| Energia | často chýba | etiketa → priemerný obsah výrobcu → odhad (označený) |
| Vlhkosť | deklarovaná | zriedka (Brit, Trovet, časť Virbac) |
