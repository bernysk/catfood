# Granule pre mačky: gastrointestinálne diéty (SK/CZ)

**Verzia 1.3 · október 2026 · 164 granúl: 19 ručne overených (GI diéty a porovnanie, [časti 4.1–4.2](#4)) + 145 automaticky stiahnutých zo stránok výrobcov — všetky suché veterinárne diéty Royal Canin, Hill's, Brit, Farmina, Calibra, Virbac HPM, Trovet a Eminent a všetky granule Pro Plan / Pro Plan Veterinary Diets z CZ, SK a UK ([časti 4.3–4.4](#4))**

> **Čo toto je.** Osobný prieskum suchých krmív na tráviace problémy, zostavený s pomocou AI (Claude, Anthropic). Všetky údaje sú doslovne prevzaté zo stránok výrobcov a uložené v [`raw_data/`](raw_data/) (ručne overené v `gi_dry.json`); prepočty robí [`build_dataset.py`](build_dataset.py).
>
> **Čo toto nie je.** Nie je to veterinárne odporúčanie. Veterinárne diéty sú určené na podávanie po konzultácii s veterinárom — ten musí najprv zistiť, prečo má mačka tráviace problémy. Žiadna diéta nenahradí vyšetrenie.
>
> Interaktívna tabuľka: [bernysk.github.io/catfood/granule](https://bernysk.github.io/catfood/granule/) · Prieskum mokrého krmiva: [`../mokre-krmivo/`](../mokre-krmivo/)

---

## Obsah

1. [Prečo bez známky](#1)
2. [Metodika](#2)
3. [Čo hovoria štúdie o GI diétach](#3)
4. [Výsledky](#4)
5. [Kontrola prilepeného zoznamu produktov](#5)
6. [Kitten verzie pre dospelé mačky?](#6)
7. [Ako to použiť v praxi](#7)
8. [Obmedzenia](#8)
9. [Zdroje](#9)

---

<a id="1"></a>
## 1. Prečo bez známky

Rámec A–E z prieskumu mokrého krmiva je postavený pre zdravú mačku: odmeňuje veľa bielkovín, málo sacharidov a „čistú etiketu". Gastrointestinálne diéty sú zámerne iné — sú vysoko stráviteľné, často obsahujú ryžu a hydrolyzované bielkoviny, niektoré majú úmyselne veľa vlákniny. V rámci A–E by vychádzali zle bez toho, aby to čokoľvek hovorilo o tom, či fungujú.

Preto sa tu diéty **porovnávajú podľa toho, čo majú robiť**, a to všetko **na 1000 kcal**, teda na množstvo, ktoré mačka naozaj zje. Granule majú 3 300 – 4 300 kcal/kg; porovnávanie percent z etikety by zvýhodňovalo energeticky riedke krmivá.

---

<a id="2"></a>
## 2. Metodika

### Zdroje

- **Iba stránky výrobcov** pre SK alebo CZ trh, načítané v prehliadači (vrátane skrytých záložiek a dát vykresľovaných JavaScriptom). E-shopy sa nepoužili — popisy na nich bývajú zastarané.
- Výrobcovia bez dohľadateľnej stránky s etiketou pre SK/CZ sú vymenovaní ako **nezaradení** (Josera, Trovet, Specific, Monge, Brit High Fibre/Low Fat) — pozri `not_included` v surových dátach. *(Oprava v1.2: RC Gastrointestinal Moderate Calorie na SK webe je — chýba len vo výpise produktov, ale je v sitemap; teraz je zaradená.)*
- Prilepený zoznam produktov (z inej AI konverzácie) slúžil len ako východisko; každé jeho tvrdenie bolo overené na stránke výrobcu ([časť 5](#5)).

### Energia

Výrobcovia granúl takmer nikdy nedeklarujú vlhkosť a nie všetci uvádzajú energiu. Poradie zdrojov:

1. **metabolizovateľná energia z etikety** (8 produktov),
2. **tabuľka priemerného obsahu od výrobcu** (Hill's, 4 produkty) — nie je to zákonná deklarácia, ale výrobca ju zverejňuje,
3. **odhad modifikovaným Atwaterom** (3,5 / 8,5 / 3,5 kcal/g) s predpokladanou vlhkosťou 8 % (2 produkty: RC Hairball, RC Digestive Care). V tabuľke označené hviezdičkou.

Purina uvádza energiu ako „4,15" bez jednotky; zodpovedá kcal/g (britská stránka toho istého produktu: 415 kcal/100 g).

### Čo sa porovnáva

| Ukazovateľ | Prečo |
|---|---|
| Energetická hustota (kcal/kg) | Vyššia = menšia porcia, menej objemu v čreve — RC to uvádza ako zámer. |
| Bielkoviny, tuk na 1000 kcal; tuk ako % energie | Porovnateľnosť medzi krmivami; FEDIAF minimá sú tiež na 1000 kcal. |
| Vláknina (hrubá) a jej druh | Psyllium, FOS, inulín, repné rezky, celulóza majú rozdielny účinok ([časť 3](#3)). |
| Sodík a draslík | Nariadenie EÚ 2020/354 vyžaduje pre diéty na poruchy vstrebávania Na ≥ 0,18 % a K ≥ 0,5 %. |
| Fosfor na 1000 kcal, Ca:P | Dôležité pri dlhodobom kŕmení, seniorských mačkách a pri obličkách. |
| Zdroje bielkovín, hydrolyzáty | Pri podozrení na potravinovú citlivosť záleží na počte a druhu bielkovín. |
| Pro-/paraprobiotiká, anorganické fosforečnany | Uvádzané v zložení, prečítané s porozumením. |
| Deklarovaná doba podávania | Diétne krmivá ju musia uvádzať. |

**Polia čítané s porozumením** (nie regexom): zdroje bielkovín a druhy vlákniny sú prečítané zo zloženia a uložené pri každom produkte, aby sa dali skontrolovať.

---

<a id="3"></a>
## 3. Čo hovoria štúdie o GI diétach

### 3.1 Samotná zmena na stráviteľnú diétu často pomôže — obsah tuku nie je rozhodujúci

**Laflamme a kol. 2011** (*JVIM*, randomizovaná, zaslepená, 55 mačiek s chronickou hnačkou, 6 týždňov) porovnávali dve vysoko stráviteľné diéty líšiace sa len tukom (23 % vs. 45 % energie). **Zlepšilo sa 78 % mačiek bez ohľadu na obsah tuku**; zlepšenie prišlo zvyčajne do prvého týždňa a maximum do 3 týždňov. Na rozdiel od psov teda nízkotučná diéta nie je u mačiek s hnačkou podmienkou. (Štúdia financovaná Nestlé Purina.)

V tomto prieskume majú diéty 38–55 g tuku na 1000 kcal (35–50 % energie) — z pohľadu dôkazov to nie je dôvod jednu preferovať.

### 3.2 Asi polovica mačiek s chronickými tráviacimi problémami reaguje na zmenu stravy

**Guilford a kol. 2001** (*JVIM*, 55 mačiek s chronickými idiopatickými GI problémami): **49 % reagovalo na zmenu stravy** a u 29 % sa potvrdila potravinová citlivosť (návrat príznakov po opätovnom podaní pôvodného krmiva). Polovica z nich reagovala na viac zložiek. Krvné testy IgE nepomohli.

Prakticky: pri chronických ťažkostiach má zmysel krmivo s **malým počtom a inými zdrojmi bielkovín** než doterajšie. V prieskume: Brit (sleď, losos, bez hydiny v bielkovinách a bez obilnín), Calibra (losos, vajcia), Purina EN (deklaruje „omezený počet zdrojů bílkovin" — sója, kura).

### 3.3 Porovnanie dvoch suchých GI diét

**Perea a kol. 2017** (*Frontiers in Vet. Science*, randomizovaná, zaslepená, 28 analyzovaných mačiek s chronickým vracaním/hnačkou, 4 týždne): Iams Intestinal vs. **Hill's i/d**. Vracanie kleslo pri oboch, medzi diétami štatisticky významný rozdiel nebol; v poslednom týždni bez vracania 67 % vs. 47 % mačiek. Malá štúdia, bez kontrolnej skupiny, financovaná výrobcom jednej z diét (P&G). Záver autorov: GI diéta samotná môže pomôcť; pri neúspechu ďalšia diagnostika a hydrolyzovaná/eliminačná diéta. (PDF v [`literatura/`](../literatura/).)

### 3.4 Psyllium pri zápche

**Rochon a kol. 2026** (*JFMS*, 6-mesačná kontrolovaná, zaslepená, multicentrická štúdia, mačky s chronickou zápchou): diéta so **6 % psyllia** vs. 0,5 % — zlyhanie diéty 26,9 % vs. 73,3 %. Na SK trhu má práve 6 % psyllia **Royal Canin Gastrointestinal Fibre Response** (deklarované „psyllium husks and seeds (6%)"). Ostatné produkty majú psyllium 0,5 % alebo bez uvedeného množstva.

### 3.5 Vláknina: hrubá vláknina na etikete nevyjadruje rozpustnú vlákninu

„Hrubá vláknina" je stará laboratórna metóda, ktorá zachytí hlavne nerozpustnú vlákninu (celulózu). Rozpustné vlákniny ako psyllium či inulín v nej takmer nie sú. Príklad: **Fibre Response má 6 % psyllia, ale len 3 % hrubej vlákniny.** Číslo „vláknina %" preto treba čítať spolu s druhom vlákniny v zložení.

### 3.6 Pravidlá EÚ pre diétne krmivá

Nariadenie EÚ **2020/354** (príloha, časť B) určuje, aké účely smie diétne krmivo uvádzať a ako dlho:

| Účel | Požiadavka | Odporúčaná doba |
|---|---|---|
| Kompenzácia zlého trávenia (maldigescia) | vysoká stráviteľnosť | zo začiatku do 12 týždňov; celoživotne pri chronickej nedostatočnosti pankreasu |
| Zníženie porúch črevného vstrebávania | stráviteľnosť + Na ≥ 1,8 g/kg, K ≥ 5 g/kg | do 12 týždňov |
| Zníženie akútnych porúch vstrebávania | elektrolyty + ≥ 32 % ľahko stráviteľných sacharidov | 1–7 dní |

Všetky produkty, ktoré sodík a draslík deklarujú, požiadavku na elektrolyty spĺňajú. **Brit** uvádza pri akútnych poruchách „1–2 týždne", čo nezodpovedá aktuálnemu nariadeniu (1–7 dní) — pravdepodobne prevzaté zo staršej smernice.

---

<a id="4"></a>
## 4. Výsledky

Hviezdička pri energii = nie je z etikety (tabuľka priemerného obsahu Hill's alebo odhad). Prázdne pole = výrobca údaj nezverejňuje.

| Produkt | Typ | kcal/kg | Bielk. g/1000 kcal | Tuk g/1000 kcal | Tuk % E | Vlák. % | P g/1000 kcal | Ca:P | Na/K % | Psyllium |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Royal Canin VHN Cat Gastrointestinal | diéta | 4095 | 78 | 54 | 48 | 4,8 | – | – | 0,60/1,00 | áno |
| Royal Canin VHN Cat Gastrointestinal Kitten | diéta | 4334 | 81 | 55 | 50 | 2,0 | – | – | 0,70/0,90 | áno |
| Royal Canin VHN Cat Gastrointestinal Fibre Response | diéta | 3903 | 79 | 38 | 35 | 3,0 | – | – | –/– | **6 %** |
| Royal Canin VHN Cat Gastrointestinal Hairball | diéta | 3332* | 108 | 42 | 36 | 7,5 | – | – | 1,00/0,74 | 0,48 % |
| Royal Canin Digestive Care | bežné | 3568* | 106 | 42 | 36 | 3,3 | – | – | –/– | 0,50 % |
| Hill's Prescription Diet i/d | diéta | 3988* | 90 | 47 | 40 | 2,2 | 1,81 | 1,38 | 0,37/0,94 | – |
| Hill's Prescription Diet i/d Kitten | diéta | 4074* | 92 | 53 | 45 | 2,8 | 2,36 | 1,46 | 0,40/0,94 | – |
| Hill's Prescription Diet Gastrointestinal Biome | diéta | 3786* | 95 | 45 | 38 | 5,3 | 1,64 | 1,27 | 0,29/0,87 | – |
| Hill's Prescription Diet Gastrointestinal Biome Stress | diéta | 3786* | 95 | 45 | 38 | 5,3 | 1,64 | 1,27 | 0,29/0,87 | – |
| Purina Pro Plan Veterinary Diets EN Gastrointestinal | diéta | 4150 | 96 | 48 | 44 | 2,0 | 3,13 | 1,15 | 0,54/0,71 | – |
| Brit GF Veterinary Diets Cat Gastrointestinal | diéta | 3840 | 89 | 44 | 40 | 3,0 | 2,34 | 1,22 | 1,00/0,50 | 0,50 % |
| Calibra VD Cat Gastrointestinal & Pancreas | diéta | 3970 | 98 | 45 | 40 | 1,5 | 2,27 | 1,22 | 0,90/0,80 | – |
| Farmina Vet Life Gastrointestinal Feline | diéta | 4253 | 78 | 51 | 46 | 1,7 | 2,12 | 1,11 | 0,50/0,90 | áno |

### 4.1 Hlavné zistenia

- **Bielkoviny:** štyri diéty (RC Gastrointestinal, RC GI Kitten, RC Fibre Response, Farmina) majú 78–81 g/1000 kcal — **mierne pod minimom FEDIAF 2025 pre kastrovanú dospelú mačku** (83,3 g/1000 kcal), hoci nad minimom pre aktívnu dospelú mačku (62,5) aj pre rast (70–75). Pri časovo obmedzenej diéte to nie je problém; pri dlhodobom kŕmení kastrovanej mačky, ktorá zje málo kalórií, áno (pozri [prieskum mokrého krmiva, časť 3.6](../mokre-krmivo/Prieskum_mokre_krmivo_macky.md#3)).
- **Fosfor** sa medzi diétami líši takmer dvojnásobne: od 1,64 g/1000 kcal (Hill's Gastrointestinal Biome) po **3,13 g/1000 kcal (Purina EN)**. Všetky sú pod predbežným maximom 5 g/1000 kcal (AAFCO). **Royal Canin fosfor ani vápnik pri GI diétach na SK webe nedeklaruje.**
- **Anorganický fosforečnan:** Farmina má v zložení **dihydrogenfosforečnan sodný** — práve tú rozpustnú formu fosforu, ktorá v štúdii Alexander a kol. 2019 pri ~1,5 g/1000 kcal spôsobila zmeny obličiek u zdravých mačiek. Množstvo výrobca neuvádza; celkový fosfor (2,12 g/1000 kcal) je v bežnom pásme.
- **Vláknina:** vysokovlákninové sú Hill's Gastrointestinal Biome (5,3 % hrubej vlákniny, 9,6 % zmesi ActivBiome+) a RC Hairball (7,5 %). RC Fibre Response je vysokovlákninová hlavne vďaka rozpustnému psylliu, čo hrubá vláknina neukáže.
- **Probiotiká:** živé probiotikum (Enterococcus faecium) má len **Brit**; Calibra obsahuje **paraprobiotikum** (inaktivované baktérie). Ostatné majú prebiotiká.
- **Hydrolyzované zložky** má väčšina, ale **ani jedna z týchto diét nie je hypoalergénna** v zmysle úplne hydrolyzovanej bielkoviny. Na eliminačnú diétu pri podozrení na alergiu existujú samostatné produkty (RC Hypoallergenic/Anallergenic, Purina HA, Hill's z/d).
- **Bez obilnín** je len Brit (pohánka, hrach). Pri GI diétach to nie je výhoda samo osebe — ryža je dobre stráviteľná.
- **Digestive Care** od Royal Canin **nie je veterinárna diéta**; prvou zložkou je pšeničný glutén a výrobca neuvádza energiu, minerály ani taurín.

### 4.2 Doplnené porovnanie: bežné krmivá Pro Plan a diéty na chudnutie

Na žiadosť autora pribudlo šesť granúl, ktoré **nie sú gastrointestinálne diéty**. V tabuľke majú vlastnú kategóriu, aby sa s GI diétami nemiešali. Údaje sú zo stránok výrobcov (purina.cz, royalcanin.com/sk); pri bežných krmivách Pro Plan CZ/SK stránka neuvádza energiu, minerály ani taurín.

**Kontrola britskej stránky výrobcu (purina.co.uk).** Pri Kitten Healthy Start, Delicate Digestion a OM sú britské zloženie (poradie aj percentá zložiek), analytické zložky a doplnkové látky **totožné s CZ** — ide o tú istú receptúru. Závod výroby neuvádza ani jedna stránka (dá sa zistiť len z kódu na obale), pri totožnej receptúre to však na údaje z etikety nemá vplyv. Pri Kitten a Delicate Digestion je preto energia prevzatá z UK stránky (4 255 a 4 140 kcal/kg); Atwaterov odhad bol o 8 % nižší. Sterilised Renal Plus losos ani Derma Care sa v UK nepredávajú (britský Renal Plus kura je iná receptúra s 36 % bielkovín), pri nich ostáva odhad. Hviezdička = energia nie je zo SK/CZ etikety.

| Produkt | Kategória | kcal/kg | Bielk. g/1000 kcal | Tuk g/1000 kcal | Tuk % E | Vlák. % | Taurín mg/kg |
|---|---|---:|---:|---:|---:|---:|---:|
| Pro Plan Adult 1+ Sterilised Renal Plus losos | bežné krmivo | 3418* | 120 | 35 | 30 | 4,0 | – |
| Pro Plan Adult Delicate Digestion morka | citlivé trávenie (bežné) | 4140* (UK) | 97 | 43 | 40 | 1,5 | – |
| Pro Plan Kitten Healthy Start kura | bežné krmivo (rast) | 4255* (UK) | 94 | 47 | 43 | 1,0 | – |
| Pro Plan Adult Derma Care losos | bežné krmivo | 3582* | 100 | 45 | 38 | 5,5 | – |
| Pro Plan Veterinary Diets OM St/Ox Obesity Management | diéta – chudnutie | 3400 | 141 | 24 | 22 | 7,5 | 1000 |
| Royal Canin VHN Cat Satiety Weight Management | diéta – chudnutie | 3040 | 112 | 30 | 27 | 14,6 | – |

- **„Renal Plus" nie je renálna diéta.** Je to bežné krmivo pre kastrované mačky s vysokým obsahom bielkovín (≈ 120 g/1000 kcal). Tvrdenie „podporuje zdraví ledvin" sa z etikety nedá overiť, lebo **fosfor ani iné minerály nie sú deklarované** — a práve fosfor je pre obličky podstatný (pozri [prieskum mokrého krmiva, časť 3.6](../mokre-krmivo/Prieskum_mokre_krmivo_macky.md#3)). Mačke s diagnostikovaným ochorením obličiek patrí veterinárna renálna diéta (Ross a kol. 2006), nie toto krmivo. Pre zdravú kastrovanú mačku je to obyčajné kompletné krmivo s dostatkom bielkovín.
- **Delicate Digestion** je bežné krmivo s čakankovým koreňom (inulín). Oproti GI diétam nemá deklarovanú stráviteľnosť, zvýšené elektrolyty ani dobu podávania. Rozumná voľba na dlhodobé kŕmenie mačky s mierne citlivým trávením; pri hnačke alebo zvracaní nenahrádza diétu.
- **Kitten Healthy Start** je rastové krmivo (1–12 mesiacov, aj pre gravidné a dojčiace mačky). Vápnik a fosfor stránka neuvádza, takže splnenie miním FEDIAF pre rast sa nedá overiť.
- **Derma Care**: druhou zložkou je pšenica; vláknina 5,5 %, omega-3 0,6 %.
- **Diéty na chudnutie** majú najnižšiu energetickú hustotu v celom porovnaní (3 040–3 400 kcal/kg) a vysoký podiel bielkovín na kalóriu — **OM 141 g/1000 kcal**, čo je v súlade so štúdiou Laflamme & Hannah 2005 (viac bielkovín pri chudnutí = menšia strata svalov). **Satiety** stavia na vláknine (14,6 %, najviac zo všetkých 19 produktov). Prvými zložkami OM sú pšeničný lepok, kukuričná bielkovina a sójová múka.
- Pri žiadnom z týchto šiestich produktov výrobca neuvádza fosfor, vápnik ani horčík a okrem OM ani taurín.

### 4.3 Všetky granule Pro Plan a všetky suché veterinárne diéty Royal Canin (automaticky stiahnuté)

Na žiadosť autora boli stiahnuté **všetky** granule Pro Plan a Pro Plan Veterinary Diets zo stránok purina.cz, purina.sk a purina.co.uk a **všetky suché veterinárne diéty Royal Canin** zo SK stránky (78 nových riadkov). Robia to skripty [`scrape_proplan.py`](scrape_proplan.py) a [`scrape_royalcanin.py`](scrape_royalcanin.py); surové dáta sú v `raw_data/proplan_dry.json` a `raw_data/royalcanin_vet.json`, prevod do tabuľky v [`scraped.py`](scraped.py).

**Ako sa sťahovalo**
- Stránkovanie výpisov Purina v prehliadači nefunguje; server však vracia každú stranu (`?page=N`) správne, takže skript číta odkazy priamo z HTML. Výpis „granule" na purina.cz vynecháva časť veterinárnych diét — skript preto prechádza aj všeobecný výpis.
- **purina.eu**: všetkých 7 produktových stránok vrátilo **chybu servera (HTTP 500)**. Rovnaké produkty (rovnaké adresy) sú na purina.co.uk, odkiaľ sú zaradené.
- Royal Canin skrýva časť produktov vo výpise; skript berie zoznam zo **sitemap** (SK aj CZ: zhodne 33 suchých diét + 1 tekutá, ktorá nie je zaradená). Do tabuľky ide SK verzia; CZ je ten istý sortiment s rovnakými ID produktov.
- Produkty, ktoré už boli ručne overené (časti 4.1–4.2), sa nezdvojujú.
- **Kategória** sa priraďuje podľa názvu produktu (tabuľka pravidiel v `scraped.py`), **druhy vlákniny** automaticky zo zloženia, **zdroje bielkovín sa pri stiahnutých produktoch neurčujú**. V tabuľke majú tieto riadky štítok „auto".
- **Energia**: z etikety, ak ju stránka uvádza; inak z rovnakého produktu na inom trhu, ak má zhodné deklarované bielkoviny, tuk, popol a vlákninu (28 produktov — zväčša bežné Pro Plan CZ/SK s energiou z UK); inak Atwaterov odhad (21 produktov). Zdroj je pri každom produkte v detaile.
- Rovnaké deklarované hodnoty na viacerých trhoch má 49 riadkov (37 vo všetkých troch krajinách).

**Prehľad podľa kategórie (stav verzie 1.2, 97 granúl; aktuálny prehľad všetkých 161 je v [časti 4.4](#4))**

| Kategória | n | Bielkoviny g/1000 kcal — medián (rozsah) | Fosfor g/1000 kcal — medián (rozsah; počet s deklarovaným P) | kcal/kg (medián) |
|---|---:|---|---|---:|
| bežné krmivo | 25 | 101 (90–114) | nedeklarovaný (0) | 3850 |
| GI diéta | 16 | 93 (77–108) | 2,30 (1,64–3,13; 10) | 4012 |
| diéta – močové cesty | 13 | 94 (76–112) | 2,37 (1,76–3,41; 13) | 3557 |
| diéta – obličky | 12 | 70 (59–79) | 0,92 (0,74–1,41; 12) | 3852 |
| citlivé trávenie (bežné krmivo) | 6 | 102 (97–107) | nedeklarovaný (0) | 3945 |
| diéta – chudnutie | 6 | 128 (110–141) | 3,69 (1 produkt) | 3249 |
| diéta – alergie | 5 | 96 (66–96) | nedeklarovaný (0) | 3640 |
| diéta – pečeň | 4 | 66 (63–66) | nedeklarovaný (0) | 4240 |
| diéta – diabetes | 3 | 119 | nedeklarovaný (0) | 4190 |
| ostatné veterinárne (udržiavacie, stres, srdce, zuby, kĺby, koža) | 7 | 78–134 | 1,67–2,85 (4) | — |

**Čo z toho vyplýva**
- **Renálne diéty** majú fosforu najmenej (0,74–1,41 g/1000 kcal, polovica až tretina oproti GI diétam) a bielkoviny mierne obmedzené (59–79 g/1000 kcal). „Ranné" verzie (Pro Plan NF Early Care, RC Early Renal) sú na hornej hranici — 76–79 g bielkovín a 0,9–1,4 g fosforu na 1000 kcal — teda blízko „mierneho obmedzenia" zo štúdie Schauf a kol. 2021 (76–98 g bielkovín, 1,4–1,6 g P). Pre porovnanie: bežné krmivo **Pro Plan „Renal Plus" má ~120 g bielkovín na 1000 kcal a fosfor nedeklaruje** — je to iný typ krmiva ([časť 4.2](#4)).
- **Bežné krmivá Pro Plan** (25 + 6 riadkov naprieč trhmi) neuvádzajú fosfor, vápnik ani horčík na žiadnej z troch stránok; veterinárne diéty Pro Plan a Royal Canin ich uvádzajú takmer vždy.
- **Royal Canin** uvádza fosfor pri renálnych a močových diétach, ale pri GI diétach nie.
- Pribudli dve GI diéty Royal Canin, ktoré v ručnom výbere chýbali: **Gastrointestinal Moderate Calorie** (menej tuku, 35 g/1000 kcal) a **CA Gastrointestinal Hydrolysed Protein** (hydrolyzovaná bielkovina, 77 g bielkovín/1000 kcal).
- Kategórie z názvu sú pomôcka na filtrovanie, nie klasifikácia účelu podľa EÚ — napr. „Neutered Satiety Balance" je zaradená medzi diéty na chudnutie, hoci je to udržiavacia diéta pre kastrované mačky.

### 4.4 Ďalší výrobcovia dostupní na SK/CZ: Hill's, Brit, Farmina, Calibra, Virbac, Trovet, Eminent

Verzia 1.3 dopĺňa **všetky suché veterinárne diéty pre mačky** ďalších siedmich výrobcov, ktorých stránka uvádza etiketu (67 nových riadkov). GI diéty týchto značiek boli ručne overené už v časti 4.1 a nezdvojujú sa.

| Výrobca | Stránka | Počet | Ako sa sťahovalo |
|---|---|---:|---|
| Hill's Prescription Diet | hillspet.cz | 21 | stránka blokuje skripty (HTTP 403) → text etikety načítaný vstavaným prehliadačom (`raw_data/hills_vet.json`) |
| Brit Veterinary Diets | brit.pet/sk | 10 | skript [`scrape_others.py`](scrape_others.py) |
| Farmina Vet Life | farmina.com/cz | 12 | skript; konzerva 85 g vynechaná (nie granule) |
| Calibra VD | mojacalibra.sk | 3 | stránka skriptu vráti prázdnu stránku → vstavaný prehliadač (`raw_data/calibra_vet.json`) |
| Virbac Veterinary HPM | sk.virbac.com | 9 | skript; analytické zložky sú tabuľka bez znaku % (stĺpec „% v krmive“) |
| Trovet | trovet.com (anglicky) | 9 | skript; **výrobca nemá SK/CZ stránku**, použitá anglická; doplnkové látky stránka neuvádza |
| Eminent Diet (Tekro, CZ) | krmivo-eminent.cz | 3 | vstavaný prehliadač; zloženie zo stránky, analytické hodnoty a energia z PDF tabuľky výrobcu odkázanej zo stránky (`raw_data/eminent_vet.json`); sodík, draslík, horčík a vlhkosť neuvádza |

**Nezaradené** (stránka výrobcu s etiketou sa nenašla alebo je zastaraná; e-shopy sa nepoužívajú): Specific (specific-diets.com – 404), Josera Help (josera.com/sk a /cs líniu pre mačky nezobrazuje), Monge VetSolution (len PDF listy z rokov 2016–2019, väčšinou mokré verzie a bez energie). Trovet má 6 ďalších diét pre mačky len v mokrej forme (Renal Venison, Hypoallergenic Horse/Turkey/Venison, Recovery Liquid) – nie sú zaradené.

**Opravy oproti verzii 1.2**
- Brit **Gastrointestinal Low Fat** a **Gastrointestinal High Fibre** na brit.pet sú (v1.2 ich uvádzala ako nenájdené) — sú zaradené.
- Brit **Ultra-hypoallergenic** je na báze **hmyzu** (sušený hmyz 30 %), nie lososa.
- Trovet **Intestinal** má stránku výrobcu (anglickú) — zaradený.

**Prehľad podľa kategórie (stav pred doplnením Eminent, 161 granúl)**

| Kategória | n | Bielkoviny g/1000 kcal — medián (rozsah) | Fosfor g/1000 kcal — medián (rozsah; počet s deklarovaným P) | kcal/kg (medián) |
|---|---:|---|---|---:|
| diéta – močové cesty | 27 | 92 (74–118) | 1,89 (1,47–3,41; 27) | 3800 |
| bežné krmivo | 25 | 101 (90–114) | nedeklarovaný (0) | 3850 |
| diéta – obličky | 22 | 69 (58–99) | 1,04 (0,74–1,56; 22) | 4020 |
| GI diéta | 19 | 92 (77–108) | 2,27 (1,64–3,13; 13) | 3988 |
| diéta – chudnutie | 14 | 117 (110–141) | 2,49 (1,85–3,69; 9) | 3400 |
| diéta – alergie | 14 | 76 (66–96) | 2,17 (1,30–3,27; 9) | 3720 |
| diéta – diabetes | 9 | 121 (111–133) | 2,70 (1,83–3,38; 6) | 3787 |
| diéta – pečeň | 7 | 66 (63–83) | 1,57 (1,54–2,45; 3) | 4136 |
| citlivé trávenie (bežné krmivo) | 6 | 102 (97–107) | nedeklarovaný (0) | 3945 |
| ostatné veterinárne (udržiavacie, stres, srdce, zuby, kĺby, koža, štítna žľaza) | 18 | 67–134 | 1,53–3,12 (16) | — |

**Obličkové diéty (22) — bielkoviny a fosfor na 1000 kcal**

| Diéta | Bielkoviny g | Fosfor g |
|---|---:|---:|
| Brit GF VD Renal | 58 | 1,00 |
| Farmina Vet Life Renal | 58 | 0,94 |
| RC CA Renal – Mobility | 59 | 0,74 |
| Trovet Renal & Oxalate RID | 61 | 1,17 |
| Calibra VD Renal & Cardiac | 61 | 1,02 |
| RC Renal / Renal Select / CA Renal-Hypoallergenic | 62–63 | 0,81–1,05 |
| Hill's k/d, k/d + Mobility | 68 | 1,09–1,17 |
| Pro Plan NF Advanced Care | 69 | 0,82 |
| RC Renal Special | 71 | 1,22 |
| Virbac HPM Advanced Kidney & Joint KJ3 | 72 | 1,20 |
| RC CA Early Renal – Mobility | 76 | 1,34 |
| Pro Plan NF Early Care | 76 | 0,92 |
| Hill's k/d Early Stage | 78 | 1,14 |
| RC Early Renal | 79 | 1,41 |
| Virbac HPM Kidney & Joint KJ2 | 85 | 1,33 |
| Virbac HPM Early Kidney & Joint KJ1 | 99 | 1,56 |

**Čo z toho vyplýva**
- **Renálne diéty všetkých výrobcov** sa zhodujú v tom podstatnom: fosfor 0,74–1,41 g/1000 kcal (okrem Virbac KJ1/KJ2) a bielkoviny 58–79 g/1000 kcal. Najnižší fosfor majú stále RC CA Renal – Mobility, RC Renal a Pro Plan NF Advanced Care (0,74–0,82 g); najnižšie bielkoviny Brit a Farmina.
- **Eminent Diet** (doplnený neskôr, 3 diéty): Gastrointestinal Hypoallergenic/Hepatic má 86 g bielkovín a 2,19 g fosforu na 1000 kcal, jedinou bielkovinou sú ryby (hydrolyzovaný losos); Renal/Urinary 70 g bielkovín a 1,61 g fosforu — fosforu má zo všetkých renálnych diét najviac; Struvite 75 g bielkovín.
- **Virbac KJ1 a KJ2** sú kombinované diéty „obličky + kĺby“ pre skoré štádiá (IRIS 2, resp. počiatočná fáza): KJ1 má 99 g bielkovín a 1,56 g fosforu na 1000 kcal — to je bližšie bežnému krmivu pre seniorov než renálnej diéte. Do kategórie „obličky“ ich dalo pravidlo podľa názvu („Kidney“).
- **Diabetické diéty** sú všetky vysokobielkovinové (111–133 g/1000 kcal) s nízkym podielom energie zo sacharidov (NFE 14–21 % energie); výnimkou je **Trovet Weight & Diabetic** s 39 % energie z NFE.
- **Močové diéty** sa delia na dve skupiny podľa sodíka: s vysokým sodíkom (≥ 2,9 g/1000 kcal — RC S/O, Pro Plan UR, Calibra, Brit, Virbac U1–U3), ktorý zvyšuje príjem vody a riedi moč, a s nízkym sodíkom (Hill's c/d a s/d, Farmina, Trovet ASD, RC S/O Bladder Comfort Ageing: 0,6–1,4 g); Trovet Urinary Calm je medzi nimi (2,0 g).
- **Virbac U2 a U3** majú na stránke úplne rovnaké analytické zložky a energiu — líšia sa len deklarovaným účelom.
- **Hill's** uvádza energiu na etikete len pri 7 z 21 diét; pri ostatných je použitý „priemerný obsah“ z tabuľky výrobcu na tej istej stránke (zdroj je pri každom produkte v detaile). Pri m/d je energia na etikete v MJ/kg (16,5 MJ/kg = 3 944 kcal/kg).
- Kontrola elektrolytov podľa nariadenia EÚ 2020/354, položky 20 (Na ≥ 0,18 %, K ≥ 0,5 %), platí len pre GI diéty. Pri iných diétach sa v tabuľke zobrazuje iba informatívne — napr. Brit Struvite má draslík 0,45 %, čo pre močovú diétu nie je chyba.

---

<a id="5"></a>
## 5. Kontrola prilepeného zoznamu produktov

| Tvrdenie zo zoznamu | Stránka výrobcu | Stav |
|---|---|---|
| RC Gastrointestinal: 400 g, 2 kg, 4 kg | 400 g, 2 kg, 4 kg | ✅ |
| RC Gastrointestinal Kitten: 400 g, 2 kg | SK web: len 400 g | ⚠️ 2 kg na webe výrobcu nie je |
| RC Digestive Care: 400 g, 1,5 / 2 / 4 / 10 kg | SK web: 400 g, 2 kg, 10 kg | ⚠️ |
| Hill's i/d: 400 g, 1,5 / 3 / 8 kg | CZ web: 8 kg | ⚠️ ostatné veľkosti na webe výrobcu nie sú |
| Hill's i/d Kitten existuje | áno, CZ web 3 kg | ✅ |
| Hill's „ActivBiome+" | áno, 4 % v i/d, 9,6 % v GI Biome | ✅ |
| Brit GI: „hydrolyzovaný sleď a žltý hrach" | **sušený sleď 40 %**, žltý hrach 18 %, **hydrolyzovaná lososová bielkovina 10 %** | ❌ hydrolyzovaný je losos, nie sleď |
| Brit GI: 400 g, 2 kg, 5 kg | 400 g, 2 kg, 5 kg | ✅ |
| Purina EN: pre dospelé aj mačiatka | „pro kočky všech věkových kategorií", kŕmna tabuľka od 6 týždňov | ✅ |
| Purina EN: 400 g, 1,5 kg, 5 kg | 400 g, 1,5 kg, 5 kg | ✅ |
| „Kitten verzie sú často ideálnou voľbou aj pre dospelé" | — | ⚠️ zjednodušené, pozri [časť 6](#6) |

Veľkosti balení sa môžu líšiť podľa predajcu a krajiny; zoznam vyššie porovnáva so stránkou výrobcu pre SK/CZ k 15. 10. 2026.

---

<a id="6"></a>
## 6. Kitten verzie pre dospelé mačky?

Prilepený zoznam odporúča Kitten verzie aj dospelým mačkám kvôli menším granulám. Dáta ukazujú, čo to znamená:

| | RC GI Adult → Kitten | Hill's i/d → i/d Kitten |
|---|---|---|
| Energia | 4 095 → **4 334 kcal/kg (+6 %)** | 3 988 → 4 074 kcal/kg (+2 %) |
| Tuk (% energie) | 48 → 50 % | 40 → 45 % |
| Fosfor | nedeklarovaný | 1,81 → **2,36 g/1000 kcal (+30 %)** |
| Vápnik | nedeklarovaný → 1,3 % | 0,99 → 1,40 % |

- **Krátkodobo** (týždne, počas tráviacich ťažkostí) je Kitten verzia pre dospelú mačku v poriadku — je to kompletné krmivo s vyšším obsahom živín.
- **Dlhodobo** pre kastrovanú dospelú mačku: viac kalórií v rovnakom objeme (riziko priberania pri kŕmení „od oka") a viac fosforu, čo je nevýhoda najmä u starších mačiek.
- **Veľkosť granúl** sa dá riešiť aj inak: granule dospelej verzie sa dajú namočiť vo vlažnej vode (Brit to výslovne uvádza), alebo zvoliť mokrú verziu tej istej diéty — na stránkach výrobcov ju majú Royal Canin, Hill's, Purina, Calibra aj Farmina.
- **Purina EN** je jedna receptúra pre všetky vekové kategórie, takže dilema odpadá.

---

<a id="7"></a>
## 7. Ako to použiť v praxi

Pre dve adoptované mačky s citlivým trávením (všeobecný postup, nie diagnóza):

1. **Najprv veterinár, nie krmivo.** U mačiek z útulku sú častou príčinou hnačky parazity a infekcie; vyšetrenie trusu a odčervenie by mali byť prvým krokom. Pri dlhodobých ťažkostiach veterinár zvyčajne zvažuje aj krvné testy (napr. vitamín B12, štítna žľaza u starších mačiek).
2. **Akútna hnačka:** GI diéta krátkodobo podľa veterinára (podľa EÚ pravidiel 1–7 dní pri akútnych poruchách).
3. **Chronické ťažkosti (> 3 týždne):** štruktúrovaný pokus s vysoko stráviteľnou GI diétou. Podľa Laflamme 2011 sa zlepšenie zvyčajne ukáže do týždňa a maximum do 3 týždňov — ak sa nič nezmení, má zmysel ďalšia diagnostika alebo eliminačná diéta s novou/hydrolyzovanou bielkovinou (Guilford 2001: polovica mačiek reaguje na zmenu stravy).
4. **Zápcha:** najlepšie doložené je psyllium v dávke ~6 % (RC Fibre Response, Rochon 2026).
5. **Iba túto diétu:** pri diétnom pokuse nekombinovať s iným krmivom ani pamlskami, inak sa výsledok nedá vyhodnotiť (Hill's to na etikete výslovne uvádza: „Podávejte pouze toto krmivo").
6. **Prechod postupne** počas 7–10 dní, pokiaľ veterinár neurčí inak.
7. **Po 12 týždňoch prehodnotiť** — väčšina diét má deklarovanú dobu „do 12 týždňov"; dlhodobé podávanie je rozhodnutie veterinára.

---

<a id="8"></a>
## 8. Obmedzenia

1. **Deklarované ≠ namerané.** Analytické zložky majú zákonnú toleranciu (pozri [prieskum mokrého krmiva, časť 9](../mokre-krmivo/Prieskum_mokre_krmivo_macky.md#9)).
2. **Stráviteľnosť nie je na etikete.** Je to hlavná vlastnosť GI diét a z dát sa nedá overiť; tvrdenia o „vysokej stráviteľnosti" sú od výrobcov. Nariadenie EÚ však pre diétne krmivá na maldigesciu vyžaduje stráviteľnosť bielkovín ≥ 85 % a tuku ≥ 90 % (pri nízkej vláknine).
3. **Vlhkosť chýba** u 18 z 19 produktov (deklaruje ju len Brit); odhady energie (4 produkty: RC Hairball, RC Digestive Care, Pro Plan Sterilised Renal Plus a Derma Care; pri dvoch ďalších Pro Plan je energia z UK stránky výrobcu pri overenej zhodnej receptúre) a podiel energie z tuku preto počítajú s predpokladanou alebo priemernou vlhkosťou.
4. **Hill's** zverejňuje energiu len v tabuľke priemerného obsahu, nie na etikete.
5. **Klinické tvrdenia výrobcov** („klinicky overené", „do 24 hodín") sa tu nehodnotia — väčšina súvisiacich štúdií je financovaná výrobcami a nie vždy publikovaná.
6. **Vybrané štúdie** sú malé (28–55 mačiek) a takmer všetky financované výrobcami krmív.
7. **Rozsah:** ručne overené sú GI diéty a porovnanie v časti 4.2; ostatné veterinárne diéty (8 výrobcov) sú automaticky stiahnuté (časti 4.3–4.4). Chýbajú výrobcovia bez stránky s etiketou (Specific, Josera Help, Monge VetSolution) a mokré diéty. Trovet je z anglickej stránky výrobcu — zloženie pre SK/CZ trh sa môže líšiť.
8. **Automaticky stiahnuté produkty** (štítok „auto“) neprešli čítaním s porozumením: kategória je z názvu, druhy vlákniny z kľúčových slov a zdroje bielkovín nie sú určené. Číselné údaje sú doslovne zo stránky výrobcu (pri Virbac je % doplnené podľa hlavičky stĺpca tabuľky).
9. **Kontrola elektrolytov EÚ 2020/354 (položka 20)** sa vzťahuje len na GI diéty; pri ostatných kategóriách je v tabuľke len informatívna.

---

<a id="9"></a>
## 9. Zdroje

**Stránky výrobcov** (jediný zdroj údajov o produktoch; odkaz pri každom produkte v [`raw_data/gi_dry.json`](raw_data/gi_dry.json)): royalcanin.com/sk, hillspet.cz, purina.cz, purina.sk, purina.co.uk, brit.pet/sk, mojacalibra.sk, farmina.com/cz, sk.virbac.com, trovet.com.

**Štúdie a regulácia**

- **Laflamme DP a kol. 2011.** Effect of diets differing in fat content on chronic diarrhea in cats. *J Vet Intern Med* 25:230–235 ([zhrnutie](https://www.dvm360.com/view/hot-literature-cats-fats-and-chronic-diarrhea))
- **Guilford WG a kol. 2001.** Food sensitivity in cats with chronic idiopathic gastrointestinal problems. *J Vet Intern Med* 15:7–13
- **Perea SC a kol. 2017.** Evaluation of two dry commercial therapeutic diets for the management of feline chronic gastroenteropathy. *Front Vet Sci* 4:69 — [doi:10.3389/fvets.2017.00069](https://doi.org/10.3389/fvets.2017.00069) (CC BY, PDF v [`literatura/`](../literatura/))
- **Rochon a kol. 2026.** A psyllium-supplemented gastrointestinal diet is effective for the management of chronic constipation in cats: a 6-month controlled clinical trial. *J Feline Med Surg* — [doi:10.1177/1098612X261420519](https://doi.org/10.1177/1098612X261420519)
- **Alexander J a kol. 2019.** Effects of the long-term feeding of diets enriched with inorganic phosphorus on the adult feline kidney and phosphorus metabolism. *Br J Nutr* 121:249–269 (PDF v [`literatura/`](../literatura/))
- **Ross SJ a kol. 2006.** Clinical evaluation of dietary modification for treatment of spontaneous chronic kidney disease in cats. *JAVMA* 229:949–957
- **Laflamme DP, Hannah SS 2005.** Increased dietary protein promotes fat loss and reduces loss of lean body mass during weight loss in cats. *Intern J Appl Res Vet Med* 3:62–68
- **Nariadenie Komisie (EÚ) 2020/354** — zoznam zamýšľaných účelov krmív na osobitné výživové účely, príloha časť B ([legislation.gov.uk](https://www.legislation.gov.uk/eur/2020/354/annex/part/B))
- **FEDIAF Nutritional Guidelines 2025**, tabuľka III-4b — [PDF](https://europeanpetfood.org/wp-content/uploads/2025/09/FEDIAF-Nutritional-Guidelines_2025-ONLINE.pdf)
- **AAFCO Expert Panel on Ca & P (2025)** — predbežné maximum fosforu 5 g/1000 kcal — [PDF](https://www.aafco.org/wp-content/uploads/2026/08/PFC-Expert_Panel_Ca-P_WGRprt.pdf)

---

*Vygenerované z [`dataset.json`](dataset.json) skriptom [`build_dataset.py`](build_dataset.py). Rekonštrukcia: `python granule/build_dataset.py`.*
