# Kontrola metodiky: Feline NutriScore (NotebookLM)

**Predmet:** [`NutriScoreLM.md`](./NutriScoreLM.md), [`AnalyzaLM.md`](./AnalyzaLM.md), [`AnalyzaLM2.md`](./AnalyzaLM2.md)
**Kontrolované proti:** [`raw_data/*.json`](raw_data/) — doslovný text etikiet, ktorý bol vstupom pre obe analýzy
**Dátum:** júl 2026

---

## Verdikt

**Extrakcia dát je prevažne správna. Hodnotiaci rámec nie je použiteľný v predloženej podobe.**

Konkrétne čísla sú z veľkej časti dobre odpísané z etikiet a prepočet na sušinu je aritmeticky
správny. Problém je v štyroch veciach: **škála nemá rozlišovaciu schopnosť**, **taurín sa
hodnotí nekonzistentne s vlastnou metodikou**, **niektoré zložky sa pripisujú produktom,
ktoré ich na etikete nemajú**, a v jednom prípade sa **medzera v dátach vydáva za
zdravotné riziko**.

---

## 1. Čo je overiteľne správne

Poctivo najprv to, čo obstálo:

| Tvrdenie | Overenie |
|---|---|
| Calibra Life Adult Veal: 40,6 % teľacie, 17 % pečeň, 15 % bravčové, 10 % kuracie | ✅ presne tak na etikete |
| Meowing Heads: proteín 11 %, popol 0,5 %, vlhkosť 80 % → 55 % / 2,5 % DM | ✅ aritmetika sedí |
| **Stuzzy: taurín 100 mg/kg** | ✅ **skutočne je na etikete — dobrý nález** |
| Ontario „kuracie a krevety" neobsahuje krevety, ale kačicu | ✅ potvrdené (nezávisle nájdené aj v tomto prieskume) |
| Shelma kitten: zámena ľanového a lososového oleja oproti názvom | ✅ potvrdené |
| Royal Canin Sterilised: v doplnkových látkach chýba taurín | ✅ na stiahnutej stránke skutočne nie je |
| CarniLove: 66 % morka + 14 % pomenované mäso vo väčšine príchutí | ✅ potvrdené |

Nález taurínu 100 mg/kg pri Stuzzy je vecne cenný — je to najnižšia hodnota v celom
datasete a v mojom vlastnom rámci prešla bez povšimnutia, lebo Stuzzy vychádzalo B.

---

## 2. Škála nerozlišuje — a rozpor s vlastným zadaním

`NutriScoreLM.md` otvára tvrdením, že A–E škála je nedostatočná a treba
„vysoko-rozlišovací, viacfaktorový systém". Výsledok robí presný opak.

**V `AnalyzaLM2.md` dostane 100/100 približne 34 produktov:** všetky štyri Meowing Heads,
všetkých desať CarniLove, všetkých osem Calibra Life a dvanásť Brit Care filetiek.

Príčina je štrukturálna. Základ je 50 bodov, bonusy môžu dosiahnuť +50 a strop je 100.
Ktorýkoľvek produkt, ktorý naplno zaboduje v troch kategóriách, **narazí na strop a ďalšie
rozdiely sa stratia**. Horšie: **penalizácie sa pri takom produkte stanú neviditeľnými**,
lebo ich strop pohltí.

Ukážka priamo z dát — CarniLove Trout:

```
proteín 7,0 % pri vlhkosti 80 %  →  35,0 % v sušine
```

Vlastné pravidlo FNS znie „< 40 % DM proteín = −5 bodov". Produkt teda mal dostať
penalizáciu — a napriek tomu má **100/100**, rovnako ako CarniLove Turkey s 50 % DM
proteínu. Rozdiel 15 percentuálnych bodov v proteíne na sušine sa v skóre neprejaví vôbec.

