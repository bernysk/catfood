# -*- coding: utf-8 -*-
"""Builds a normalized dataset (dataset.json) from raw_data/*.json for the cat wet-food survey.

Parsing is best-effort over verbatim label text; every derived number keeps a
reference to the raw string it came from so it can be audited.
"""
import json, re, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
OUT = os.path.join(os.path.dirname(__file__), "dataset.json")

def num(s):
    return float(s.replace(",", "."))

# --- analytics parsing -------------------------------------------------------
MINMAX = r"(?:\((?:min|max)\.?\)\s*)?"
LABELS = {
    "protein":  r"(?:hrub[ýé]\s+)?(?:prote[ií]n|b[íi]lkoviny|bielkoviny|dus[íi]kat[ée]\s+l[áa]tky|crude\s+protein|rohprotein)",
    "fat":      r"(?:hrub[ýé]\s+|crude\s+)?(?:tuk\w*|fat(?:\s+content)?|oleje\s+a\s+tuky|obsah\s+tuk\w*|fettgehalt|rohfett)",
    "fiber":    r"(?:hrub[áé]\s+|crude\s+)?(?:vl[áa]knin\w*|fib(?:re|er)s?|rohfaser)",
    "ash":      r"(?:hrub[ýé]\s+|crude\s+)?(?:pop[oe]?l|ash|inorganic\s+matter|anorganick\w+\s+l[áa]t\w*|rohasche)",
    "moisture": r"(?:vlhkos[tť][i]?|moisture(?:\s+content)?|feuchte)",
}

def parse_analytics(text):
    out = {}
    if not text:
        return out
    for key, label in LABELS.items():
        # The gap between a label and its number must not cross a list separator,
        # otherwise "crude protein, 5.0% fat" reads protein as the fat figure.
        m = re.search(label + r"[\s:=]{0,4}" + MINMAX + r"(\d+[.,]?\d*)\s*%?", text, re.IGNORECASE)
        if not m:  # reversed order: "8.0% crude protein"
            m = re.search(r"(\d+[.,]?\d*)\s*%\s*" + label, text, re.IGNORECASE)
        if m:
            out[key] = num(m.group(1))
    return out

def parse_taurine(*texts):
    for t in texts:
        if not t:
            continue
        m = re.search(r"taur[íi]n[eu]?\D{0,25}?(\d[\d\s]*[.,]?\d*)\s*mg", t, re.IGNORECASE)
        if m:
            return num(m.group(1).replace(" ", ""))
    return None

def parse_energy(text):
    """Return kcal/100g if derivable."""
    if not text:
        return None
    m = re.search(r"(\d+[.,]?\d*)\s*kcal\s*/\s*100\s*g", text, re.IGNORECASE)
    if m:
        return num(m.group(1))
    m = re.search(r"(\d+[.,]?\d*)\s*kcal\s*/\s*kg", text, re.IGNORECASE)
    if m:
        return round(num(m.group(1)) / 10.0, 1)
    m = re.search(r"(\d+[.,]?\d*)\s*kcal\s*/\s*g", text, re.IGNORECASE)
    if m:
        return round(num(m.group(1)) * 100.0, 1)
    return None

FERMENTABLE = r"inul[ií]n|fos\b|frukto|fructo|psyll?i|čekank|cakank|čakank|chicory"
BULK = r"lignocelul[óo]z|celul[óo]z|cellulose"

def prebiotic_class(comp, extra=""):
    t = f"{comp or ''} {extra or ''}".lower()
    if re.search(FERMENTABLE, t):
        return "fermentovateľné (inulín/FOS/psyllium)"
    if re.search(BULK, t):
        return "objemové (lignocelulóza)"
    return "žiadne deklarované"

SUGAR = r"\bcukr|various\s+sugars|r[ôo]zne\s+cukry"
GRAIN = r"obilovin|obilnin|cereals?\b|pšeničn|wheat|r[yý]ž|rice|ryžov"

