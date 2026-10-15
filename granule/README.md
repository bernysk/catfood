# Granule pre mačky — gastrointestinálne diéty

**13 suchých GI diét · 6 výrobcov · dáta zo stránok výrobcov (SK/CZ) · október 2026**

📄 **[Dokument prieskumu](./Prieskum_granule_GI.md)** — metodika, štúdie, výsledky, kontrola prilepeného zoznamu, Kitten vs. Adult
📊 **[Interaktívna tabuľka](https://bernysk.github.io/catfood/granule/)** — triedenie, filtre, pôvodný text etikety pri každom produkte

> **⚠️** Nie je to veterinárne odporúčanie. Veterinárne diéty sa podávajú po konzultácii
> s veterinárom, ktorý najprv zistí príčinu ťažkostí. Bez známky A–E — diéty sa porovnávajú
> podľa účelu, všetko na 1000 kcal.

## Štruktúra

```
README.md                 tento prehľad
Prieskum_granule_GI.md    dokument prieskumu
raw_data/gi_dry.json      doslovný text zo stránok výrobcov + nezaradené produkty s dôvodom
build_dataset.py          raw_data → dataset.json + index.html
index.template.html       šablóna tabuľky (dáta sa vkladajú pri builde)
index.html                vygenerovaná tabuľka (otvorí sa aj lokálne)
dataset.json              prepočítané hodnoty
```

## Prebuildovanie

```bash
python granule/build_dataset.py
```

## Rozdiely oproti prieskumu mokrého krmiva

| | Mokré krmivo | Granule (GI diéty) |
|---|---|---|
| Hodnotenie | rámec A–E | bez známky, porovnanie podľa účelu |
| Základ porovnania | sušina | 1000 kcal |
| Energia | často chýba | etiketa → priemerný obsah výrobcu → odhad (označený) |
| Vlhkosť | deklarovaná | takmer nikdy (len Brit) |
