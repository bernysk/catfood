# -*- coding: utf-8 -*-
"""Turn the automatically scraped manufacturer pages (scrape_proplan.py,
scrape_royalcanin.py, scrape_others.py) and the pages collected in the built-in
browser (raw_data/hills_vet.json, raw_data/calibra_vet.json, raw_data/eminent_vet.json) into product records with the same fields as the
hand-curated raw_data/gi_dry.json.

Rules
- Text fields stay verbatim (only cut into composition / analytics / additives).
- Products already curated by hand in gi_dry.json (same URL) are skipped.
- Royal Canin: the SK page is used; the CZ site sells the same range under the
  same product IDs and stays in the raw file only.
- Pro Plan: CZ, SK and UK pages are all kept (market filter in the table);
  purina.eu product pages returned HTTP 500 and are reported, not used.
- Hill's, Brit, Farmina, Calibra, Virbac, Eminent (SK/CZ pages) and Trovet (English page;
  no SK/CZ manufacturer site) are dry veterinary diets only.
- Category comes from the product name (keyword table below). Fibre types are
  detected automatically from the composition and labelled as such; protein
  sources are NOT guessed for scraped products.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# order matters: first match wins ("Renal + Mobility" is a renal diet)
CATEGORY_RULES = [
    (r"renal|\bnf\b|ledvin|kidney|obli|\bk/d", "diéta – obličky"),
    (r"urinary|\bur\b|s/o|mo[čc]ov|struvit|urolog|\bc/d|\bs/d", "diéta – močové cesty"),
    (r"gastro|\ben\b|traviciho|intestin|fibre response", "GI diéta"),
    (r"hypoallerg|anallerg|ultrahypo|\bha\b|alergie|sensitivity control|hydrolysed protein|\bz/d|\bd/d", "diéta – alergie"),
    (r"diabet|\bdm\b|cukrovk|\bm/d", "diéta – diabetes"),
    (r"hepat|\bhp\b|jater|\bl/d", "diéta – pečeň"),
    (r"obes|\bom\b|satiety|weight|obezit|metabolic|\br/d|\bw/d", "diéta – chudnutie"),
    (r"\by/d|thyroid|[šs]t[íi]tn", "diéta – štítna žľaza"),
    (r"cardiac", "diéta – srdce"),
    (r"mobility|\bj/d", "diéta – kĺby"),
    (r"calm", "diéta – stres"),
    (r"dental|\bt/d", "diéta – zuby"),
    (r"skin|derma", "diéta – koža"),
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


def _rec(brand, prefix, key, name, url, market, comp, ana, add, note, **kw):
    r = {
        "id": f"{prefix}-{key}"[:90], "brand": brand, "name": name,
        "category": category(name, True), "type": "veterinárna diéta",
        "lifestage": lifestage(name), "url": url, "market": market,
        "statement_raw": "", "purpose_raw": "", "period_raw": "", "sizes": [],
        "composition_raw": comp, "analytical_raw": ana, "additives_raw": add, "typical_raw": "",
        "protein_sources": [], "fibre_types": fibres(comp), "auto": True,
        "fetch_notes": note + " Zdroje bielkovín neurčené; druhy vlákniny rozpoznané automaticky zo zloženia.",
    }
    r.update(kw)
    return r


def _slug(url):
    return re.sub(r"\.html$", "", url.rstrip("/").rsplit("/", 1)[-1])


def hills(existing):
    path = os.path.join(HERE, "raw_data", "hills_vet.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for r in d["products"]:
        if r["url"] in existing:
            continue
        lab = r["label"]
        comp = cut(lab, r"SLOŽENÍ\s*:", r"ANALYTICK[ÉA] SLO[ŽZ]")
        ana = cut(lab, r"ANALYTICK[ÉA] SLO[ŽZ](?:KY|ENÍ)\s*:", r"PŘÍDATNÉ LÁTKY")
        add = cut(lab, r"PŘÍDATNÉ LÁTKY[^:]*:", None)
        # energy sometimes follows the additives block ("Využitelná energie: 3 149 kcal/kg")
        en = re.search(r"(Využitelná energie[^.]*?kcal/kg|Metabolizovaná energie[^:]*:\s*[\d,]+\s*MJ/kg)", add)
        if en and en.group(1) not in ana:
            ana = (ana + " ¦ " + en.group(1)).strip(" ¦")
        name = "Prescription Diet " + re.sub(r"\s*(suché )?krmivo pro kočky", "", r["h1"]).strip()
        out.append(_rec("Hill's", "hills", _slug(r["url"]), name, r["url"], r.get("market", "CZ"), comp, ana, add,
                        f"Načítané vstavaným prehliadačom ({d['fetched_at']}; hillspet.cz blokuje skripty). Text etikety doslovne.",
                        statement_raw=r.get("intro", ""), period_raw=r.get("per", ""), sizes=r.get("sizes", []),
                        typical_raw=r.get("typ", "")))
    return out


def _pairs(cells, pct):
    """'Proteíny | 44 | Tuky | 12' -> 'Proteíny 44 %, Tuky 12 %' (the column heading says '% v krmive')."""
    toks = [t.replace("\u200b", "").strip(" ,.") for t in cells.split("|")]
    toks = [t for t in toks if t and t not in ("%", "% v krmive")]
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if re.search(r"[A-Za-zÀ-ž]", t) and re.search(r"\s\d+(?:[.,]\d+)?\s*%?$", t) and "(" not in t:
            out.append(re.sub(r"\s*%$", "", t) + (" %" if pct else "")); i += 1; continue   # "Tuky 13,5"
        if i + 1 < len(toks) and re.fullmatch(r"[\d ]+(?:[.,]\d+)?\s*%?", toks[i + 1]):
            v = toks[i + 1].replace("%", "").strip()
            out.append(f"{t} {v}" + (" %" if pct else "")); i += 2; continue
        if i + 1 < len(toks):
            out.append(f"{t} {toks[i + 1]}"); i += 2; continue
        i += 1
    return ", ".join(out)


def others(existing):
    path = os.path.join(HERE, "raw_data", "others_vet.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    out = []
    src = f"Automaticky stiahnuté (scrape_others.py, {d['fetched_at']})"
    for r in d["products"]:
        if r.get("fetch_status") != "ok" or r["url"] in existing:
            continue
        b = r["brand"]
        if b == "Farmina" and not r.get("is_dry"):
            continue
        name = re.sub(r"^(Brit|Trovet)\s+", "", r["name"])
        if b == "Virbac":
            name = "Veterinary HPM " + name.split(" – ")[0]
            ana = _pairs(r["analytical_cells"], True)
            m = re.search(r"Metabolizovateľná energia – vypočítané \(kcal/100 g\) \| ([\d ,]+)", r["energy_cells"])
            if m:
                ana += f" ¦ Metabolizovateľná energia – vypočítané: {m.group(1).strip()} kcal/100 g"
            out.append(_rec(b, "virbac", _slug(r["url"])[:40], name, r["url"], "SK", r["composition_raw"], ana,
                            _pairs(r["additives_cells"], False),
                            src + ". Analytické zložky sú na stránke tabuľka bez znaku % pri číslach (stĺpec „% v krmive“); % doplnené podľa hlavičky stĺpca.",
                            purpose_raw=r.get("purpose_raw", "")[:600], sizes=r.get("sizes", [])))
            continue
        prefix = {"Brit": "brit", "Farmina": "farmina", "Trovet": "trovet"}[b]
        note = src + (". Trovet nemá stránku pre SK/CZ – použitá anglická stránka výrobcu (trovet.com); doplnkové látky stránka neuvádza." if b == "Trovet" else ".")
        out.append(_rec(b, prefix, _slug(r["url"]), name, r["url"], r["market"], r.get("composition_raw", ""),
                        r.get("analytical_raw", ""), r.get("additives_raw", ""), note,
                        statement_raw=r.get("statement_raw", ""), period_raw=r.get("period_raw", "")[:600],
                        sizes=r.get("sizes", [])))
    return out


def calibra(existing):
    path = os.path.join(HERE, "raw_data", "calibra_vet.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    out = []
    strip = lambda t, lab: re.sub(r"^" + lab + r"\s*:?\s*", "", t)
    for r in d["products"]:
        if r["url"] in existing:
            continue
        out.append(_rec("Calibra", "calibra", _slug(r["url"]), re.sub(r"^Calibra\s+", "", r["name"]), r["url"], "SK",
                        strip(r["composition_raw"], "Zloženie"), strip(r["analytical_raw"], "Analytické zložky"),
                        strip(r["additives_raw"], "Nutričné aditíva v 1 kg"),
                        "Načítané vstavaným prehliadačom (2026-10-15; mojacalibra.sk zobrazí skriptom prázdnu stránku). Text etikety doslovne.",
                        statement_raw=r.get("statement_raw", ""), period_raw=r.get("period_raw", ""), sizes=r.get("sizes", [])))
    return out


def eminent(existing):
    path = os.path.join(HERE, "raw_data", "eminent_vet.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for r in d["products"]:
        if r["url"] in existing:
            continue
        out.append(_rec("Eminent", "eminent", _slug(r["url"]).replace("eminent-", "", 1), r["name"], r["url"], r.get("market", "CZ"),
                        r["composition_raw"], r["analytical_raw"], r["additives_raw"],
                        f"Načítané vstavaným prehliadačom ({d['fetched_at']}): text zo stránky výrobcu; analytické hodnoty "
                        "a energia z PDF tabuľky výrobcu odkázanej z produktovej stránky. Sodík, draslík, horčík a vlhkosť výrobca neuvádza.",
                        statement_raw=r.get("statement_raw", ""), purpose_raw=r.get("purpose_raw", ""),
                        period_raw=r.get("period_raw", ""), sizes=r.get("sizes", []),
                        vitamins_total=True))   # PDF "Obsah látek" = content, not added amount
    return out


def load(existing_urls):
    pp, failed = proplan(existing_urls)
    return (pp + royalcanin(existing_urls) + hills(existing_urls) + others(existing_urls)
            + calibra(existing_urls) + eminent(existing_urls)), failed