def flags(comp):
    t = (comp or "").lower()
    return {
        "sugar": bool(re.search(SUGAR, t)),
        "grain": bool(re.search(GRAIN, t)),
    }

SPECIES = r"(kur[aeäc][\w]*|kuře[\w]*|chicken|hov[äe]dz[\w]*|hověz[\w]*|beef|morčac[\w]*|mork[aayu]\b|kr[uů]t[\w]*|krocan[\w]*|turkey|los[oa]s[\w]*|salmon|tuniak[\w]*|tuň[áa]k[\w]*|tuna|treska[\w]*|cod|kač[aíi][\w]*|kachn[\w]*|duck|jahňac[\w]*|jehněč[\w]*|lamb|kr[áa]l[ií]k[\w]*|rabbit|pstruh[\w]*|trout|makrel[\w]*|mackerel|sleď|herring|okoun[\w]*|perch|krab[\w]*|crab|krevet[\w]*|shrimps?|sob[íi\w]*|reindeer|los[íi][\w]*|elk|j[áa]tra|pečeň[\w]*|peceň[\w]*|liver|šunk[\w]*|ham|srdc[\w]*|diviak[\w]*|diviač[\w]*|boar|bažant[\w]*|pheasant|prepelic[\w]*|quail|perličk[\w]*|guinea|sardinka[\w]*|sardine|b[íi]l[áa]\s+ryba|whitefish|white\s+fish|fresh\s+deboned\s+\w+|fresh\s+salmon)"

def max_named_meat_pct(comp):
    """Highest percentage that is attributable to a *specific named species*.

    Label percentages come in two orders ("krůtí 8 %" and "9 % treska"), and block
    totals ("maso a výrobky živočišného původu 50 % (krůtí 8 %)") must not be
    credited as named meat just because a species appears later in the sentence.
    So: look backwards freely, but forwards only up to the next bracket/comma.
    """
    if not comp:
        return None
    best = None
    for m in re.finditer(r"(\d+[.,]?\d*)\s*%", comp):
        before = comp[max(0, m.start() - 35):m.start()].lower()
        fwd = comp[m.end():m.end() + 14].lower()
        fwd = re.split(r"[(),;|]", fwd)[0]          # stop at the next block boundary
        if re.search(SPECIES, before) or re.search(SPECIES, fwd):
            v = num(m.group(1))
            if v < 70:  # 70%+ is virtually always a block total, not one species
                best = max(best or 0, v)
    return best

# Completeness is a reading task, not a pattern-matching task: labels contain
# negations ("not explicitly labeled complementary") and sentences holding both
# words at once, where keyword matching inverts the meaning. The verdicts live in
# curated.json, keyed by the verbatim label text; anything unseen is reported
# rather than guessed.
CURATED = json.load(open(os.path.join(os.path.dirname(__file__), "curated.json"),
                         encoding="utf-8"))["completeness"]
UNKNOWN_COMPLETENESS = set()

def completeness(statement):
    s = (statement or "").strip()
    if s in CURATED:
        return CURATED[s]
    UNKNOWN_COMPLETENESS.add(s)
    return "neuvedené"

