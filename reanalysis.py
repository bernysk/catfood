# -*- coding: utf-8 -*-
"""Independent re-analysis of bernysk/catfood dataset.json (v4).

Usage:  python reanalysis.py path/to/repo
Outputs: reanalysis_out.json + console report.

1. Completeness bug  - 5 Czech "Doplňkové krmivo" statements missing in curated.json
2. Label-tolerance Monte Carlo - how stable is each A-E grade?
3. Energy basis      - ME (modified Atwater), protein & P per 1000 kcal, % energy
4. Life-stage check  - FEDIAF 2025 minima (Table III-4a/b) for neutered adult,
                       active adult, growth
5. Weight robustness - leave-one-criterion-out rank correlation
"""
import json, os, re, sys, random, statistics as st, collections
sys.stdout.reconfigure(encoding="utf-8")
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
D = json.load(open(os.path.join(REPO, "dataset.json"), encoding="utf-8"))
P = [p for p in D["products"] if p["is_product"]]

# ---------------------------------------------------------------- 1. bug fix
MISSING = {s: "doplnkové" for s in [
    "Doplňkové krmivo (complementary feed)",
    "Doplňkové krmivo pro dospělé kočky (complementary feed for adult cats)",
    "Doplňkové krmivo pro dospělé kočky (complementary food for adult cats)",
    "Doplňkové krmivo pro kočky (complementary food for cats)",
    "Doplňkové krmivo pro koťata od 1 měsíce (complementary feed for kittens from 1 month)",
]}

def grade_of(pct):
    return "A" if pct >= .85 else "B" if pct >= .70 else "C" if pct >= .50 else "D" if pct >= .35 else "E"

def subscores(an, p, completeness):
    """Re-implements build_dataset.score() from analytics so we can perturb inputs."""
    s = {}
    need = ("protein", "fat", "moisture", "fiber", "ash")
    if all(k in an for k in need):
        dm = 100 - an["moisture"]
        # same rounding as build_dataset.py (thresholds are applied to rounded values)
        pdm = round(an["protein"] / dm * 100, 1)
        nfe = round(max(100 - sum(an[k] for k in need), 0) / dm * 100, 1)
        s["protein"] = 2 if pdm >= 45 else 1 if pdm >= 35 else 0
        s["carbs"] = 2 if nfe < 15 else 1 if nfe <= 25 else 0
        t = p["taurine_mg_kg"]
        tdm = None if t is None else round(t / (round(dm, 1) / 100))
        s["taurine"] = None if t is None else (2 if tdm >= 2500 else 1 if tdm >= 1500 else 0)
    else:
        s["protein"] = s["carbs"] = None
        s["taurine"] = p["scores"]["taurine"]
    s["prebiotic"] = p["scores"]["prebiotic"]
    s["meat"] = p["scores"]["meat"]
    s["complete"] = {"kompletné": 2, "neuvedené": 1, "doplnkové": 0}[completeness]
    s["clean"] = p["scores"]["clean"]
    return s

def pct_of(s, drop=None):
    k = [v for key, v in s.items() if v is not None and key != drop]
    return sum(k) / (2 * len(k)) if k else 0

fixed = []
for p in P:
    comp = MISSING.get(p["completeness_source"].strip(), p["completeness"])
    s = subscores(p["analytics"], p, comp)
    pct = pct_of(s)
    assert comp != p["completeness"] or round(pct * 100) == p["score_pct"], p["name"]
    fixed.append((p, comp, s, pct))

print("=== 1. completeness fix ===")
for p, comp, s, pct in fixed:
    if comp != p["completeness"]:
        print(f"  {p['brand']:10} {p['name'][:46]:46} {p['grade']} {p['score_pct']:3} -> "
              f"{grade_of(pct)} {round(pct*100):3}")
cnt = collections.Counter(grade_of(f[3]) for f in fixed)
print("  grades after fix:", dict(sorted(cnt.items())))
print("  completeness after fix:", dict(collections.Counter(f[1] for f in fixed)))
br = collections.defaultdict(list)
for p, comp, s, pct in fixed:
    br[p["brand"]].append(round(pct * 100))