Reálne použité hodnoty naprieč `AnalyzaLM2.md` sú len: 100, 90, 85, 80, 75, 70, 65, 60, 55,
25, 20, 15. To je zhruba **päť použiteľných pásiem** — teda rovnaká rozlišovacia schopnosť
ako A–E, ale prezentovaná ako stobodová presnosť.

---

## 3. Taurín: rozpor s vlastnou metodikou

`NutriScoreLM.md`, sekcia II, správne vysvetľuje, prečo sa musí počítať na sušinu:

> *„Nutrients must be evaluated on a Dry Matter basis to prevent high water content from
> masking poor nutrient density."*

Sekcia III potom taurín hodnotí **v stave ako podávané** (≥ 1000 mg/kg = +10, < 300 = −5) —
teda presne tou metódou, ktorú dokument o odsek vyššie odmieta. Pritom vlhkosť
v porovnávanom poli kolíše od 74 % do 89 %.

Dôsledky:

| Produkt | Etiketa | Vlhkosť | Na sušinu | FNS verdikt |
|---|---:|---:|---:|---|
| Brit Premium Delicate | 280 mg/kg | 82 % | **1 556 mg/kg** | −20 bodov, „pod fyziologickou normou" |
| Stuzzy Shreds | 100 mg/kg | 82 % | **556 mg/kg** | −30 bodov |
| Ontario vývar | 780 mg/kg | 89 % | **7 090 mg/kg** | bez zvláštneho ohodnotenia |

Brit Premium je na sušinu **takmer trojnásobne lepší než Stuzzy**, no v FNS je medzi nimi
rozdiel len 10 bodov. Ontario má najvyšší taurín v sušine z celej trojice a nedostane zaň nič.

Navyše prahy 500 / 1000 mg/kg nie sú v dokumente nikde zdrojované. **FEDIAF udáva minimá
na sušinu** (rádovo 2 000–2 500 mg/kg sušiny pre vlhké krmivo), takže hranica „500 mg/kg =
záchovná dávka" nezodpovedá žiadnej publikovanej norme.

---

## 4. Zložky pripísané produktom, ktoré ich na etikete nemajú

Toto je najvážnejší vecný problém, lebo z neho vychádzajú klinické závery.

### Pšeničný lepok

`AnalyzaLM.md` aj `AnalyzaLM2.md` opakovane tvrdia, že Royal Canin a celá udržiavacia rada
Purina Pro Plan stoja na **pšeničnom lepku**, a stavajú na tom argument, že lepok je
„ťažko stráviteľný a dlhodobo zaťažuje obličky a pečeň".

Prehľadal som zloženia všetkých 151 produktov v `raw_data/`. **Lepok je explicitne uvedený
v dvoch produktoch** — Royal Canin Digestive Care Loaf (US) a Purina NF Renal. Etikety
ostatných menovaných produktov uvádzajú:

```
Royal Canin Sterilised Gravy:
  „Mäso a živočíšne produkty, bielkovinové extrakty rastlinného pôvodu, obilniny,
   vedľajšie produkty rastlinného pôvodu, rastlinné bielkovinové extrakty,
   minerálne látky, kvasnice"
```

„Rastlinné bielkovinové extrakty" môže byť lepok, ale aj hrachový alebo sójový proteín.
Dosadiť konkrétnu surovinu a potom o nej vyvodzovať orgánovú záťaž je krok za dáta.

### Cukry v Royal Canin

Sekcia IV `NutriScoreLM.md` uvádza Royal Canin ako príklad pridaných cukrov (−10 bodov)
a tabuľka v `AnalyzaLM.md` mu do stĺpca dáva „cukor". V zložení **Sterilised Gravy ani
Hairball Care sa cukry nenachádzajú**:

```
Hairball Care: „mäso a produkty živočíšneho pôvodu, ryby a produkty z rýb, rastlinné
bielkovinové extrakty, obilniny, minerálne látky, produkty rastlinného pôvodu, kvasnice"
```

