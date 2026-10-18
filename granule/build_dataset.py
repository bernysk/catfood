# -*- coding: utf-8 -*-
"""Gastrointestinal dry diets for cats: raw_data/gi_dry.json -> dataset.json + index.html.

No A-E grade. Veterinary diets are compared on what a GI diet is supposed to do,
everything per 1000 kcal (what the cat actually eats), with every derived number
traceable to the verbatim label text kept next to it.

Energy priority: declared ME on the label > manufacturer's typical-analysis table
(Hill's) > modified Atwater estimate (flagged). Moisture is rarely declared on dry
food; when it is needed for an estimate, the typical value or an assumed 8 % is
used and the row is flagged.
"""
import json, os, re, sys, html
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = json.load(open(os.path.join(HERE, "raw_data", "gi_dry.json"), encoding="utf-8"))
ASSUMED_MOISTURE = 8.0
sys.path.insert(0, HERE)
import scraped  # Pro Plan, Royal Canin, Hill's, Brit, Farmina, Calibra, Virbac, Trovet pages
import nutrients_extra as nx  # omega-3, EPA+DHA, vitamin D3 (EU 2017/1492 maximum)
SCRAPED, SCRAPE_FAILED = scraped.load({p["url"] for p in RAW["products"]})
PRODUCTS = RAW["products"] + SCRAPED

def num(s):
    return float(s.replace(" ", "").replace(",", "."))

N = r"(\d+(?:[.,]\d+)?)"
LABELS = {
    "protein":  r"(?:hrub[éýá] )?(?:bielkoviny|b[íi]lkovin[ay]?\\?|prote[íi]ny?|dus[íi]kat[ée] l[áa]tky)",   # Hill's t/d: "Bílkovin\ 32,5 %"
    "fat":      r"(?:obsah tuku|oleje a tuky|fat content|hrub[ýá] tuky?|hrub[ée] tuky|\bfat\b|\btuky?\b)",   # Eminent PDF: "Tuk 19 %"
    "fiber":    r"(?:hrub[áé] )?(?:vl[áa]knina|crude fibres?)",
    "ash":      r"(?:hrub[ýé] )?(?:popol|popel|crude ash|obsah anorganick[ýé]ch l[áa]t(?:ek|ok)|miner[áa]ln[ei] l[áa]tky|inorganic matter|anorganick[ée] l[áa]tky)",
    "carb":     r"(?:sacharidy|carbohydrates?)",
    "moisture": r"(?:vlhkos[tť]|moisture)",
    "ca":       r"(?:v[áa]pn[íi]k|calcium)",
    "p":        r"(?:fosfor|phosphor(?:o)?us)",
    "na":       r"(?:sod[íi]k|sodium)",
    "k":        r"(?:drasl[íi]k|potassium)",
    "mg":       r"(?:ho[řr][čc][íi]k|magnesium)",
}

def parse_analytics(text):
    out = {}
    for key, lab in LABELS.items():
        m = re.search(lab + r"(?:\s*\([A-Za-z]{1,7}\))?\s*:?\s*" + N + r"\s*%", text, re.I)   # Trovet "Calcium (Ca) 0.95 %"
        if m:
            out[key] = num(m.group(1))
    return out

def parse_energy(p):
    """Return (kcal/kg, source)."""
    a = p["analytical_raw"]
    m = re.search(r"(\d[\d ]*[.,]?\d*)\s*kcal\s*/\s*kg", a, re.I)
    if m:
        return num(m.group(1)), "etiketa"
    m = re.search(r"kcal\s*/\s*kg\s*(\d[\d ]*)", a, re.I)        # Farmina: "EM Kcal/Kg 4253"
    if m:
        return num(m.group(1)), "etiketa"
    # Purina: "Metabolizovatelná energie (ME): 4,15.* *Vypočítaná" — unit missing,
    # matches 415 kcal/100 g on the UK page, i.e. kcal/g.
    m = re.search(r"\(ME\)\*?\s*:\s*(\d[.,]\d+)", a)          # also "(ME)* : 3,4 kcal/g"
    if m:
        return num(m.group(1)) * 1000, "etiketa (kcal/g, jednotka na stránke chýba)"
    m = re.search(r"(\d+[.,]\d+)\s*kcal\s*/\s*g\b", a, re.I)   # "Energy value: 4.15 kcal/g"
    if m:
        return num(m.group(1)) * 1000, "etiketa"
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*kcal\s*(?:per|/)\s*100\s*g", a, re.I)   # "415kcal per 100g"
    if m:
        return num(m.group(1)) * 10, "etiketa"
    m = re.search(r"(\d+[.,]\d+)\s*MJ\s*/\s*kg", a)                  # Hill's m/d: "16,5 MJ/kg"
    if m:
        return round(num(m.group(1)) * 239.006), "etiketa (prepočet z MJ/kg)"
    m = re.search(r"Kalorick[ýy] obsah\s*(\d[\d ]*)\s*kcal/kg", p.get("typical_raw", ""))
    if m:
        return num(m.group(1)), "priemerný obsah (výrobca)"
    # Same manufacturer, other market, only used when the recipe was checked to be
    # identical (composition, analytics, additives) — see fetch_notes.
    alt = p.get("energy_alt_raw", "")
    m = re.search(r"(\d[\d ]*[.,]?\d*)\s*kcal\s*/\s*kg", alt, re.I)
    if m:
        return num(m.group(1)), "stránka výrobcu UK (receptúra zhodná s CZ)"
    m = re.search(r"(\d[\d ]*[.,]?\d*)\s*kcal\s*per\s*100\s*g", alt, re.I)
    if m:
        return num(m.group(1)) * 10, "stránka výrobcu UK (receptúra zhodná s CZ)"
    return None, None

