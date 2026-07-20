# Mokré krmivo pre mačky (kapsičky): dátový prieskum trhu

**Verzia 4 · júl 2026 · prepracované od základu**
**151 produktov · 15 značiek · všetky údaje priamo zo stránok výrobcov**

> **Čo toto je.** Osobný nutričný prieskum kapsičkového mokrého krmiva, zostavený s pomocou AI (Claude, Anthropic). Na rozdiel od predchádzajúcich verzií je **celý postavený výhradne na surových dátach stiahnutých priamo zo stránok výrobcov** — uložených v [`raw_data/`](raw_data/) ako JSON, s doslovným znením etikiet. Žiadne číslo v tomto dokumente nepochádza z e-shopu, blogu ani z pamäte modelu; každé sa dá spätne dohľadať v surovom súbore.
>
> **Čo toto nie je.** Nie je to veterinárne odporúčanie, nezávislý laboratórny test ani platený obsah. Známka A–E je **vlastný, neoficiálny rámec** — pre krmivo pre zvieratá žiadny oficiálny „Nutri-Score" neexistuje. Pri zdravotných problémoch sa poraďte s veterinárom.
>
> Interaktívna, filtrovateľná verzia všetkých dát: [`index.html`](./index.html) · Strojovo čitateľný výstup: [`dataset.json`](./dataset.json) · Staršie verzie: [`old/`](old/)

---

## Obsah

