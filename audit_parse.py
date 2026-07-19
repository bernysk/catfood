# -*- coding: utf-8 -*-
"""Independent cross-check of build_dataset.py's parsing.

Deliberately uses a *different* strategy than the main parser: split the raw
analytics string on separators and read each fragment on its own, instead of
searching the whole string with one regex per nutrient. Where the two methods
disagree, the row needs a human look.
"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

d = json.load(open("dataset.json", encoding="utf-8"))
P = [p for p in d["products"] if p["is_product"]]

KEYS = {
    "protein":  ("protein", "bílkov", "bielkov", "dusíkat", "rohprotein"),
    "fat":      ("tuk", "fat", "fett", "oleje a tuky"),
    "fiber":    ("vlákn", "fib", "rohfaser"),
    "ash":      ("popel", "popol", "ash", "anorganic", "rohasche", "inorganic"),
    "moisture": ("vlhkos", "moisture", "feuchte"),
}
SKIP = ("omega", "vápn", "vapn", "fosfor", "sod", "draslík", "hořč", "horč",
        "chlorid", "síra", "sira", "calcium", "phosph", "sodium", "potassium",
        "magnes", "dha", "kalor", "kcal", "škrob", "cukr", "sugar", "starch")

issues, checked = [], 0
for p in P:
    raw = p.get("analytics_raw") or ""
    if not raw:
        continue
    checked += 1
    # Czech/Slovak labels use the comma as a DECIMAL separator as well as a list
    # separator, so normalise decimals to dots before splitting on commas.
    norm = re.sub(r"(?<=\d),(?=\d)", ".", raw)
    # independent read: fragment-by-fragment
    indep = {}
    for frag in re.split(r"[,;•\n]|\s\|\s", norm):
        f = frag.strip().lower()
        if not f or any(s in f for s in SKIP):
            continue
        m = re.search(r"(\d+[.,]?\d*)\s*%?", f)
        if not m:
            continue
        v = float(m.group(1).replace(",", "."))
        for key, words in KEYS.items():
            if any(w in f for w in words) and key not in indep:
                indep[key] = v
                break
    got = p["analytics"]
    for key in KEYS:
        a, b = got.get(key), indep.get(key)
        if a is None and b is None:
            continue
        if a is None:
            issues.append((p, key, "parser MISSED", b, raw))
        elif b is None:
            pass  # fragment method is the weaker one; not evidence of a bug
        elif abs(a - b) > 0.001:
            issues.append((p, key, "DISAGREE", f"main={a} indep={b}", raw))

print(f"rows with analytics checked: {checked}")
print(f"disagreements / misses: {len(issues)}\n")
for p, key, kind, v, raw in issues:
    print(f"[{kind}] {key:9} {p['brand']:14} | {p['name'][:44]}")
    print(f"           value={v}")
    print(f"           raw: {raw[:130]}\n")

# sanity: every parsed number must literally occur in the raw text
print("--- literal-presence check ---")
bad = 0
for p in P:
    raw = (p.get("analytics_raw") or "").replace(",", ".")
    for key, v in (p["analytics"] or {}).items():
        s1, s2 = f"{v:g}", f"{v:.1f}"
        if s1 not in raw and s2 not in raw:
            bad += 1
            print(f"  {key}={v} not literally in raw | {p['brand']} {p['name'][:40]}")
print(f"values not found literally in source text: {bad}")