def typical_moisture(p):
    m = re.search(r"Vlhkost\s*" + N + r"\s*%", p.get("typical_raw", ""))
    return num(m.group(1)) if m else None

def taurine_mg_kg(p):
    t = p["additives_raw"] + " " + p["analytical_raw"]
    m = re.search(r"taur[íi]n[e]?\s*(?:\([^)]{0,12}\))?\s*:?\s*(\d[\d ]*[.,]?\d*)\s*(mg|g)\b", t, re.I)
    if m:
        v = num(m.group(1))
        return (v * 1000 if m.group(2).lower() == "g" else v), "etiketa"
    # Purina: "... mg/kg: Taurin: 1 100;" — unit only in the block heading
    m = re.search(r"mg/kg:\s*Taurin\s*:\s*(\d[\d ]*)", t, re.I)
    if m:
        return num(m.group(1)), "etiketa"
    m = re.search(r"Taur[íi]n\s*\(mg/kg\)\s*(\d[\d ]*)", t, re.I)       # Virbac table: "Taurín (mg/kg) 2 900"
    if m:
        return num(m.group(1)), "etiketa"
    m = re.search(r"Taur[íi]ne?\s*:?\s*" + N + r"\s*%", t, re.I)         # "Taurín 0,23 %"
    if m:
        return num(m.group(1)) * 10000, "etiketa"
    m = re.search(r"Taurin\s*" + N + r"\s*%", p.get("typical_raw", ""))
    if m:
        return num(m.group(1)) * 10000, "priemerný obsah (výrobca)"
    return None, None

def flags(p):
    c = p["composition_raw"]
    psy = re.search(r"psyll\w*[^,(]{0,25}?\(?\s*" + N + r"\s*%", c, re.I)
    return {
        "hydrolyzate": bool(re.search(r"hydroly[zs]", c, re.I)),
        "psyllium": bool(re.search(r"psyll", c, re.I)),
        "psyllium_pct": num(psy.group(1)) if psy else None,
        "inorganic_phosphate": bool(re.search(r"fosfore[čc]n|phosphate", c, re.I)),
        "live_probiotic": bool(re.search(r"Enterococcus|Lactobacillus", p["additives_raw"] + c)
                               and not re.search(r"deaktiv|inaktiv", c, re.I)),
        "paraprobiotic": bool(re.search(r"(Lactobacillus|Enterococcus)[^,]{0,40}(deaktiv|inaktiv)|"
                                        r"(deaktiv|inaktiv)[^,]{0,40}Lactobacillus", c, re.I)),
        "grain_or_gluten": bool(re.search(r"glut[ée]n|lepok|p[šs]enic|kukuric|kuku[řr]i[čc]|r[yý][žz]|rice|maize|wheat|[šs]pald|obilovin|obiloviny", c, re.I)),
        "soy": bool(re.search(r"s[óo]j|soya", c, re.I)),
    }

# FEDIAF 2025, Table III-4b (per 1000 kcal ME)
FEDIAF = {
    "protein_growth": 75.0, "protein_adult_neutered": 83.3,
    "ca_growth": 2.5, "p_growth": 2.1, "p_adult_neutered": 0.85,
}
# EU Reg. 2020/354, Annex B entry 20: Na >= 1.8 g/kg, K >= 5 g/kg (12 % moisture)
EU20 = {"na": 0.18, "k": 0.5}

