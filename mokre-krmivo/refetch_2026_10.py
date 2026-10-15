# -*- coding: utf-8 -*-
"""Apply the 2026-10-14 browser re-fetch to raw_data/*.json (one-off, kept for provenance).

The July fetch used WebFetch, which misses text rendered by JavaScript or hidden in
tabs. On 2026-10-14 the gaps were re-read in a real browser (DOM textContent).
Only verbatim text visible on the product's own page is written; every touched
product gets a dated note in fetch_notes. Pages that confirmed "not stated" are
noted too, so the gap is documented as the manufacturer's, not the scraper's.
Re-running is idempotent.
"""
import glob, json, os

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_data")
TAG = "[2026-10-14 prehliadač]"

CAL_LIFE = "Kompletné superprémiové vlhké krmivo je určené na dlhodobé kŕmenie."
CAL_PREM = ("Rad kapsičiek pre mačky Calibra Cat Premium Line s kompletným a vyváženým zložením "
            "zahŕňa kapsičky pre mačiatka, pre dospelé mačky i pre mačky kastrované.")
SHELMA_AD = "kompletní krmivo s recepturou bez obilovin"
SHELMA_KIT = "kompletní krmivo pro koťata s recepturou bez obilovin"
SHEBA_CZ = "Vysoce kvalitní krmivo, které poskytuje kompletní výživu pro vašeho kočičího společníka"
SHEBA_UK = "100% complete and balanced everyday meal for your feline companion"

C = "https://www.mojacalibra.sk/"
S = "https://www.shelma.eu/cz/kapsicky/"
B = "https://www.krmivo-brit.cz/pro-kocky/krmivo/kapsicky/"
SCZ = "https://www.sheba.cz/vyrobky/fresh-fine/sheba-fresh-fine-kapsicky-pro-dospele-kocky-"
SUK = "https://www.uk.sheba.com/wet-cat-food/fresh-fine/sheba-fresh-fine-adult-wet-cat-food-"

COMPLETENESS = {
    **{C + u: CAL_LIFE for u in [
        "calibra-cat-life-kapsicka-adult-veal-in-gravy-85g", "calibra-cat-life-kapsicka-adult-beef-in-gravy-85g",
        "calibra-cat-life-kapsicka-adult-duck-in-gravy-85g", "calibra-cat-life-kapsa-adult-turkey-in-gravy-85g",
        "calibra-cat-life-kapsicka-sterilised-duck-in-gravy-85g", "calibra-cat-life-kapsicka-sterilised-salmon-in-gravy-85g",
        "calibra-cat-life-kapsicka-kitten-turkey-in-gravy-85g", "calibra-cat-life-kapsicka-kitten-salmon-in-gravy-85g"]},
    **{C + u: CAL_PREM for u in [
        "calibra-cat-kapsicka-premium-kitten-salmon-100g", "calibra-cat-kapsicka-premium-kitten-turkey-chicken-100g",
        "calibra-cat-kapsicka-premium-adult-chicken-beef-100g", "calibra-cat-kapsicka-premium-adult-trout-salmon-100g",
        "calibra-cat-kapsicka-premium-adult-duck-chicken-100g", "calibra-cat-kapsicka-premium-adult-lamb-poultry-100g",
        "calibra-cat-kapsicka-premium-sterilised-liver-100g", "calibra-cat-kapsicka-premium-sterilised-salmon-100g"]},
    **{S + u: SHELMA_AD for u in [
        "dusene-filetky-bohate-na-hovezi-s-rajcaty-a-bylinkami-v-omacce/", "dusene-filetky-bohate-na-kureci-s-rajcaty-a-bylinkami-v-omacce/",
        "dusene-filetky-bohate-na-kachni-s-brusinkami-v-omacce/", "dusene-filetky-bohate-na-kruti-s-rakytnikem-v-omacce/",
        "dusene-filetky-s-lososem-a-spirulinou-v-omacce/", "dusene-filetky-s-treskou-a-spirulinou-v-omacce/"]},
    **{S + u: SHELMA_KIT for u in [
        "dusene-filetky-pro-kotata-s-lososem-a-rakytnikem-v-omacce/", "dusene-filetky-pro-kotata-bohate-na-kruti-s-brusinkami-v-omacce/",
        "dusene-filetky-bohate-na-hovezi-a-kruti-s-rajcaty-a-bylinkami,-kachni-a-kureci-s-brusinkami-v--zele/",
        "dusene-filetky-s-lososem-a-treskou-se-spirulinou,-s-tunakem-a-pstruhem-se-spenatem-v--zele/"]},
    "https://bozita.com/cz/products/bozita-masove-a-rybi-menu-kousky-v-zele/": "Použití: Kompletní krmivo pro kočky",
    "https://bozita.com/cz/products/bozita-masove-a-rybi-menu-kousky-v-omacce/": "Použití: Kompletní krmivo pro kočky",
    B + "bcc-sterilized-fillets-in-gravy-w-healthy-rabbit-85-g.html":
        "Kompletní superprémiové bezobilné krmivo pro dospělé kastrované kočky ve formě filetek ve šťávě s dietním králíkem",
    B + "brit-premium-cat-pouches-with-beef-stew-peas-100-g.html":
        "Kompletní prémiová kapsička s hovězím a hráškem v omáčce pro dospělé kočky všech plemen",
    B + "brit-premium-cat-delicate-fillets-in-gravy-with-duck-for-sterilised-85-g.html":
        "Kompletní vlhké krmivo ve formě masových filetek s kachnou v lahodné šťávě pro sterilizované kočky.",
    **{SCZ + u: SHEBA_CZ for u in [
        "drubezi-vyber", "kureci-a-kruti-6-x-50g", "hovezi-a-kureci", "losos-a-tunak", "kureci-a-losos", "rybi-vyber"]},
    **{SUK + u: SHEBA_UK for u in [
        "poultry-in-gravy-pouches-50x50g-15x50g-6x50g", "chicken-turkey-gravy-6x50g-pouches",
        "beef-chicken-gravy-6-x-50g-pouches", "fish-in-gravy-pouches-50x50g-15x50g",
        "tuna-salmon-in-jelly-6x50g-pouches", "salmon-tuna-in-gravy-6x50g-pouches",
        "tuna-and-cod-in-gravy-6x50g-pouches", "meaty-pieces-in-gravy-pouches-50x50g-15x50g"]},
}

