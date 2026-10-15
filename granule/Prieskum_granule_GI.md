# Granule pre mačky: gastrointestinálne diéty (SK/CZ)

**Verzia 1 · október 2026 · 13 produktov od 6 výrobcov · údaje výhradne zo stránok výrobcov**

> **Čo toto je.** Osobný prieskum suchých krmív na tráviace problémy, zostavený s pomocou AI (Claude, Anthropic). Všetky údaje sú doslovne prevzaté zo stránok výrobcov a uložené v [`raw_data/gi_dry.json`](raw_data/gi_dry.json); prepočty robí [`build_dataset.py`](build_dataset.py).
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
- Výrobcovia bez dohľadateľnej stránky s etiketou pre SK/CZ sú vymenovaní ako **nezaradení** (Josera, Trovet, Specific, Monge, RC Moderate Calorie, Brit High Fibre/Low Fat) — pozri `not_included` v surových dátach.
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
3. **Vlhkosť chýba** u 12 z 13 produktov (deklaruje ju len Brit); odhady energie (2 produkty) a podiel energie z tuku preto počítajú s predpokladanou alebo priemernou vlhkosťou.
4. **Hill's** zverejňuje energiu len v tabuľke priemerného obsahu, nie na etikete.
5. **Klinické tvrdenia výrobcov** („klinicky overené", „do 24 hodín") sa tu nehodnotia — väčšina súvisiacich štúdií je financovaná výrobcami a nie vždy publikovaná.
6. **Vybrané štúdie** sú malé (28–55 mačiek) a takmer všetky financované výrobcami krmív.
7. **Rozsah:** len suché GI diéty od výrobcov s overiteľnou stránkou pre SK/CZ; ďalšie veterinárne diéty (obličky, moč, alergie, diabetes, hmotnosť) sú plánované ako ďalší krok.

---

<a id="9"></a>
## 9. Zdroje

**Stránky výrobcov** (jediný zdroj údajov o produktoch; odkaz pri každom produkte v [`raw_data/gi_dry.json`](raw_data/gi_dry.json)): royalcanin.com/sk, hillspet.cz, purina.cz, brit.pet/sk, mojacalibra.sk, farmina.com/cz.

**Štúdie a regulácia**

- **Laflamme DP a kol. 2011.** Effect of diets differing in fat content on chronic diarrhea in cats. *J Vet Intern Med* 25:230–235 ([zhrnutie](https://www.dvm360.com/view/hot-literature-cats-fats-and-chronic-diarrhea))
- **Guilford WG a kol. 2001.** Food sensitivity in cats with chronic idiopathic gastrointestinal problems. *J Vet Intern Med* 15:7–13
- **Perea SC a kol. 2017.** Evaluation of two dry commercial therapeutic diets for the management of feline chronic gastroenteropathy. *Front Vet Sci* 4:69 — [doi:10.3389/fvets.2017.00069](https://doi.org/10.3389/fvets.2017.00069) (CC BY, PDF v [`literatura/`](../literatura/))
- **Rochon a kol. 2026.** A psyllium-supplemented gastrointestinal diet is effective for the management of chronic constipation in cats: a 6-month controlled clinical trial. *J Feline Med Surg* — [doi:10.1177/1098612X261420519](https://doi.org/10.1177/1098612X261420519)
- **Alexander J a kol. 2019.** Effects of the long-term feeding of diets enriched with inorganic phosphorus on the adult feline kidney and phosphorus metabolism. *Br J Nutr* 121:249–269 (PDF v [`literatura/`](../literatura/))
- **Nariadenie Komisie (EÚ) 2020/354** — zoznam zamýšľaných účelov krmív na osobitné výživové účely, príloha časť B ([legislation.gov.uk](https://www.legislation.gov.uk/eur/2020/354/annex/part/B))
- **FEDIAF Nutritional Guidelines 2025**, tabuľka III-4b — [PDF](https://europeanpetfood.org/wp-content/uploads/2025/09/FEDIAF-Nutritional-Guidelines_2025-ONLINE.pdf)
- **AAFCO Expert Panel on Ca & P (2025)** — predbežné maximum fosforu 5 g/1000 kcal — [PDF](https://www.aafco.org/wp-content/uploads/2026/08/PFC-Expert_Panel_Ca-P_WGRprt.pdf)

---

*Vygenerované z [`dataset.json`](dataset.json) skriptom [`build_dataset.py`](build_dataset.py). Rekonštrukcia: `python granule/build_dataset.py`.*