# --- load --------------------------------------------------------------------
rows = []
for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.json"))):
    fname = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    file_brand = data.get("brand", "")
    for p in data.get("products", []):
        brand = p.get("sub_brand") or p.get("brand") or file_brand or fname.replace(".json", "")
        brand = {"Meowing Heads (sold on barkingheads.co.uk)": "Meowing Heads",
                 "Purina": "Purina Pro Plan"}.get(brand, brand)
        name = p.get("name", "")
        comp = p.get("composition_raw", "")
        # Bozita nested flavours -> merge flavour compositions for parsing/display
        if not comp and p.get("flavours"):
            comp = " | ".join(
                f"{fl.get('flavour','')}: {fl.get('composition_raw','')}" for fl in p["flavours"]
            )
        an_raw = p.get("analytical_constituents_raw", "")
        add_raw = p.get("additives_per_kg_raw", "")
        an = parse_analytics(an_raw)
        # derived (dry matter)
        derived = {}
        # NFE is a difference calculation, so it is only meaningful when every
        # subtracted component is actually on the label. A missing ash figure
        # would silently inflate the carbohydrate estimate.
        if all(k in an for k in ("protein", "fat", "moisture", "fiber", "ash")):
            dm = 100.0 - an["moisture"]
            fiber = an["fiber"]
            ash = an["ash"]
            nfe = 100.0 - an["moisture"] - an["protein"] - an["fat"] - fiber - ash
            if dm > 0:
                derived = {
                    "dm": round(dm, 1),
                    "protein_dm": round(an["protein"] / dm * 100, 1),
                    "fat_dm": round(an["fat"] / dm * 100, 1),
                    "carbs_nfe_dm": round(max(nfe, 0.0) / dm * 100, 1),
                    "ash_dm": round(ash / dm * 100, 1) if ash else None,
                    # At >=85% moisture the dry matter base is so small (<=15%) that a
                    # 1pp labelling/rounding error in moisture swings every DM figure by
                    # several points. Such rows are mathematically correct but fragile.
                    "dm_unreliable": dm <= 15.0,
                }
        energy = parse_energy(p.get("energy_value_raw", "") or an_raw)
        taur = parse_taurine(add_raw, comp)
        # FEDIAF taurine minima are expressed on dry matter; as-fed values on a
        # ~80% moisture wet food must be divided by DM to be comparable.
        taur_dm = None
        if taur is not None and derived.get("dm"):
            taur_dm = round(taur / (derived["dm"] / 100.0))
        market = p.get("market") or ("UK" if "uk.sheba" in p.get("url", "") or "barkingheads" in p.get("url", "") else
                                     "CZ/SK")
        compl_stmt = p.get("completeness_statement_raw", "")
        rows.append({
            "source_file": fname,
            "brand": brand,
            "name": name,
            "url": p.get("url", ""),
            "market": market,
            "texture": p.get("texture") or p.get("product_line") or p.get("product_type") or p.get("range") or "",
            "lifestage": p.get("lifestage", ""),
            "fetch_status": p.get("fetch_status", ""),
            "composition_raw": comp,
            "analytics_raw": an_raw,
            "additives_raw": add_raw,
            "analytics": an,
            "derived": derived,
            "energy_kcal_100g": energy,
            "taurine_mg_kg": taur,
            "taurine_mg_kg_dm": taur_dm,
            "prebiotic": prebiotic_class(comp, add_raw),
            "named_meat_max_pct": max_named_meat_pct(comp),
            "flags": flags(comp),
            "completeness": completeness(compl_stmt),
            "completeness_source": compl_stmt,
            "notes": p.get("fetch_notes", ""),
        })

# --- scoring (branched sub-scores 0-2) --------------------------------------
def score(r):
    s = {}
    d = r["derived"]
    # 1. protein on dry matter
    if d.get("protein_dm") is None:
        s["protein"] = None
    else:
        s["protein"] = 2 if d["protein_dm"] >= 45 else (1 if d["protein_dm"] >= 35 else 0)
    # 2. carbs (NFE) on dry matter — lower is better
    if d.get("carbs_nfe_dm") is None:
        s["carbs"] = None
    else:
        s["carbs"] = 2 if d["carbs_nfe_dm"] < 15 else (1 if d["carbs_nfe_dm"] <= 25 else 0)
    # 3. fibre & prebiotics
    if r["prebiotic"].startswith("ferment"):
        s["prebiotic"] = 2
    elif r["prebiotic"].startswith("objem"):
        s["prebiotic"] = 1
    else:
        s["prebiotic"] = 0
    # 4. named meat share
    nm = r["named_meat_max_pct"]
    s["meat"] = None if nm is None else (2 if nm >= 25 else (1 if nm >= 8 else 0))
    # 5. taurine — scored on DRY MATTER against FEDIAF minima for wet food
    #    (FEDIAF 2024: 2500 mg/kg DM for wet/canned; the as-fed label figure on an
    #     ~80% moisture food is ~5x lower than its DM value, so as-fed comparison
    #     against a DM minimum would be badly misleading.)
    t = r["taurine_mg_kg_dm"]
    s["taurine"] = None if t is None else (2 if t >= 2500 else (1 if t >= 1500 else 0))
    # 6. completeness
    s["complete"] = {"kompletné": 2, "neuvedené": 1, "doplnkové": 0}[r["completeness"]]
    # 7. clean label (no added sugar / no grain)
    f = r["flags"]
    s["clean"] = 2 - int(f["sugar"]) - int(f["grain"])
    known = [v for v in s.values() if v is not None]
    max_pts = 2 * len(known)
    pct = sum(known) / max_pts if max_pts else 0
    grade = ("A" if pct >= 0.85 else "B" if pct >= 0.70 else
             "C" if pct >= 0.50 else "D" if pct >= 0.35 else "E")
    return s, round(pct * 100), grade