# taurine that is on the page but was missing from additives_per_kg_raw
TAURINE = {
    B + "brit-care-cat-fillets-in-gravy-with-savory-salmon-85-g.html": "taurin (3a370) 500 mg",
}

# re-checked, still not stated by the manufacturer
NOTES = {
    **{SCZ + u: "Doplnkové látky (vrátane taurínu) ani v prehliadači stránka neuvádza — nejde o chybu sťahovania, CZ web ich nezverejňuje."
       for u in ["drubezi-vyber", "kureci-a-kruti-6-x-50g", "hovezi-a-kureci", "losos-a-tunak", "kureci-a-losos", "rybi-vyber"]},
    B + "brit-premium-cat-delicate-fillets-in-gravy-with-salmon-for-sterilised-85-g-1.html":
        "Kompletnosť ani v prehliadači neuvedená (podnadpis: „Delikátní šťavnaté masové filetky…“).",
    "https://www.krmivo-brit.cz/pro-kocky/brit-care-cat-sterilized-fillets-in-gravy-with-healthy-rabbit-85-g.html":
        "URL presmeruje na úvodnú stránku brit.pet — produkt (táto URL) už neexistuje.",
    "https://www.krmivo-brit.cz/pro-kocky/brit-care-cat-mousse-real-tuna-6-x-25-g.html":
        "URL presmeruje na úvodnú stránku brit.pet — produkt (táto URL) už neexistuje.",
    "https://www.stuzzy.it/shreds-with-beef-85g-cat":
        "Len marketingová otázka „Are you looking for a complete and palatable meal…“ — nepovažuje sa za deklaráciu kompletnosti.",
    "https://www.stuzzy.it/multipack-shreds-with-salmon-with-cod-12x85g-sterilized-cat":
        "Len marketingové „complete, genuine recipes“ — nepovažuje sa za deklaráciu kompletnosti.",
    "https://www.purina.cz/kocka/krmivo-pro-kocky/produkt-proplan-senior-sterilised-maintenance-kapsicka-pro-kocky-s-krutou":
        "Kompletnosť ani v prehliadači neuvedená.",
    "https://www.purina.cz/kocka/krmivo-pro-kocky/produkt-proplan-domaci-kocka-kapsicky-a-konzervy-indoor-losos":
        "Analytické zložky ani v prehliadači stránka neuvádza (uvádza „Kompletní krmivo pro dospělé kočky“ a taurin 630).",
    "https://www.purina.cz/kocka/krmivo-pro-kocky/produkt-proplan-veterinarni-diety-onemocneni-ledvin-kapsicka-losos":
        "Popol ani v prehliadači stránka neuvádza — NFE sa preto nepočíta.",
    "https://www.royalcanin.com/sk/cats/products/retail-products/sterilised-gravy-4095":
        "Taurín ani v prehliadači medzi doplnkovými látkami neuvedený.",
    "https://kattovit.com/en/products/nassfutter-ente-reis-frischebeutel-24-x-85g-gastro":
        "Kompletnosť ani v prehliadači neuvedená.",
    "https://carnilove.com/sk/produkty/trout-enriched-with-echinacea-gravy-pouch-for-cats-85-g":
        "Kompletnosť ani v prehliadači neuvedená; taurín (3a370) 1 400 mg potvrdený.",
    "https://barkingheads.co.uk/products/paw-lickin-chicken-wet-pouch":
        "Kompletnosť ani v prehliadači neuvedená; popol 0,5 % je skutočne deklarovaná hodnota výrobcu.",
}


def note(p, text):
    old = p.get("fetch_notes", "") or ""
    entry = f"{TAG} {text}"
    if entry not in old:
        p["fetch_notes"] = (old + " | " if old else "") + entry


seen = set()
for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
    data = json.load(open(path, encoding="utf-8"))
    changed = False
    for p in data.get("products", []):
        u = p.get("url", "")
        if u in COMPLETENESS:
            if p.get("completeness_statement_raw") != COMPLETENESS[u]:
                note(p, f"Kompletnosť doplnená z produktovej stránky (predtým: {p.get('completeness_statement_raw') or 'prázdne'!r}).")
                p["completeness_statement_raw"] = COMPLETENESS[u]
                changed = True
            seen.add(u)
        if u in TAURINE:
            seen.add(u)
            if TAURINE[u] not in (p.get("additives_per_kg_raw") or ""):
                p["additives_per_kg_raw"] = ((p.get("additives_per_kg_raw") or "") + "; " + TAURINE[u]).lstrip("; ")
                note(p, f"Doplnené z produktovej stránky: {TAURINE[u]}.")
                changed = True
        if u in NOTES:
            before = p.get("fetch_notes")
            note(p, NOTES[u])
            changed |= before != p.get("fetch_notes")
            seen.add(u)
    if changed:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated", os.path.basename(path))

missing = (set(COMPLETENESS) | set(TAURINE) | set(NOTES)) - seen
print("URLs not found in raw_data:", sorted(missing) or "none")
