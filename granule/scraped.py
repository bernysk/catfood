# -*- coding: utf-8 -*-
"""Turn the automatically scraped manufacturer pages (scrape_proplan.py,
scrape_royalcanin.py) into product records with the same fields as the
hand-curated raw_data/gi_dry.json.

Rules
- Text fields stay verbatim (only cut into composition / analytics / additives).
- Products already curated by hand in gi_dry.json (same URL) are skipped.
- Royal Canin: the SK page is used; the CZ site sells the same range under the
  same product IDs and stays in the raw file only.
- Pro Plan: CZ, SK and UK pages are all kept (market filter in the table);
  purina.eu product pages returned HTTP 500 and are reported, not used.
- Category comes from the product name (keyword table below). Fibre types are
  detected automatically from the composition and labelled as such; protein
  sources are NOT guessed for scraped products.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# order matters: first match wins ("Renal + Mobility" is a renal diet)
CATEGORY_RULES = [
    (r"renal|\bnf\b|ledvin|kidney|obli", "diéta – obličky"),
    (r"urinary|\bur\b|s/o|mo[čc]ov", "diéta – močové cesty"),
    (r"gastro|\ben\b|traviciho|intestin|fibre response", "GI diéta"),
    (r"hypoallerg|anallerg|\bha\b|alergie|sensitivity control|hydrolysed protein", "diéta – alergie"),
    (r"diabet|\bdm\b|cukrovk", "diéta – diabetes"),
    (r"hepat|\bhp\b|jater", "diéta – pečeň"),
    (r"obes|\bom\b|satiety|weight|obezit", "diéta – chudnutie"),
    (r"cardiac", "diéta – srdce"),
    (r"mobility", "diéta – kĺby"),
    (r"calm", "diéta – stres"),
    (r"dental", "diéta – zuby"),
    (r"skin", "diéta – koža"),
]
FIBRES = [
    (r"psyll", "psyllium"), (r"fruktooligo|frukto-oligo|fructo-?oligo|\bfos\b", "FOS"),
    (r"inul[ií]n|[čc]ekank|[čc]akank|chicory", "inulín/čakanka"), (r"manno|mann[áa]n|\bmos\b", "MOS"),
    (r"[řr]epn|repn|cukrovarsk|beet", "repné rezky"), (r"lignocel", "lignocelulóza"),
    (r"celul[óo]z|cellulose", "celulóza"), (r"hrachov[éá] (slupky|šupky|vl[áa]knin)|pea hulls|pea fibre", "hrachová vláknina"),
    (r"rastlinn[áa] vl[áa]knina|rostlinn[áa] vl[áa]knina|vegetable fibre|plant fibre", "rastlinná vláknina (bližšie neurčená)"),
]


def category(name, vet):
    n = name.lower()
    if not vet:
        return "citlivé trávenie (bežné krmivo)" if re.search(r"delicate|digest", n) else "bežné krmivo"
    for pat, cat in CATEGORY_RULES:
        if re.search(pat, n):
            return cat
    return "veterinárna – iná/udržiavacia"


def fibres(comp):
    found = [lab for pat, lab in FIBRES if re.search(pat, comp, re.I)]
    return found or ["žiadne rozpoznané"]


def lifestage(name):
    n = name.lower()
    if re.search(r"kitten|kot[ěe]|ma[čc]iat|ko[ťt]at", n):
        return "mačiatka"
    if re.search(r"7\s*\+|seven plus|longevis|ageing|senior|mature", n):
        return "staršie mačky"
    return "dospelé"


def cut(text, start, stop):
    m = re.search(start, text, re.I)
    if not m:
        return ""
    rest = text[m.end():]
    s = re.search(stop, rest, re.I) if stop else None
    return (rest[:s.start()] if s else rest).strip(" ¦:")


def sentence(text, pat):
    for part in re.split(r"(?<=[.!])\s+|\s¦\s", text):
        if re.search(pat, part, re.I):
            return part.strip()
    return ""


def proplan(existing):
    path = os.path.join(HERE, "raw_data", "proplan_dry.json")
    if not os.path.exists(path):
        return [], {}
    d = json.load(open(path, encoding="utf-8"))
    out, failed = [], {}
    for mk, recs in d["markets"].items():
        for r in recs:
            if r.get("fetch_status") != "ok":
                failed.setdefault(mk, []).append(f"{r['url']} (HTTP {r.get('http_status')})")
                continue
            if r["url"] in existing:
                continue
            s = r.get("sections", {})
            nut = s.get("nutrition", "")
            comp = cut(nut, r"(Složení|Zloženie|Ingredients)\s*:?", r"(Analytické složky|Analytické zložky|Nutrition & Analytical Constituents|Analytical Constituents)")
            ana = cut(nut, r"(Analytické složky|Analytické zložky|Analytical Constituents)\s*:?", r"(Doplňkové látky|Nutriční doplňkové|Výživné doplnkové|Nutritional additives)")
            add = cut(nut, r"(Doplňkové látky|Nutriční doplňkové látky|Výživné doplnkové látky|Nutritional additives)\s*:?", None)
            kcal = re.findall(r"[^¦]*\d[^¦]*kcal[^¦]*", nut, re.I)
            if kcal and not re.search(r"kcal", ana, re.I):
                ana = (ana + " ¦ " + kcal[0].strip()).strip(" ¦")
            name = r.get("h1") or r.get("title", "")
            vet = bool(re.search(r"veterin", r["url"] + name, re.I))
            ov, fg = s.get("overview", ""), s.get("feeding-guide", "")
            slug = r["url"].rstrip("/").rsplit("/", 1)[-1]
            out.append({
                "id": f"pp-{mk.lower()}-{slug}"[:90], "brand": "Purina Pro Plan", "name": name,
                "category": category(name, vet),
                "type": "veterinárna diéta" if vet else "bežné krmivo (nie diéta)",
                "lifestage": lifestage(name), "url": r["url"], "market": mk,
                "statement_raw": sentence(ov, r"kompletn|complete (dietetic )?(pet )?food"),
                "purpose_raw": ov[:500], "period_raw": sentence(fg, r"t[ýy]d|t[ýy][žz]d|week|celo[žz]ivot|lifelong|lifetime"),
                "sizes": re.findall(r"\d+(?:[.,]\d+)?\s?(?:kg|g)\b", r.get("sizes_raw", "")),
                "composition_raw": comp, "analytical_raw": ana, "additives_raw": add, "typical_raw": "",
                "protein_sources": [], "fibre_types": fibres(comp), "auto": True,
                "fetch_notes": f"Automaticky stiahnuté (scrape_proplan.py, {d['fetched_at']}). Zdroje bielkovín neurčené; druhy vlákniny rozpoznané automaticky zo zloženia.",
            })
    return out, failed


def royalcanin(existing):
    path = os.path.join(HERE, "raw_data", "royalcanin_vet.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for r in d["markets"].get("SK", []):
        if r.get("fetch_status") != "ok" or r.get("technology") != "dry" or r["url"] in existing:
            continue
        s = r.get("sections", {})
        comp = s.get("composition", "")
        name = r.get("h1", "")
        slug = r["url"].rstrip("/").rsplit("/", 1)[-1]
        feeding = s.get("feeding", "") + " " + s.get("dvp", "")
        out.append({
            "id": f"rc-{slug}"[:90], "brand": "Royal Canin", "name": name,
            "category": category(name, True), "type": "veterinárna diéta",
            "lifestage": lifestage(name), "url": r["url"], "market": "SK",
            "statement_raw": r.get("statement_raw", ""), "purpose_raw": "",
            "period_raw": sentence(feeding, r"t[ýy][žz]d|t[ýy]d|celo[žz]ivot|week"),
            "sizes": [p.replace(".", ",") for p in r.get("packs", [])],
            "composition_raw": re.sub(r"^(ZLOŽENIE|COMPOSITION)\s*:?\s*", "", comp),
            "analytical_raw": s.get("analytical", ""),
            "additives_raw": re.split(r"ANALYTICK|ANALYTICAL", s.get("additives", ""))[0],
            "typical_raw": "", "protein_sources": [], "fibre_types": fibres(comp), "auto": True,
            "fetch_notes": f"Automaticky stiahnuté (scrape_royalcanin.py, {d['fetched_at']}) zo SK stránky výrobcu; CZ stránka má rovnaký produkt. Zdroje bielkovín neurčené; druhy vlákniny rozpoznané automaticky zo zloženia.",
        })
    return out


def load(existing_urls):
    pp, failed = proplan(existing_urls)
    return pp + royalcanin(existing_urls), failed