rows = []
for p in PRODUCTS:
    an = parse_analytics(p["analytical_raw"])
    me, me_src = parse_energy(p)
    moist = an.get("moisture")
    moist_src = "etiketa" if moist is not None else None
    if moist is None and typical_moisture(p) is not None:
        moist, moist_src = typical_moisture(p), "priemerný obsah (výrobca)"
    if moist is None:
        moist, moist_src = ASSUMED_MOISTURE, f"predpoklad {ASSUMED_MOISTURE:g} %"
    need = all(k in an for k in ("protein", "fat", "fiber", "ash"))
    nfe = 100 - moist - an["protein"] - an["fat"] - an["fiber"] - an["ash"] if need else None
    if not need and "carb" in an and all(k in an for k in ("protein", "fat")):
        need, nfe = True, an["carb"]          # carbohydrate declared, ash not (Pro Plan UR CZ)
    atw = (3.5 * an["protein"] + 8.5 * an["fat"] + 3.5 * nfe) * 10 if need else None  # kcal/kg
    if me is None and atw is not None:
        me, me_src = round(atw), "odhad (Atwater, " + moist_src + ")"
    per = lambda k: round(an[k] * 10 * 1000 / me, 2) if (k in an and me) else None
    tau, tau_src = taurine_mg_kg(p)
    r = {
        "id": p["id"], "brand": p["brand"], "name": p["name"], "type": p["type"],
        "category": p.get("category", "GI diéta"),
        "lifestage": p["lifestage"], "url": p["url"], "market": p["market"],
        "sizes": p["sizes"], "analytics": an,
        "me_kcal_kg": me, "me_source": me_src,
        "moisture_used": moist, "moisture_source": moist_src,
        "nfe_pct": round(nfe, 1) if nfe is not None else None,
        "per_1000kcal": {k: per(k) for k in ("protein", "fat", "fiber", "ash", "ca", "p", "na", "k", "mg")},
        "energy_split_pct": ({"protein": round(350 * an["protein"] / atw * 10, 1),
                              "fat": round(850 * an["fat"] / atw * 10, 1),
                              "nfe": round(350 * nfe / atw * 10, 1)} if atw else None),
        "ca_p": round(an["ca"] / an["p"], 2) if ("ca" in an and "p" in an) else None,
        "taurine_mg_kg": tau, "taurine_source": tau_src,
        "flags": flags(p),
        "protein_sources": p["protein_sources"], "fibre_types": p["fibre_types"],
        "statement_raw": p["statement_raw"], "purpose_raw": p["purpose_raw"],
        "period_raw": p["period_raw"],
        "composition_raw": p["composition_raw"], "analytical_raw": p["analytical_raw"],
        "additives_raw": p["additives_raw"], "typical_raw": p.get("typical_raw", ""),
        "notes": p["fetch_notes"], "auto": bool(p.get("auto")),
        "vitamins_total": bool(p.get("vitamins_total")),
    }
    pk = r["per_1000kcal"]
    r["eu20_electrolytes"] = (None if ("na" not in an or "k" not in an)
                              else an["na"] >= EU20["na"] and an["k"] >= EU20["k"])
    r["fediaf_growth"] = {
        "protein": None if pk["protein"] is None else pk["protein"] >= FEDIAF["protein_growth"],
        "ca": None if pk["ca"] is None else pk["ca"] >= FEDIAF["ca_growth"],
        "p": None if pk["p"] is None else pk["p"] >= FEDIAF["p_growth"],
    }
    r["missing"] = [lab for key, lab in (("moisture", "vlhkosť"), ("ca", "vápnik"), ("p", "fosfor"),
                                         ("na", "sodík"), ("k", "draslík"), ("mg", "horčík")) if key not in an]
    if me_src != "etiketa" and not (me_src or "").startswith("etiketa"):
        r["missing"].insert(0, "energia na etikete")
    if tau is None:
        r["missing"].append("taurín")
    rows.append(r)

# Same product sold in several markets: identical declared protein/fat/ash/fibre
# for the same brand is treated as "same values" (a hint, not proof of one recipe).
groups = {}
for r in rows:
    r["same_values_markets"] = []
    a = r["analytics"]
    if all(k in a for k in ("protein", "fat", "ash", "fiber")):
        groups.setdefault((r["brand"], a["protein"], a["fat"], a["ash"], a["fiber"]), []).append(r)
for g in groups.values():
    mks = sorted({x["market"].split(" ")[0] for x in g})
    for x in g:
        x["same_values_markets"] = mks if len(mks) > 1 else []