print("  brand means after fix:", {b: round(st.mean(v), 1) for b, v in br.items() if b in ("Ontario", "Brit Care")})

# ---------------------------------------------------------- 2. Monte Carlo
# Scenario "typical": batch/rounding noise. Scenario "legal": EU 767/2009 Annex IV
# tolerances for non-food-producing animals (protein <16 %: ±2 units; fat <16 %:
# -2/+4; fibre ±1.75; ash -2/+1); moisture kept at ±1 unit.
SCEN = {
    "typical": dict(protein=(-.5, .5), fat=(-.5, .5), fiber=(-.2, .2), ash=(-.3, .3), moisture=(-1, 1)),
    "legal":   dict(protein=(-2, 2), fat=(-2, 4), fiber=(-1.75, 1.75), ash=(-2, 1), moisture=(-1, 1)),
}
random.seed(42)
N = 2000
print("\n=== 2. grade stability under label tolerance (share of draws keeping the published grade) ===")
mc = {}
for name, tol in SCEN.items():
    stab = []
    for p, comp, s0, pct0 in fixed:
        an = p["analytics"]
        if not all(k in an for k in ("protein", "fat", "moisture", "fiber", "ash")):
            continue
        g0 = grade_of(pct0); same = 0
        for _ in range(N):
            a = {k: max(0.0, an[k] + random.uniform(*tol[k])) for k in tol}
            same += grade_of(pct_of(subscores(a, p, comp))) == g0
        stab.append((same / N, p))
    mc[name] = stab
    v = [x[0] for x in stab]
    print(f"  {name:8}: median {st.median(v):.0%}, products with <80% stability: "
          f"{sum(x < .8 for x in v)}/{len(v)}, <60%: {sum(x < .6 for x in v)}")

# ------------------------------------------------- 3. energy-based nutrients
def num(x): return float(x.replace(",", "."))
def mineral(raw, words):
    m = re.search(r"(?:" + words + r")\w*\s*[:=]?\s*(\d+[.,]?\d*)\s*%", raw or "", re.I)
    return num(m.group(1)) if m else None

rows = []
for p, comp, s, pct in fixed:
    an = p["analytics"]
    if not all(k in an for k in ("protein", "fat", "moisture", "fiber", "ash")):
        continue
    nfe = max(100 - sum(an[k] for k in ("protein", "fat", "moisture", "fiber", "ash")), 0)
    me_atw = 3.5 * an["protein"] + 8.5 * an["fat"] + 3.5 * nfe          # kcal/100 g, modified Atwater
    me_decl = p["energy_kcal_100g"]
    me = me_decl or me_atw
    raw = p["analytics_raw"]
    phos = mineral(raw, r"fosfor|phosph")
    ca = mineral(raw, r"v[áa]pn|calcium")
    dm = 100 - an["moisture"]
    rows.append(dict(
        brand=p["brand"], name=p["name"], grade_fixed=grade_of(pct), lifestage=p["lifestage"],
        complete=comp, unreliable=p["derived"].get("dm_unreliable"),
        me_kcal100=round(me, 1), me_source="declared" if me_decl else "atwater",
        me_atwater=round(me_atw, 1),
        protein_dm=round(an["protein"] / dm * 100, 1),
        protein_g_per_1000kcal=round(an["protein"] * 10 / me * 100, 1),
        protein_pct_energy=round(3.5 * an["protein"] / me_atw * 100, 1),
        fat_pct_energy=round(8.5 * an["fat"] / me_atw * 100, 1),
        carb_pct_energy=round(3.5 * nfe / me_atw * 100, 1),
        taurine_mg_per_1000kcal=None if p["taurine_mg_kg"] is None else round(p["taurine_mg_kg"] / 10 / me * 1000),
        P_g_per_1000kcal=None if phos is None else round(phos * 10 / me * 100, 2),
        Ca_P=None if (phos is None or ca is None) else round(ca / phos, 2),
    ))