1. [Čo je na tejto verzii nové](#1)
2. [Metodika: odkiaľ sa čísla berú](#2)
3. [Vedecký základ — čo hovoria štúdie](#3)
4. [Hodnotiaci rámec A–E (prepracovaný)](#4)
5. [Výsledky podľa značiek](#5)
6. [Vetvené nutričné údaje — ako čítať tabuľky](#6)
7. [Kľúčové zistenia a anomálie](#7)
8. [Odporúčania podľa situácie](#8)
9. [Obmedzenia a čo tento prieskum nevie](#9)
10. [Zdroje](#10)

---

<a id="1"></a>
## 1. Čo je na tejto verzii nové

Predchádzajúca verzia miešala dáta od výrobcov s údajmi z e-shopov, blogov a z pamäte modelu. Táto verzia to rieši tvrdo: **staré súbory sú odložené v [`old/`](old/) a nepoužil sa z nich ani jeden údaj.** Všetko sa stiahlo nanovo.

Podstatné zmeny oproti v3:

- **Trojnásobný rozsah.** 151 produktov namiesto ~40, vrátane úplne nových značiek: **Brit** (54 produktov naprieč Premium/Care), **Ontario** (9), **Bozita** (4 multiboxy = 16 príchutí), **Meowing Heads** (4), a kompletná **Purina Pro Plan** rada vrátane veterinárnych diét (16).
- **Oprava metodickej chyby v tauríne.** Predošlá verzia porovnávala taurín v stave „ako podávané" (napr. 520 mg/kg) — lenže **FEDIAF svoje minimá udáva na sušinu.** Pri 80 % vlhkosti je to päťnásobný rozdiel. Všetky hodnoty sú teraz prepočítané na sušinu (detail v [časti 4](#4)).
- **Vetvené nutričné údaje.** Namiesto jedného čísla za produkt sa každý parameter člení na *deklarovanú hodnotu* → *prepočet na sušinu* → *čiastkové skóre*. Dá sa filtrovať a triediť podľa ktorejkoľvek vetvy ([`index.html`](./index.html)).
- **Nové štúdie (2024–2026)** vrátane dvoch prác o psylliu, ktoré v predošlej verzii chýbali — a jedna práca, ktorá **spochybňuje** sacharidovú paniku ([časť 3](#3)).
- **Priznaná neistota.** 19 produktov má vlhkosť ≥ 85 %, kde je prepočet na sušinu matematicky správny, ale krehký. Sú označené a v tabuľkách sa dajú odfiltrovať.

---

<a id="2"></a>
## 2. Metodika: odkiaľ sa čísla berú

### Reťazec spracovania

```
stránka výrobcu → raw_data/*.json (doslovný text etikety)
                → build_dataset.py (parsovanie + prepočty)
                → dataset.json + dáta vložené priamo do index.html
                → audit_parse.py (nezávislá kontrola parsovania)
```

Každý riadok v `dataset.json` si nesie polia `composition_raw`, `analytics_raw` a `additives_raw` — teda **pôvodný text, z ktorého sa číslo vyparsovalo.** Ak sa niečo zdá nesprávne, dá sa to okamžite overiť bez opätovného sťahovania.

`index.html` má dáta **vložené priamo v sebe**, takže sa otvorí obyčajným dvojklikom bez servera. (Načítavanie cez `fetch()` zo susedného súboru prehliadače z `file://` blokujú kvôli CORS — tabuľka by ostala prázdna.)

### Deľba práce: čo počíta stroj a čo sa musí prečítať

Prieskum zámerne používa dve rôzne metódy podľa toho, aká je úloha:

| Typ údaja | Metóda | Prečo |
|---|---|---|
| **Čísla z etikety** (bielkoviny, tuk, vláknina, popol, vlhkosť, taurín) | deterministický parser | Musí byť opakovateľné a spätne kontrolovateľné. |
| **Prepočty** (sušina, NFE, skóre) | deterministický výpočet | Aritmetika sa nesmie odhadovať. |
| **Kompletnosť krmiva** | prečítané s porozumením → [`curated.json`](./curated.json) | Vyžaduje pochopenie vety vrátane negácií. |

Tretí riadok je poučenie z chyby. Pôvodne som kompletnosť určoval hľadaním kľúčových slov — a to zlyhalo na vetách ako **„Complete food for adult cats (not explicitly labeled complementary)"**, kde skript našiel slovo *complementary* a označil produkt za doplnkový, hoci veta hovorí pravý opak. Takto bolo **6 produktov klasifikovaných úplne obrátene**, čo každému z nich bralo 2 body zo 14.

Riešenie: všetkých 66 unikátnych formulácií je prečítaných a klasifikovaných v [`curated.json`](./curated.json), kľúčom je doslovné znenie z etikety. Ak pribudne produkt s neznámou formuláciou, build ju **nahlási na doplnenie namiesto hádania**. Súbor obsahuje aj poznámky pri sporných prípadoch — napríklad prečo je Purina Senior označená ako „neuvedené" a nie „doplnkové" (formulácia „implied, not explicitly stated" znamená domnienku extrakcie, nie údaj zo stránky).

### Nezávislý audit číselného parsovania

K parseru patrí `audit_parse.py`, ktorý číta tie isté etikety **inou metódou** (rozsekaním textu na fragmenty namiesto hľadania jedným regexom) a hlási nezhody. Zachytil dve reálne chyby:

- **Kattovit** má anglickú etiketu s obráteným poradím („8.0% crude protein, 5.0% fat content"). Parser čítal cez čiarku a priradil každej živine hodnotu tej nasledujúcej — **všetkých päť čísel bolo posunutých o jedno.**
- **Dein Bestes (SK)** používa „obsah tukov" a „anorganické látky" namiesto tvarov, ktoré parser poznal — tuk a popol vôbec nenačítal.

Ďalšie dve chyby sa našli skôr, pri kontrole v prehliadači: regex nezachytával české „popel" (čo nafukovalo dopočet sacharidov) a ako pomenované mäso započítaval blokový súčet, keď za ním v zátvorke nasledoval druh mäsa. Aktuálny stav auditu: **1 hlásenie zo 755 kontrolovaných hodnôt, a to falošný poplach** (Royal Canin oddeľuje položky pomlčkou, ktorú audit nerozdeľuje).

### Prečo je prepočet na sušinu nutný

Mokré krmivá majú 76–89 % vody. Porovnávať „bielkoviny 8 %" v kapsičke s „bielkoviny 10 %" v inej hovorí hlavne o tom, koľko je v ktorej vody — nie o výživovej hodnote. Preto sa všetko prepočítava na **sušinu (DM)**:

```
sušina        = 100 − vlhkosť
bielkoviny DM = bielkoviny / sušina × 100
sacharidy NFE = 100 − vlhkosť − bielkoviny − tuk − vláknina − popol   (dopočet)
```

**NFE (dusíkaté látky bez dusíka)** je odhad sacharidov *dopočtom*, nie meraním. Výrobcovia sacharidy nedeklarujú, takže je to jediná dostupná cesta — ale znamená to, že sa v ňom kumulujú všetky zaokrúhľovacie chyby ostatných piatich hodnôt.

### Kde to prestáva fungovať

Pri vlhkosti ≥ 85 % je sušina ≤ 15 %, takže **posun vlhkosti o 1 p. b. hýbe každou hodnotou na sušine o niekoľko bodov.** Príklad: Ontario tuniak a losos deklaruje bielkoviny 12 % pri vlhkosti 87 % → 92,3 % bielkovín na sušine. To je nereálne vysoké číslo a je artefaktom malého menovateľa, nie dôkazom výnimočnej kvality.

Takýchto produktov je **19** (celá rada Ontario, mousse rada Brit Care, Sheba Tuna & Salmon Jelly). V dátach nesú príznak `dm_unreliable` a v [`index.html`](./index.html) sa dajú jedným prepínačom skryť. **Neignoroval som ich — označil som ich.**

### Čo sa nedalo získať

- **Ceny.** V predošlej verzii tvorili veľkú časť dokumentu, ale pochádzali z e-shopov (Tier 3) a rýchlo zastarávajú. Táto verzia ich neuvádza, s výnimkou tam, kde ich výrobca sám zverejňuje (Brit, ktorý prevádzkuje vlastný e-shop). Cenu si overte pred nákupom.
- **Horčík a fosfor** väčšina bežných značiek nedeklaruje. Riziko močových kryštálov sa preto pri nich posúdiť nedá — dáta má hlavne Royal Canin a Purina veterinárne diéty.
- **Energetická hodnota** chýba u približne polovice produktov.

---

<a id="3"></a>
## 3. Vedecký základ — čo hovoria štúdie

### 3.1 Vláknina a bezoáre — s dôležitou výhradou

**Weber a kol. 2015** (*Veterinary Medicine and Science*) je najcitovanejšia práca k téme a v predošlej verzii tohto dokumentu bola zhrnutá príliš optimisticky. Skutočný výsledok je jemnejší:

- U **dlhosrstých** mačiek strava s 11 % a 15 % celkovej vlákniny zvýšila vylučovanie srsti stolicou o **81 %**, resp. **113 %** oproti kontrole.
- U **krátkosrstých** mačiek **nemala žiadny merateľný efekt.**

To je zásadné pre praktické rozhodovanie: ak máte krátkosrstú mačku, dôkazy pre „viac vlákniny na bezoáre" sú výrazne slabšie, než sa bežne prezentuje. Zároveň si všimnite úroveň vlákniny — 11–15 % na sušinu. **Žiadny produkt v tomto prieskume sa k tomu ani nepribližuje**; typická kapsička má 0,3–1 % v stave ako podávané, čo je zhruba 2–5 % na sušinu.

**PMC7079073** (vplyv zdrojov vlákniny na stráviteľnosť a manažment bezoárov) potvrdzuje, že typ aj množstvo vlákniny ovplyvňujú kvalitu stolice a vylučovanie srsti — ale varuje, že **nadmerná vláknina znižuje stráviteľnosť bielkovín a tuku.** Viac nie je automaticky lepšie.

### 3.2 Psyllium — nové a najsilnejšie dôkazy (2024, 2026)

Dve práce, ktoré v predošlej verzii chýbali a sú metodicky najsilnejšie z celého zoznamu:

- **Keller a kol. 2024** (*Journal of Feline Medicine and Surgery*): psyllium u **zdravých** mačiek zvýšilo frekvenciu vyprázdňovania a zlepšilo skóre, objem aj vlhkosť stolice.
- **Rochon a kol. 2026** (*JFMS*) — **6-mesačná kontrolovaná, zaslepená, multicentrická klinická štúdia**, teda najvyššia úroveň dôkazu v tomto dokumente. Mačky s chronickou zápchou dostávali buď diétu s **6 % psyllia**, alebo kontrolnú s 0,5 %. Zlyhanie diéty z gastrointestinálnych dôvodov: **26,9 % v testovanej skupine vs. 73,3 % v kontrolnej.**

Psyllium je **nízko fermentovateľná** vláknina, ktorá viaže vodu a tvorí gél — funguje mechanicky, inak než inulín. Prakticky: pre mačku s reálnym problémom so zápchou alebo tranzitom je psyllium najlepšie podložená voľba, **ale opäť v dávkach (6 %), aké bežná kapsička neposkytuje.** Z celého prieskumu obsahuje pomenované psyllium jediný produkt — *Brit Care Velvet Mousse Weight Management Chicken* (0,29 %), čo je dvadsaťnásobne menej než v štúdii.

### 3.3 Inulín a FOS — mechanizmus

Inulín je fruktán, ktorý mačka nevie stráviť vlastnými enzýmami; **fermentujú ho baktérie hrubého čreva** za vzniku mastných kyselín s krátkym reťazcom (najmä butyrátu), ktoré vyživujú bunky črevnej výstelky a podporujú prospešnú mikroflóru. Typická dávka v komerčnom krmive je 0,1–0,4 %; nad ~1–2 % môže spôsobiť riedku stolicu a plynatosť.

Rozdiel oproti psylliu je podstatný a v marketingu sa zamlčiava: **inulín/FOS = výživa mikrobiómu, psyllium = mechanický objem a tranzit.** Nie sú zameniteľné.

### 3.4 Sacharidy — a prečo som zmiernil hodnotenie

Predošlá verzia zaobchádzala so sacharidmi ako s jednoznačným zlom (odvolávajúc sa na catinfo.org, čo je osobný web veterinárky, nie recenzovaná literatúra). Nová verzia zohľadňuje aj protiargument:

**Verbrugghe & Hesta / JAVMA 2022 — „Evidence does not support the controversy regarding carbohydrates in feline diets"** tvrdí, že priama príčinná súvislosť medzi sacharidmi v strave a cukrovkou u mačiek **nie je dostatočne doložená**; hlavným rizikovým faktorom je obezita a celkový energetický príjem, nie sacharidy samy osebe.

Zároveň platí, že u **už diagnostikovaných diabetických** mačiek majú nízkosacharidové vlhké diéty dobre doložený prínos (remisia až ~68 % vs. <20 % pri vysokosacharidovom suchom krmive) — to však hovorí o liečbe, nie o prevencii u zdravej mačky.

**Dôsledok pre hodnotenie:** sacharidy zostali v rámci ako kritérium (mačka je striktný mäsožravec a vysoký NFE zvyčajne signalizuje lacnú receptúru), ale majú **rovnakú váhu ako ostatné kritériá, nie vyššiu** — a hranice sú miernejšie než v predošlej verzii.

### 3.5 Taurín — a metodická oprava

Nedostatok taurínu spôsobuje u mačiek dilatačnú kardiomyopatiu a degeneráciu sietnice; mačky si ho nevedia dostatočne syntetizovať. Od 80. rokov ho výrobcovia povinne dopĺňajú, takže pri kompletných krmivách od etablovaných výrobcov ide o v podstate vyriešený problém.

**Oprava:** **FEDIAF udáva minimá na sušinu** — pre vlhké krmivo rádovo 2 000–2 500 mg/kg sušiny. Predošlá verzia porovnávala hodnoty z etikety („taurín 520 mg/kg") priamo proti takémuto minimu, čo je chyba päťnásobného rádu, keďže etiketa uvádza stav ako podávané pri ~80 % vody.

Správne prepočítané: Shelma 520 mg/kg ako podávané → **2 737 mg/kg sušiny** (vyhovuje). Bozita 700 → **3 889** (vyhovuje s rezervou). CarniLove 1 400 → **7 000** (veľmi vysoké). Rozdiely medzi značkami sú teda menej dramatické, než sa na etikete javí, a takmer všetky kompletné krmivá požiadavku plnia.

---

<a id="4"></a>
## 4. Hodnotiaci rámec A–E (prepracovaný)

Sedem kritérií, každé **0–2 body**. Skóre je **percento z dosiahnuteľných bodov** — ak niektorý údaj výrobca nedeklaruje, kritérium sa vynechá z čitateľa *aj* menovateľa, takže chýbajúci údaj produkt netrestá ani neodmeňuje.

| # | Kritérium | 2 body | 1 bod | 0 bodov |
|---|---|---|---|---|
| 1 | **Bielkoviny** (na sušinu) | ≥ 45 % | 35–45 % | < 35 % |
| 2 | **Sacharidy NFE** (na sušinu) | < 15 % | 15–25 % | > 25 % |
| 3 | **Vláknina / prebiotiká** | fermentovateľné pomenované (inulín, FOS, psyllium) | objemové (lignocelulóza, celulóza) | žiadne deklarované |
| 4 | **Pomenované mäso** (najvyššie % konkrétneho druhu) | ≥ 25 % | 8–25 % | < 8 % |
| 5 | **Taurín** (na sušinu) | ≥ 2 500 mg/kg | 1 500–2 500 | < 1 500 |
| 6 | **Kompletnosť** | kompletné krmivo | neuvedené | doplnkové |
| 7 | **Čistá etiketa** | bez cukru aj bez obilnín | jedno z toho | cukor aj obilniny |

**Známky:** A ≥ 85 % · B 70–85 % · C 50–70 % · D 35–50 % · E < 35 %

### Čo rámec zámerne nehodnotí

- **Textúru.** Pre bezzubú mačku je paté/mousse zásadné, ale nutrične to nič nehovorí. Textúra je v dátach ako **filtrovateľný atribút**, nie ako súčasť známky.
- **Cenu.** Nie je to výživový parameter a rýchlo zastaráva.
- **Výrobcu ani závod.** Ako ukazuje [časť 7](#7), ten istý závod vyrába kvalitné aj slabé receptúry.
- **Marketingové nároky** typu „holistic", „super-premium" — WSAVA na ne explicitne upozorňuje ako na neregulované termíny.

### Známa slabina rámca

Kritérium 4 (pomenované mäso) sa parsuje automaticky z textu zloženia a **nie je dokonalé**. Ak výrobca uvedie blokové „85 % mäsa vo filetách (62 % kuře, 15 % játra, 8 % kachna)", algoritmus berie najvyššie pomenované číslo pod 70 %, teda 62 %. To je rozumné, ale pri neobvykle formulovaných etiketách môže minúť. Pri každom produkte je preto pôvodný text zloženia zobrazený v [`index.html`](./index.html) na kontrolu.

---

<a id="5"></a>
## 5. Výsledky podľa značiek

Priemerné skóre a rozloženie známok. **Pozor:** počet produktov sa výrazne líši — Bozita má 4 položky (multiboxy), Brit Care 31, takže priemer nie je rovnako spoľahlivý.

| Značka | n | Priem. | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Shelma** | 10 | **90,2** | 10 | – | – | – | – |
| **Bozita** | 4 | **89,5** | 4 | – | – | – | – |
| **Dein Bestes** | 2 | **89,0** | 2 | – | – | – | – |
| **Calibra** | 16 | **81,2** | 8 | 5 | 3 | – | – |
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

**Celkové rozloženie:** 33× A · 55× B · 58× C · 4× D · 1× E

### Ako to čítať férovo

**Bozita, Dein Bestes a Almo Nature/Kattovit majú príliš málo položiek** na to, aby sa z priemeru dali robiť závery o značke. Bozita skončila druhá, ale sú to 4 multiboxy s jedinou zdieľanou receptúrnou platformou — v skutočnosti hodnotíme jednu receptúru, nie sortiment. To isté platí pre **Shelmu na prvom mieste**: 10 produktov, ktoré zdieľajú jednu analytickú platformu (bielkoviny 10 %, tuk 3,5 %, popol 2,5 %, vláknina 0,4 %, vlhkosť 81 %) a líšia sa hlavne druhom mäsa. Desať A-čiek teda neznamená desať nezávislých dôkazov kvality — je to jedna dobre postavená receptúra v desiatich príchutiach.

**Purina Pro Plan a Royal Canin sú znevýhodnené štruktúrou rámca**, nie nutne kvalitou. Väčšina ich položiek sú **veterinárne diéty**, ktoré sú zámerne formulované proti bežným kritériám: renálna diéta *má* mať nízke bielkoviny (7,2 %), obsahuje obilniny a cukry, a preto v tomto rámci nutne skóruje zle. **To neznamená, že je to zlé krmivo** — znamená to, že rámec navrhnutý pre bežnú stravu zdravej mačky na terapeutické diéty nesedí. Veterinárne diéty sú v [`index.html`](./index.html) samostatne označené a odporúčam ich hodnotiť oddelene.

**Brit Care má široký rozptyl** (A až D), pretože zahŕňa dve úplne odlišné kategórie: kompletné filetové kapsičky a **doplnkové mousse/loaf pamlsky**, ktoré automaticky strácajú 2 body za kompletnosť. To je korektné — nie sú to plnohodnotné krmivo — ale skresľuje priemer značky.

**Sheba skončila nižšie, než by sa od benchmarku čakalo** (59,4; 13 zo 14 produktov je C). Dôvod nie je jeden zlý parameter, ale kombinácia: len 4 % pomenovaného mäsa, pridané cukry a **žiadna deklarovaná vláknina či prebiotikum**. Bielkoviny na sušinu má pritom slušné (47–49 %). Nie je to zlé krmivo — je to priemerne formulované krmivo, ktoré mačke nič nepokazí, ale ani neponúka nič navyše.

---

<a id="6"></a>
## 6. Vetvené nutričné údaje — ako čítať tabuľky

Každý produkt v [`index.html`](./index.html) sa dá rozbaliť do troch úrovní. Príklad na *Shelma dušené filetky, hovädzie*:

**Úroveň 1 — deklarované na etikete (ako podávané)**
> bielkoviny 10 % · tuk 3,5 % · vláknina 0,4 % · popol 2,5 % · vlhkosť 81 %

**Úroveň 2 — prepočet na sušinu**
> sušina 19 % → bielkoviny **52,6 %** · tuk **18,4 %** · sacharidy NFE **13,7 %** · popol **13,2 %** · taurín **2 737 mg/kg**

**Úroveň 3 — čiastkové skóre**
> bielkoviny 2/2 · sacharidy 2/2 · prebiotiká 2/2 · mäso 2/2 · taurín 2/2 · kompletnosť 2/2 · čistá etiketa 2/2 → **14/14 = 100 % → A**

Rozvetvenie odhaľuje aj to, čo súhrnná známka skrýva. Porovnajte s *Brit Care BCC Sterilized Fillets in Gravy, morčacie*: aj to je B-produkt s pomenovaným mäsom 62 % — ale sacharidy má na **41,7 % sušiny** (0/2 body) a vlákninu len objemovú lignocelulózu (1/2). Dve „dobré" krmivá, dva úplne odlišné dôvody prečo. Bez vetvenia by z toho ostali len dve písmená.

**Praktická poznámka k popolu:** popol je pri dopočte NFE nutný. Ak ho výrobca nedeklaruje (v tomto prieskume 2 produkty — Royal Canin Digestive Care US a Purina NF Renal), sacharidy sa **nedopočítavajú vôbec** a kritérium sa vynechá — inak by chýbajúci popol falošne nafúkol odhad sacharidov o niekoľko percent.

Filtrovať a triediť sa dá podľa ktoréhokoľvek údaja z ktorejkoľvek úrovne, plus podľa textúry, životnej fázy, trhu (SK/CZ vs. UK), kompletnosti a typu prebiotika.

---

<a id="7"></a>
## 7. Kľúčové zistenia a anomálie

### 7.1 Sheba: UK a CZ verzia „toho istého" produktu sa líšia

Potvrdené priamym stiahnutím oboch trhov:

| | UK (Gravy) | CZ/SK |
|---|---|---|
| Bielkoviny | 7,9 % | 8 % |
| Tuk | 4,4 % | 5 % |
| Popol | 1,4 % | 1,9 % |
| Vlhkosť | 84 % | 83 % |
| Pomenované mäso v zložení | neuvádza | **uvádza (45 % / 40 %)** |
| Doplnkové látky na kg | **uvádza** (D3, taurín, stopové prvky) | na stiahnutých stránkach neuvedené |

Na sušinu: UK 49,4 % bielkovín / 12,5 % NFE, CZ 47,1 % / 10,6 %. Rozdiel je malý, ale **„Sheba Fresh & Fine" nie je jedna univerzálna receptúra naprieč trhmi** — a britská stránka poskytuje viac údajov o doplnkových látkach než česká.

### 7.2 Ten istý závod, diametrálne odlišná kvalita

**Calibra, Shelma, Bozita, Propesko a Prevital vyrába tá istá zmluvná skupina** (Partner in Pet Food; veterinárne schválenie CZ843 pre závod vo Veselí nad Lužnicí). V tomto prieskume z toho vychádzajú tri z prvých štyroch najlepšie hodnotených značiek — a zároveň to potvrdzuje, že **výrobný závod nie je indikátorom kvality**, receptúru si u neho objednáva každá značka samostatne.

Calibra Cat Life a Shelma dušené filetky majú prakticky **identickú analytickú platformu** (bielkoviny 10 %, tuk 3,5 %, popol 2,5 %, vláknina 0,4 %, vlhkosť 81 %, inulín 0,4 %, taurín 520 mg/kg) — pravdepodobne rovnaký základný recept pod dvoma značkami.

### 7.3 Marketingové názvy často nesedia so zložením

Systematický vzor naprieč značkami, ktorý sa dá vidieť len pri čítaní surových zložení:

- **CarniLove**: v 6 zo 7 receptúr tvorí mäsový základ **66 % morčacie + 10 % morčacia pečeň**, a pomenované „hlavné" mäso (pstruh, diviak, bažant, kačica, prepelica, králik) je len **14 %**. „Wild Boar" kapsička obsahuje viac morčacieho než diviačieho.
- **Brit Care filety**: takmer všetky príchute stoja na **62 % kuracieho + 15 % pečene**, pomenovaná príchuť je 8 %.
- **Ontario tuniak**: druhá najsilnejšia zložka je kuracie mäso (30,27 %).
- **Bozita**: kuracia príchuť má 14 % pomenovaného mäsa, všetky ostatné 8 %.

Nejde o porušenie predpisov — pomenovaná zložka je vždy prítomná. Ale ak vyberáte podľa druhu mäsa kvôli alergii alebo chuťovej preferencii, **názov na obale je nespoľahlivý vodítko a treba čítať zloženie.**

### 7.4 Chyby priamo na stránkach výrobcov

Pri sťahovaní sa objavili tri nezrovnalosti, ktoré som **neopravil, ale zaznamenal** — sú v `fetch_notes` príslušných JSON súborov:

- **Ontario „kuracie a krevety" — chyba potvrdená a vyriešená.** Slovenská stránka uvádzala pri tejto príchuti **kačicu 4 % a žiadne krevety**, so zložením aj analytikou identickou s kačacím produktom. Stiahnutie **českej mutácie** ([`ontario_cz.json`](raw_data/ontario_cz.json)) ukázalo skutočnú receptúru: **krevety 8 %, zelený hrášok 3 %, kuracie 45 %** a odlišnú analytiku (tuk 0,2 %, vlhkosť 88 %). Šlo teda o chybu v CMS na slovenskej verzii; české dáta sú v prieskume použité ako kanonické a slovenský riadok je odložený ako záznam o chybe.
- **Ontario „pre mačiatka so šunkou"** — slovenský názov hovorí „pre mačiatka", klasifikácia na tej istej stránke „pre dospelé mačky". Česká verzia má v názve len „kuře se šunkou" a klasifikuje ho ako krmivo pre dospelé mačky — **chyba je teda v slovenskom názve**, nie v označení typu krmiva.
- **Shelma „v želé" multipacky** — produktová stránka ich popisuje ako krmivo „pro koťata" (pre mačiatka), prehľadová stránka ako „pro dospělé kočky". Overené trojnásobným načítaním.
- **Shelma kitten olej** — príchuť „losos a rakytník" obsahuje **ľanový** olej, zatiaľ čo „morčacie a brusnice" obsahuje **lososový** olej. Zámena oproti tomu, čo naznačujú názvy.
- **Purina** — URL s „obezita" vracia produkt **Diabetes Management**; URL s „kote" (mačiatko) vracia dospelý produkt Delicate Digestion.

### 7.5 Prebiotiká: len necelá polovica produktov

| Typ | Počet | Podiel |
|---|---:|---:|
| Žiadne deklarované | 74 | 49 % |
| Fermentovateľné (inulín / FOS / psyllium) | 59 | 39 % |
| Objemové (lignocelulóza) | 18 | 12 % |

Pripomínam ale [časť 3.1](#3): aj tie „lepšie" produkty majú vlákninu rádovo desaťnásobne nižšie, než aké dávky vykazovali efekt v štúdiách. **Rozdiel medzi produktom s 0,4 % inulínu a bez neho je reálny, ale skromný** — nie je to náhrada za veterinárne riešenie problému s bezoármi.

### 7.6 Pridaný cukor

**28 zo 151 produktov (19 %)** má v zložení deklarované cukry. Koncentrujú sa u masových značiek (Sheba, Purina Pro Plan, Royal Canin OTC rady). Väčšina prémiových a bezobilných rád (Shelma, Calibra, Bozita, CarniLove, Meowing Heads) cukor neobsahuje.

### 7.7 Doplnkové vs. kompletné

**21 produktov (14 %) je len doplnkových** — nesmú tvoriť podstatnú časť stravy. Patrí sem takmer celá mousse/loaf rada Brit Care a celá rada Ontario. Pri Ontariu je to podstatné, lebo produkty pôsobia ako plnohodnotné kapsičky, ale sú deklarované ako doplnkové krmivo.

**63 produktov (42 %) je deklarovaných ako kompletné** a pri **67 (44 %) to stránka výrobcu neuvádza vôbec** — čo treba overiť priamo na obale. Toto vysoké číslo je dôsledok prísnejšieho prístupu: ak stránka kompletnosť nedeklaruje, prieskum ju **nedomýšľa** z názvu ani z analógie so súrodeneckým produktom. Rozhodnutia pri sporných formuláciách sú zdokumentované v [`curated.json`](./curated.json).

---

<a id="8"></a>
## 8. Odporúčania podľa situácie

Nie univerzálne poradie, ale výber podľa toho, čo riešite. Zdôvodnenia sú v dátach — čísla si viete overiť v [`index.html`](./index.html).

### Mačka bez zubov / potreba jemnej textúry

Textúra sa nehodnotí známkou, tak sem patrí samostatne. **Paté a mousse** (žuvanie netreba): rada **Brit Care Velvet Mousse** — pozor, *Weight Management* varianty sú kompletné krmivo (A, 86 %), ale *Creamy Duo Mousse*, *Real Loaf* a *Double Layer Mousse* sú **doplnkové pamlsky**, nie strava.

**Jemné kúsky/filety** ako kompromis: Shelma dušené filetky, Calibra Cat Life, Sheba Fresh & Fine — všetky majú malé mäkké kúsky dobre nasiaknuté omáčkou.

### Podpora trávenia a tranzitu (bezoáre, zápcha)

Podľa [časti 3.2](#3) je najlepšie podložené **psyllium** — ale v dávkach, ktoré komerčné kapsičky neposkytujú. Ak problém pretrváva, **riešením je veterinárna diéta alebo doplnok, nie výber kapsičky.**

Z bežných produktov s pomenovaným fermentovateľným prebiotikom: **Shelma** (0,4 % inulín, A), **Calibra Cat Life** (0,4 % inulín, A), **Bozita** (0,1 % FOS z čakanky, A), **Stuzzy** (0,4 % inulín z čakanky, B).

### Kontrola hmotnosti

**Brit Care Velvet Mousse Weight Management** — jediné produkty v prieskume s funkčnou vlákninou cielenou na sýtosť (psyllium 0,29 % v kuracom, vláknina z čakanky 0,29 % v hovädzom), kompletné krmivo, A (86 %). Nízka energetická denzita (677–700 kcal/kg) je pri chudnutí výhoda.

Ďalej **Dein Bestes Sensitive** (A, 90 %) — tuk len 3 %, deklarovane vyvinuté s veterinármi na trávenie aj hmotnosť.

### Priberanie / vyššia energia

Hľadajte vysoký tuk a energetickú denzitu: **Brit Care Real Tuna Loaf** (1 220 kcal/kg, bielkoviny 16,5 %) alebo **Double Layer Mousse Tuna & Salmon** (1 020 kcal/kg) — ale obe sú **doplnkové**, takže ako *doplnok* k plnohodnotnej strave, nie ako náhrada.

Z kompletných: **Calibra Cat Life Kitten** (93 kcal/100 g) alebo kitten rady všeobecne, ktoré majú zámerne vyšší tuk (5 % vs. 3,5 %).

### Najlepší pomer kvality naprieč sortimentom

**Shelma** (10 produktov, 10× A, priemer 97,2) a **Calibra Cat Life** (8× A) — obe s pomenovaným inulínom, bez cukru, bez obilnín, vysoké bielkoviny na sušinu, taurín bezpečne nad FEDIAF minimom. Keďže ide pravdepodobne o rovnakú receptúru ([časť 7.2](#7)), je rozumné vybrať tú, ktorá je práve dostupnejšia alebo lacnejšia.

Prekvapením je **Brit Premium** (7× A, priemer 77,3) — v predošlej verzii prieskumu úplne chýbal. Rada 100 g kapsičiek má 0,4 % inulínu, bez cukru a bez obilnín, s pomenovaným mäsom až 40 % (Chicken & Turkey). Je to najširší A-hodnotený sortiment v prieskume.

### Čo obísť

- **Produkty s pridaným cukrom a obilninami zároveň** (0 bodov za čistú etiketu) — v prieskume najmä lacnejšie OTC rady Royal Canin a časť Purina Pro Plan.
- **Doplnkové krmivá ako hlavná strava** — hlavne rada Ontario, ktorá tak nevyzerá.
- **Marketing „hairball care" bez pomenovanej vlákniny** — ak produkt sľubuje riešenie bezoárov, ale v zložení nemá pomenovaný zdroj vlákniny, je to len názov.

---

<a id="9"></a>
## 9. Obmedzenia a čo tento prieskum nevie

Poctivý zoznam toho, čo tieto dáta **nedokážu** povedať:

1. **Deklarované ≠ namerané.** Podľa nariadenia EÚ 767/2009 sú „analytické zložky" **garantované minimá/maximá**, nie laboratórne hodnoty konkrétnej šarže. Dve šarže sa môžu líšiť pri identickom obale. Zhoda Shelma/Calibra „na desatinu percenta" teda môže byť aj zhodou zaokrúhlenia na rovnakú deklarovanú hodnotu, nie dôkazom identického receptu.
2. **Žiadny nezávislý laboratórny test.** Overil som štyri hlavné európske spotrebiteľské testovacie organizácie (Stiftung Warentest, Öko-Test, VKI/Konsument, Test-Aankoop) — testujú prevažne masové supermarketové značky v DACH/Benelux regióne a **väčšinu značiek z tohto prieskumu netestovali.**
3. **NFE je dopočet, nie meranie.** Kumuluje chyby piatich ostatných hodnôt.
4. **19 produktov má nespoľahlivý základ sušiny** (vlhkosť ≥ 85 %) — označené, ale nevyradené.
5. **Stráviteľnosť sa nemeria vôbec.** Dva produkty s identickým zložením na papieri sa môžu líšiť biologickou dostupnosťou bielkovín. Toto je pravdepodobne **najväčšia slepá škvrna** celého rámca.
6. **Chýbajúce údaje = vynechané kritérium**, čo môže mierne zvýhodniť značky, ktoré deklarujú menej. Napríklad Calibra Premium neuvádza energetickú hodnotu a väčšina bežných značiek neuvádza horčík/fosfor.
7. **Veterinárne diéty sú v tomto rámci systémovo znevýhodnené** — pozri [časť 5](#5).
8. **Parsovanie je automatické.** Pri neobvykle formulovaných etiketách môže algoritmus minúť pomenované mäso alebo prebiotikum. Preto je pri každom produkte zobrazený pôvodný text.

---

<a id="10"></a>
## 10. Zdroje

### Tier 1 — recenzované štúdie a regulačné dokumenty

- **Weber a kol. 2015** — [Influence of the dietary fibre levels on faecal hair excretion after 14 days in short and long-haired domestic cats](https://onlinelibrary.wiley.com/doi/10.1002/vms3.6), *Veterinary Medicine and Science* ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5645811/))
- **Rochon a kol. 2026** — [A psyllium-supplemented gastrointestinal diet is effective for the management of chronic constipation in cats: a 6-month controlled clinical trial](https://journals.sagepub.com/doi/10.1177/1098612X261420519), *Journal of Feline Medicine and Surgery* ([PubMed](https://pubmed.ncbi.nlm.nih.gov/41631677/)) — **najsilnejší dôkaz v tomto dokumente**
- **Keller a kol. 2024** — [Psyllium husk powder increases defecation frequency and faecal score, bulk and moisture in healthy cats](https://journals.sagepub.com/doi/10.1177/1098612X241234151), *JFMS*
- **Verbrugghe & Hesta 2022** — [Evidence does not support the controversy regarding carbohydrates in feline diets](https://avmajournals.avma.org/view/journals/javma/260/5/javma.21.06.0291.xml), *JAVMA* — protiargument k sacharidovej panike
- [The effects of diets varying in fibre sources on nutrient utilization, stool quality and hairball management in cats](https://pmc.ncbi.nlm.nih.gov/articles/PMC7079073/), *PMC*
- [Clinical Signs of Hairballs in Cats Fed a Diet Enriched with Cellulose](https://www.researchgate.net/publication/289117024_Clinical_Signs_of_Hairballs_in_Cats_Fed_a_Diet_Enriched_with_Cellulose)
- [The effect of changing the moisture levels of dry extruded and wet canned diets on physical activity in cats](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5465855/), *PMC*
- **FEDIAF Nutritional Guidelines 2024** — [europeanpetfood.org](https://europeanpetfood.org/self-regulation/nutritional-guidelines/) ([oznámenie o aktualizácii](https://europeanpetfood.org/_/news/fediaf-announces-updated-2024-nutritional-guidelines/))
- **WSAVA Global Nutrition Guidelines** — [wsava.org](https://wsava.org/global-guidelines/global-nutrition-guidelines/)
- Nariadenie EÚ č. 767/2009 o uvádzaní krmív na trh (tolerancie deklarovaných hodnôt)

### Tier 1 — stránky výrobcov (jediný zdroj zloženia a analytiky)

Všetky produktové dáta pochádzajú výhradne odtiaľto a sú uložené v [`raw_data/`](raw_data/):

| Súbor | Značka | Zdroj | n |
|---|---|---|---:|
| `sheba.json` | Sheba | uk.sheba.com, sheba.cz | 14 |
| `shelma.json` | Shelma | shelma.eu/cz | 10 |
| `calibra.json` | Calibra | mojacalibra.sk | 16 |
| `carnilove.json` | CarniLove | carnilove.com/sk | 12 |
| `brit_premium.json` | Brit Premium | krmivo-brit.cz | 19 |
| `brit_care_fillets.json` | Brit Care / Premium | krmivo-brit.cz | 18 |
| `brit_care_mousse.json` | Brit Care | krmivo-brit.cz | 17 |
| `purina_proplan.json` | Purina Pro Plan | purina.cz | 15 |
| `ontario.json` | Ontario | ontario.pet/sk | 9* |
| `ontario_cz.json` | Ontario | ontario.pet (CZ) | 9 |
| `bozita.json` | Bozita | bozita.com/cz | 4 |
| `meowing_heads.json` | Meowing Heads | barkingheads.co.uk | 4 |
| `other_brands.json` | RC, Animonda, Almo Nature, Dein Bestes, Stuzzy, Kattovit, Purina | rôzne | 20 |

\* Slovenské riadky Ontaria sú v archíve zachované, ale **do štatistík sa nepočítajú** — ide o tie isté produkty ako v českej mutácii, ktorá je presnejšia (opravené krevety, úplnejšie zloženie kraba, správny názov pri šunkovej príchuti). Zoznam vyradených URL aj s dôvodom je v [`curated.json`](./curated.json) v sekcii `superseded`; skript ich neodstraňuje zo surových dát, len ich vynechá pri výpočte.

### Nezaradené (a prečo)

- **E-shopy** (Zoohit, Alza, ABC-ZOO) — v predošlej verzii sa z nich brali ceny a niekedy aj zloženie. Táto verzia ich nepoužíva vôbec; popisy na e-shopoch bývajú zastarané alebo prepísané.
- **Blogy a SEO obsah** — predošlá verzia citovala laický blog vedľa odborných zdrojov, čo bolo zavádzajúce. Odstránené.
- **catinfo.org** — kvalifikovaná veterinárka, ale osobný web s vyhraneným názorom, nie recenzovaná literatúra. Nahradené recenzovaným protiargumentom (JAVMA 2022).
- **Marketingové výrazy** („holistic", „super-premium") — WSAVA ich označuje za neregulované a bez výpovednej hodnoty.

---

*Vygenerované z [`dataset.json`](./dataset.json) (151 produktov) skriptom [`build_dataset.py`](./build_dataset.py). Rekonštrukcia: `python build_dataset.py`. Staršie verzie prieskumu sú v [`old/`](old/) a ich údaje sa v tomto dokumente nepoužili.*