# Borrow label energy from the same product in another market (identical declared
# protein/fat/ash/fibre) instead of an Atwater estimate, which ran ~8 % low.
for g in groups.values():
    donors = [x for x in g if (x["me_source"] or "").startswith("etiketa")]
    for x in g:
        if donors and (x["me_source"] or "").startswith("odhad"):
            dn = donors[0]
            me = x["me_kcal_kg"] = dn["me_kcal_kg"]
            x["me_source"] = f"stránka výrobcu {dn['market'].split(' ')[0]} (rovnaké deklarované hodnoty)"
            a = x["analytics"]
            x["per_1000kcal"] = {k: (round(a[k] * 10 * 1000 / me, 2) if k in a else None)
                                 for k in ("protein", "fat", "fiber", "ash", "ca", "p", "na", "k", "mg")}

# Omega-3 / EPA+DHA per 1000 kcal and vitamin D3 vs. the EU maximum — after the
# energy borrowing above, so the per-1000-kcal figures use the final energy.
for x in rows:
    me = x["me_kcal_kg"]
    o3 = nx.omega3_pct(x["analytical_raw"])
    ed, ed_how = nx.epa_dha_pct(x["analytical_raw"])
    x["omega3_g_1000kcal"] = round(o3 * 10000 / me, 2) if (o3 is not None and me) else None
    x["epa_dha_g_1000kcal"] = round(ed * 10000 / me, 2) if (ed is not None and me) else None
    x["epa_dha_declared"] = ed_how
    d3, kind = nx.vitamin_d3(x["analytical_raw"], x["additives_raw"], x["typical_raw"])
    if d3 is not None and x.pop("vitamins_total"):
        kind = "celkový"
    x.pop("vitamins_total", None)
    x["vit_d3_iu_kg"], x["vit_d3_kind"] = d3, kind
    x["vit_d3_iu_kg_12"] = nx.d3_at_12(d3, x["moisture_used"])
    x["vit_d3_over_eu"] = None if x["vit_d3_iu_kg_12"] is None else x["vit_d3_iu_kg_12"] > nx.EU_D3_MAX_12

# Feeding tables: grams/day for a 4 kg adult cat x energy = kcal/day the manufacturer
# recommends, compared with FEDIAF 2025 maintenance energy (75 x BW^0.67 kcal for an
# indoor/neutered cat = 190 kcal; 100 x BW^0.67 for a lean active cat = 253 kcal).
FEED = {}
for fn in ("feeding_browser.json", "feeding_scripted.json"):
    fp = os.path.join(HERE, "raw_data", fn)
    if os.path.exists(fp):
        for u, v in json.load(open(fp, encoding="utf-8"))["products"].items():
            if v.get("g_day_4kg") is not None or u not in FEED:   # a failed re-fetch must not erase a value
                FEED[u] = v
MER_NEUTERED_4KG = round(75 * 4 ** 0.67)
MER_ACTIVE_4KG = round(100 * 4 ** 0.67)
for x in rows:
    f = FEED.get(x["url"]) or {}
    g = f.get("g_day_4kg")
    x["feed_g_day_4kg"] = g
    x["feed_column"] = f.get("column")
    x["feed_table_raw"] = f.get("table_raw", "")
    x["feed_kcal_day_4kg"] = round(g * x["me_kcal_kg"] / 1000) if (g and x["me_kcal_kg"]) else None
    x["feed_vs_neutered_pct"] = (round(x["feed_kcal_day_4kg"] / MER_NEUTERED_4KG * 100)
                                 if x["feed_kcal_day_4kg"] else None)

not_included = dict(RAW.get("not_included", {}))
for mk, urls in SCRAPE_FAILED.items():
    not_included[f"Pro Plan {mk} ({len(urls)} stránok)"] = "Stránka výrobcu vrátila chybu: " + "; ".join(sorted(set(urls)))
payload = {"generated": RAW["fetched_at"], "count": len(rows), "products": rows,
           "mer_4kg": {"neutered_indoor": MER_NEUTERED_4KG, "active": MER_ACTIVE_4KG},
           "not_included": not_included}
with open(os.path.join(HERE, "dataset.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)

# --- index.html (static, data inlined so it also opens from disk) ------------
TEMPLATE = open(os.path.join(HERE, "index.template.html"), encoding="utf-8").read()
blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(TEMPLATE.replace("/*DATA*/null", blob))

# --- console summary ---------------------------------------------------------
print(f"products: {len(rows)}")
for r in rows:
    pk = r["per_1000kcal"]
    print(f"  {r['brand'][:10]:10} {r['name'][:38]:38} ME {r['me_kcal_kg'] or '-':>5} ({(r['me_source'] or '-')[:9]}) "
          f"P {pk['protein'] or '-':>6} F {pk['fat'] or '-':>5} Phos {pk['p'] or '-':>4} Na/K ok={r['eu20_electrolytes']} "
          f"miss={','.join(r['missing'])}")
