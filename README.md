# Mokré krmivo pre mačky — dátový prieskum

**151 produktov · 15 značiek · dáta priamo zo stránok výrobcov · júl 2026 (v4)**

Nutričné porovnanie kapsičkového mokrého krmiva pre mačky na SK/CZ trhu. Všetky hodnoty
sú stiahnuté z oficiálnych stránok výrobcov, prepočítané na sušinu a ohodnotené
jednotným rámcom A–E.

📄 **[Celý dokument prieskumu](./Prieskum_mokre_krmivo_macky.md)** — metodika, štúdie, zistenia, odporúčania
📊 **[Interaktívna tabuľka](./index.html)** — filtrovanie a triedenie podľa ktoréhokoľvek parametra (otvorí sa dvojklikom, netreba server)

> **⚠️ Čo toto je a čo nie je.** Osobný prieskum vytvorený s pomocou AI (Claude, Anthropic).
> **Nie je to** veterinárne odporúčanie, nezávislý laboratórny test ani platený obsah —
> autor nemá väzbu na žiadnu značku. Známka A–E je **vlastný, neoficiálny rámec**
> (oficiálny „Nutri-Score" pre krmivo pre zvieratá neexistuje). Zloženia zodpovedajú stavu
> k júlu 2026 a menia sa. Pri zdravotných problémoch sa poraďte s veterinárom.

---

## Výsledky v skratke

| Značka | n | Priemer | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shelma | 10 | 90,2 | 10 | – | – | – | – |
| Bozita | 4 | 89,5 | 4 | – | – | – | – |
| Dein Bestes | 2 | 89,0 | 2 | – | – | – | – |
| Calibra | 16 | 81,2 | 8 | 5 | 3 | – | – |
| Meowing Heads | 4 | 79,0 | – | 4 | – | – | – |
| Brit Premium | 23 | 76,7 | 7 | 12 | 4 | – | – |
| CarniLove | 12 | 74,9 | – | 8 | 4 | – | – |
| Brit Care | 31 | 71,2 | 2 | 20 | 7 | 2 | – |
| Stuzzy | 3 | 69,0 | – | 2 | 1 | – | – |
| Ontario | 9 | 68,8 | – | 2 | 7 | – | – |
| Royal Canin | 5 | 61,4 | – | 1 | 4 | – | – |
| Kattovit | 1 | 57,0 | – | – | 1 | – | – |
| Almo Nature | 1 | 57,0 | – | – | 1 | – | – |
| Purina Pro Plan | 16 | 55,8 | – | 1 | 12 | 2 | 1 |
| Sheba | 14 | 55,4 | – | – | 14 | – | – |

Priemer značky s malým počtom položiek nie je spoľahlivý a veterinárne diéty sú v tomto
rámci systémovo znevýhodnené — vysvetlenie v [časti 5 dokumentu](./Prieskum_mokre_krmivo_macky.md#5).

## Štruktúra repozitára

```
README.md                        tento prehľad
Prieskum_mokre_krmivo_macky.md   celý dokument prieskumu
index.html                       interaktívna tabuľka (dáta vložené priamo v súbore)

raw_data/*.json                  surové dáta — doslovný text etikiet zo stránok výrobcov
curated.json                     klasifikácia kompletnosti + zoznam nahradených záznamov
dataset.json                     normalizovaný výstup so skóre
KontrolaLM.md                    revízia metodiky NotebookLM analýz

build_dataset.py                 raw_data → dataset.json + vloženie dát do index.html
audit_parse.py                   nezávislá kontrola parsovania (iná metóda, hlási nezhody)

old/                             predchádzajúca verzia (v3) — jej dáta sa v v4 nepoužili
```

## Ako to prebuildovať

```bash
python build_dataset.py    # prepočíta dataset a aktualizuje index.html
python audit_parse.py      # skontroluje parsovanie proti surovému textu
```

Audit má hlásiť **1 známy falošný poplach** (Royal Canin oddeľuje položky pomlčkou,
ktorú audit nerozdeľuje). Čokoľvek nad rámec toho treba preveriť.

## Ako sa dáta spracúvajú

Úlohy sú zámerne rozdelené podľa toho, čo ktorá metóda vie lepšie:

| Typ údaja | Metóda | Prečo |
|---|---|---|
| Čísla z etikety | deterministický parser + audit | musí byť opakovateľné a kontrolovateľné |
| Prepočty (sušina, NFE, skóre) | deterministický výpočet | aritmetika sa nesmie odhadovať |
| Kompletnosť krmiva | prečítané s porozumením → `curated.json` | vyžaduje pochopenie vety vrátane negácií |

Každý riadok v `dataset.json` si nesie pôvodný text, z ktorého číslo pochádza
(`composition_raw`, `analytics_raw`, `additives_raw`), takže sa dá kedykoľvek overiť
bez opätovného sťahovania.

## Kľúčové metodické veci

- **Všetko je na sušinu.** Kapsičky majú 76–89 % vody; hodnoty z etikety sa porovnávať nedajú.
- **Taurín tiež.** FEDIAF udáva minimá na sušinu — porovnávať ich s číslom z obalu je
  chyba päťnásobného rádu.
- **Sacharidy (NFE) sú dopočet, nie meranie**, takže sa v nich kumulujú chyby ostatných hodnôt.
- **19 produktov má vlhkosť ≥ 85 %**, kde je prepočet na sušinu matematicky správny,
  ale krehký — sú označené ⚠ a dajú sa v tabuľke odfiltrovať.

Nájdené chyby v parsovaní aj nezrovnalosti priamo na stránkach výrobcov sú
zdokumentované v [dokumente](./Prieskum_mokre_krmivo_macky.md) a v poliach `fetch_notes`
surových dát — nič nebolo ticho opravené.