NONPRODUCT = re.compile(r"overview|category|přehled|prehľad|kolekcia|range page|alternate .*slug|DRY food|no longer", re.I)
for r in rows:
    sub, pct, grade = score(r)
    r["scores"] = sub
    r["score_pct"] = pct
    r["grade"] = grade
    r["is_product"] = not (NONPRODUCT.search(r["name"]) or r["fetch_status"] == "failed")

payload = {"generated": "2026-07-19", "count": len(rows), "products": rows}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)

# Inline the same payload into index.html so the page opens straight from disk.
# A fetch() of a sibling file is blocked by CORS on the file:// origin, which
# would leave the table empty for anyone who just double-clicks the HTML.
HTML = os.path.join(os.path.dirname(__file__), "index.html")
if os.path.exists(HTML):
    html = open(HTML, encoding="utf-8").read()
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")           # never break out of the <script>
    block = ('<script id="data" type="application/json">\n' + blob + '\n</script>')
    # Strip every existing data block first, then insert exactly one. Replacing
    # in place would be ambiguous: when the data is unchanged the rewritten text
    # is identical to the original, which must not be read as "no block found".
    html, removed = re.subn(r'<script id="data" type="application/json">.*?</script>\s*',
                            "", html, flags=re.S)
    anchor = "<script>\nconst SCORE_LABELS"
    if anchor not in html:
        sys.exit("index.html: anchor for the data block not found — aborting")
    open(HTML, "w", encoding="utf-8").write(
        html.replace(anchor, block + "\n" + anchor, 1))
    print(f"inlined {len(blob)//1024} KB into index.html (replaced {removed} old block(s))")

# --- console summary ---------------------------------------------------------
print(f"products: {len(rows)}")
by_grade = {}
for r in rows:
    by_grade.setdefault(r["grade"], []).append(r)
for g in "ABCDE":
    print(f"  {g}: {len(by_grade.get(g, []))}")
print("\nTOP (A/B):")
for r in sorted(rows, key=lambda x: -x["score_pct"])[:25]:
    d = r["derived"]
    print(f"  [{r['grade']} {r['score_pct']}%] {r['brand'][:18]:18} | {r['name'][:55]:55} | "
          f"P_DM {d.get('protein_dm','-'):>5} | NFE {d.get('carbs_nfe_dm','-'):>5} | "
          f"tauDM {r['taurine_mg_kg_dm'] or '-':>5} | {r['prebiotic'][:12]} | {r['completeness']}")
if UNKNOWN_COMPLETENESS:
    print(f"\n!! {len(UNKNOWN_COMPLETENESS)} completeness statement(s) missing from "
          f"curated.json — classified as 'neuvedené', please review:")
    for s in sorted(UNKNOWN_COMPLETENESS):
        print(f"   {s[:110]!r}")

missing = [r for r in rows if not r["derived"]]
print(f"\nno-analytics rows: {len(missing)}")
for r in missing:
    print("   -", r["brand"], "|", r["name"][:60])