Pri **Purine a Sheba je tvrdenie o cukroch správne** — tie ich v zložení naozaj majú.
Chyba sa týka len Royal Canin.

---

## 5. Sheba: medzera v dátach vydaná za zdravotné riziko

Toto považujem za najzávažnejšiu chybu celej analýzy.

`AnalyzaLM.md` hodnotí Sheba CZ/SK **15/100** a označuje ju za **„klinicky nebezpečné"**
s odôvodnením:

> *„V slovenskej a českej mutácii úplne absentuje deklarácia taurínu a iných aditív…
> vysoké riziko vzniku obezity a diabetes mellitus"*

Zdrojové dáta ale hovoria niečo iné. Pole `additives_per_kg_raw` pre Sheba CZ obsahuje:

```
„Nejsou v dokumentu uvedeny (not stated in the fetched content)."
```

To znamená **„naše sťahovanie to nezachytilo"**, nie „výrobok to neobsahuje". V poznámkach
k sťahovaniu je navyše zaznamenané, že české stránky Sheba sú vykresľované klientsky, takže
časť obsahu sa cez WebFetch nedostala. Pre porovnanie, **UK etiketa tej istej produktovej
rady uvádza taurín 573 mg/kg.**

Ide teda o klasickú zámenu: *absencia dôkazu* sa premenila na *dôkaz absencie*, a ten sa
následne eskaloval na tvrdenie o klinickom nebezpečenstve a riziku cukrovky. Sheba je
kompletné krmivo od Mars Petcare; taurín v ňom takmer isto je.

Rovnaká logika je aj za penalizáciou „−10 za chýbajúce analytické dáta" — trestá sa tým
kvalita nášho scraperu, nie kvalita krmiva.

---

## 6. Popol: „menej je lepšie" je nesprávny predpoklad

FNS udeľuje +10 bodov za ≤ 10 % popola v sušine a −5 nad 12 %. Meowing Heads dostáva
plný bonus za **2,5 % popola v sušine**, s odôvodnením, že to znamená kvalitné svalové
partie a nízku záťaž obličiek.

Popol je ale **celkový obsah minerálov** vrátane vápnika, fosforu a celého minerálneho
premixu, ktorý kompletné krmivo obsahovať **musí**. 2,5 % v sušine je menej, než dá samotné
čisté svalové mäso bez kostí, a hlboko pod tým, čo potrebuje kompletná receptúra.

Dva varovné signály, ktoré ani jedna analýza nespomína:

1. Na etikete Meowing Heads je **vláknina 1,5 %, ale popol len 0,5 %** — pri produkte
   s 93 % mäsa je to obrátený pomer, než sa čaká. Vyzerá to skôr na chybu alebo na
   deklaráciu typu „max." než na skutočnú hodnotu.
2. Pole kompletnosti pre Meowing Heads je **„Not stated in this fetch"** — nie je teda
   overené, že ide o kompletné krmivo. Nízky popol pri neoverenej kompletnosti je dôvod
   na opatrnosť, nie na plný bonus.

Napriek tomu je práve tento popol jedným z pilierov skóre 100/100.

---

## 7. Nekonzistentne uplatnené vlastné pravidlá

- **„−10 za chýbajúce analytické dáta"** dostane Bozita a Purina za nedeklarovanú
  energetickú hodnotu. Meowing Heads má v tej istej tabuľke poznámku *„Chýba len ME"*
  a penalizáciu nedostane — skóre 100/100 zostáva.
- **CarniLove je v `AnalyzaLM.md` reprezentované príchuťou Turkey** (jediná, ktorá má
  naozaj 80 % morky) a značka dostane 100/100. V `AnalyzaLM2.md` sú ostatné príchute
  správne rozpísané ako 66 % morka + 14 % pomenované mäso — a dostanú tiež 100/100.