print("\n=== 3. energy basis ===")
both = [r for r in rows if r["me_source"] == "declared"]
diff = [r["me_atwater"] / r["me_kcal100"] - 1 for r in both]
print(f"  declared ME available: {len(both)}/{len(rows)}; Atwater vs declared median diff {st.median(diff):+.0%}")
for k in ("protein_g_per_1000kcal", "protein_pct_energy", "fat_pct_energy", "carb_pct_energy"):
    v = [r[k] for r in rows if not r["unreliable"]]
    print(f"  {k:24} median {st.median(v):6.1f}  range {min(v):.1f}–{max(v):.1f}  (DM-reliable rows only)")
pr = [r for r in rows if r["P_g_per_1000kcal"] is not None]
print(f"  phosphorus declared: {len(pr)} rows; P g/1000 kcal range "
      f"{min(r['P_g_per_1000kcal'] for r in pr)}–{max(r['P_g_per_1000kcal'] for r in pr)}; "
      f"Ca:P range {min(r['Ca_P'] for r in pr)}–{max(r['Ca_P'] for r in pr)}")
for b in sorted({r["brand"] for r in pr}):
    v = [r for r in pr if r["brand"] == b]
    print(f"     {b:16} n={len(v):2} P {st.median([r['P_g_per_1000kcal'] for r in v]):.2f} g/1000kcal, "
          f"Ca:P {st.median([r['Ca_P'] for r in v]):.2f}, protein {st.median([r['protein_g_per_1000kcal'] for r in v]):.0f} g/1000kcal")

# -------------------------------------------------- 4. FEDIAF life-stage check
# FEDIAF 2025 Table III-4b (per 1000 kcal ME): protein 83.3 (adult, MER 75 = neutered/indoor),
# 62.5 (adult, MER 100), 70/75 (growth/reproduction). Taurine canned: 670 / 500 / 630 mg.
MIN = {"neutered adult": (83.3, 670), "active adult": (62.5, 500), "growth": (75.0, 630)}
print("\n=== 4. FEDIAF 2025 minima, complete/unstated foods, DM-reliable rows ===")
pool = [r for r in rows if r["complete"] != "doplnkové" and not r["unreliable"]]
for stage, (pmin, tmin) in MIN.items():
    lowp = [r for r in pool if r["protein_g_per_1000kcal"] < pmin]
    tt = [r for r in pool if r["taurine_mg_per_1000kcal"] is not None]
    lowt = [r for r in tt if r["taurine_mg_per_1000kcal"] < tmin]
    print(f"  {stage:15} protein<{pmin}: {len(lowp)}/{len(pool)}   taurine<{tmin} mg: {len(lowt)}/{len(tt)}")
    for r in lowp + lowt:
        print(f"       - {r['brand']:14} {r['name'][:50]:50} prot {r['protein_g_per_1000kcal']} tau {r['taurine_mg_per_1000kcal']}")
dm_t = [(p, p["taurine_mg_kg_dm"]) for p in P if p["taurine_mg_kg_dm"]]
print(f"  framework gives taurine 2/2 at >=2500 mg/kg DM; FEDIAF canned min for neutered adult = 2700. "
      f"Products in 2500–2699 band: {sum(2500 <= t < 2700 for _, t in dm_t)}")

# ---------------------------------------------- 5. weighting robustness
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for k, i in enumerate(o): r[i] = k
    return r
def spearman(a, b):
    ra, rb = rank(a), rank(b); n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))
base = [f[3] for f in fixed]
print("\n=== 5. leave-one-criterion-out ===")
for crit in ("protein", "carbs", "prebiotic", "meat", "taurine", "complete", "clean"):
    alt = [pct_of(f[2], drop=crit) for f in fixed]
    moved = sum(grade_of(a) != grade_of(b) for a, b in zip(alt, base))
    print(f"  drop {crit:9}: Spearman {spearman(base, alt):.3f}, grade changes {moved}/{len(base)}")

json.dump({"energy_rows": rows,
           "mc_stability": {k: [{"brand": p["brand"], "name": p["name"], "stable": round(s, 3)} for s, p in v]
                            for k, v in mc.items()}},
          open("reanalysis_out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