- **Ontario 92,3 % proteínu v sušine** je prezentované ako „excelentný proteínový profil".
  Pri vlhkosti 87 % je sušina len 13 %, takže posun vlhkosti o jeden percentuálny bod hýbe
  výsledkom o niekoľko bodov. Tento prieskum takéto riadky označuje príznakom
  `dm_unreliable` (19 produktov) — analýza ich berie v nominálnej hodnote.

---

## 8. Nezdrojované klinické tvrdenia

Naprieč oboma analýzami sa objavujú tvrdenia o účinkoch bylín v koncentráciách
0,025–1 %, formulované ako preukázaný fakt:

> „bylinky majú dokázaný antiseptický a protizápalový účinok v GIT" (rozmarín 0,025 %,
> tymián 0,025 %) · „kapucínka má preukázané silné močopudné a antiseptické účinky" (0,5 %)
> · „malinové listy podporujú správny tonus močových ciest" (1 %)

Pri 0,025 % rozmarínu v 85 g kapsičke ide o **21 mg** rozmarínu na dávku. Pre farmakologický
efekt v tomto rozsahu neexistuje doklad a v dokumentoch nie je uvedená ani jedna citácia.
Rozmarín v týchto receptúrach navyše najčastejšie plní funkciu **prírodného antioxidantu
(konzervanta)**, nie terapeutickej zložky.

Podobne „L-metionín zaisťuje bezpečné okyslenie moču" — mechanizmus je reálny, ale
formulácia „zaisťuje bezpečné" je pri voľnopredajnom krmive silnejšia, než je vhodné;
acidifikácia moču má aj kontraindikácie.

---

## 9. Čo v analýze nezaznelo

- **Tolerancie deklarovaných hodnôt.** Podľa nariadenia EÚ 767/2009 sú analytické zložky
  **garantované minimá/maximá**, nie namerané hodnoty šarže. Rozlišovať produkty podľa
  rozdielu 0,5 p. b. v popole na sušine (Meowing Heads 2,5 % vs. Top-Cat 2,0 %) je pod
  rozlišovacou schopnosťou vstupných dát.
- **Stráviteľnosť.** Ani jeden rámec ju nemeria a merať sa z etikety nedá — je to spoločná
  slepá škvrna, ktorú stojí za to priznať.
- **Sacharidy.** FNS ich nehodnotí vôbec, hoci pri obligátnom mäsožravcovi je to
  relevantnejšie než obsah rozmarínu.

---

## Odporúčanie

Rámec **neopravovať po častiach, ale zmeniť tri veci**:

1. **Zrušiť strop, alebo znížiť bonusy tak, aby sa saturácia nedosahovala.** Kým 34 produktov
   zdieľa 100/100, škála netriedi.
2. **Taurín počítať na sušinu** — rovnako ako proteín a popol — a prahy naviazať na
   publikované FEDIAF minimá, nie na vlastné čísla.
3. **Odlíšiť „výrobca to nedeklaruje" od „výrobok to neobsahuje".** Prvé je medzera v dátach
   a smie viesť nanajvýš k vynechaniu kritéria; druhé je vlastnosť produktu. Aktuálne obe
   vedú k penalizácii, čo najviac trestá značky s horšie dostupným webom — nie s horším krmivom.

Za správne označiť aj to, čo správne je: rozdelenie veterinárnych diét do osobitnej
kategórie s vysvetlením, prečo sa nesmú hodnotiť udržiavacím indexom, je vecne správne
a v mojom pôvodnom rámci to chýbalo rovnako. Nález taurínu pri Stuzzy stojí za zapracovanie.

---

*Kontrola vychádza výhradne z `raw_data/*.json`, teda z tých istých vstupov, ktoré mala
k dispozícii kontrolovaná analýza. Každé tvrdenie v tomto dokumente sa dá overiť priamo
v príslušnom `composition_raw` / `analytical_constituents_raw` / `additives_per_kg_raw`.*
