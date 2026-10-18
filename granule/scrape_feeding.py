# -*- coding: utf-8 -*-
"""Feeding tables -> daily grams for a 4 kg adult cat -> raw_data/feeding_scripted.json.

Brit, Virbac and Trovet pages are re-read (server-rendered); Pro Plan tables come
from the feeding-guide text already stored in raw_data/proplan_dry.json. Hill's,
Calibra and Eminent were read in the built-in browser (raw_data/feeding_browser.json).
Royal Canin shows no table on the page ("uvedené v tabuľke" = on the bag) and
Farmina only offers it as a download — both are reported, not guessed.

Rule: the 4 kg row of the dry-only column; where a table has several columns the
maintenance / normal-weight column is used and named in 'column'. Kitten and
growth tables are skipped.

Run:  python granule/scrape_feeding.py      (stdlib only)
"""
import html as htmllib, json, os, re, sys, time, urllib.request
from datetime import date
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "raw_data", "feeding_scripted.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catfood-research (+https://github.com/bernysk/catfood)"


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return ""


def cells(h):
    t = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", h, flags=re.S)
    t = htmllib.unescape(re.sub(r"<[^>]+>", " | ", t))
    t = re.sub(r"(\s*\|\s*)+", " | ", t)
    return re.sub(r"\s+", " ", t)


def num(s):
    return float(s.replace(",", "."))


def brit(url):
    t = cells(get(url))
    m = re.search(r"Hmotnosť mačky \(kg\) \| Denná dávka \(g/deň\)((?: \| \d+(?:[.,]\d+)?){4,40})", t)
    if not m:
        return None
    nums = [num(x) for x in re.findall(r"\d+(?:[.,]\d+)?", m.group(1))]
    pairs = dict(zip(nums[0::2], nums[1::2]))
    return {"table_raw": m.group(0), "g_day_4kg": pairs.get(4.0), "column": "denná dávka"}


def virbac(url):
    t = cells(get(url))
    m = re.search(r"\| Dávkovanie \|(.*?)\| (?:Denná kŕmna dávka|Zloženie)", t)
    if not m:
        return None
    raw = m.group(0)
    toks = [x.strip() for x in m.group(1).split("|") if x.strip()]
    heads = [x for x in toks if not re.fullmatch(r"\d+(?:[.,]\d+)?", x)]
    # value columns are the header cells after "Tělesná/Telesná hmotnosť (kg)" and "Denná dávka (g/deň)"
    cols = [h for h in heads if not re.search(r"^T[eě]l[eě]sn[áa] hmotnos|^Denná dávka|^V pr[íi]pad", h, re.I)
            and not h.startswith("(")]          # "(pozvolné snižování hmotnosti)" is a note under "Nadváha"
    nums = [x for x in toks if re.fullmatch(r"\d+(?:[.,]\d+)?", x)]
    ncol = max(1, len(cols))
    rows = [nums[i:i + ncol + 1] for i in range(0, len(nums), ncol + 1)]
    want = next((i for i, c in enumerate(cols) if re.search(r"Normáln|Udržiavan", c, re.I)), None)
    if want is None:                             # W1: only weight-loss columns, no maintenance amount
        return {"table_raw": raw, "g_day_4kg": None, "column": "len redukčné dávky (" + ", ".join(cols) + ")"}
    for r in rows:
        if len(r) == ncol + 1 and num(r[0]) == 4:
            return {"table_raw": raw, "g_day_4kg": num(r[1 + want]),
                    "column": cols[want] if cols else "denná dávka"}
    return {"table_raw": raw, "g_day_4kg": None, "column": None}


def trovet(url):
    h = get(url)
    m = re.search(r'id="productvorm-Dry"(.*?)(?=id="productvorm-|<footer|\Z)', h, re.S)
    if not m:
        return None
    tb = re.search(r'<table class="voedingsadvies-tabel">(.*?)</table>', m.group(1), re.S)
    if not tb:
        return None
    rows = [[htmllib.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tb.group(1), re.S)]
    raw = " ¦ ".join(" | ".join(r) for r in rows)
    w, g = rows[0][1:], rows[1][1:]
    pairs = {num(a): num(b) for a, b in zip(w, g) if re.fullmatch(r"\d+(?:[.,]\d+)?", a) and re.fullmatch(r"\d+(?:[.,]\d+)?", b)}
    return {"table_raw": raw, "g_day_4kg": pairs.get(4.0), "column": rows[1][0]}


def proplan_row(text):
    """4 kg grams from a Pro Plan feeding-guide text (CZ/SK/UK layouts).

    Tables are flattened to "header ¦ header ¦ 4 ¦ 35 ¦ 45 ¦ 6 ¦ ...": the values
    of a row are the numbers after the weight until the next weight (<= 12).
    With several columns the maintenance one wins (Udržení/maintenance), else the
    first (dry-only before "dry + wet")."""
    toks = [x.strip() for x in text.split("¦")]
    isnum = lambda x: re.fullmatch(r"\d+(?:[.,]\d+)?\s*(?:g|kg)?", x) is not None
    val = lambda x: num(re.sub(r"\s*(?:g|kg)$", "", x))
    for k, t in enumerate(toks):
        if isnum(t) and val(t) == 4 and k + 1 < len(toks) and isnum(toks[k + 1]) and val(toks[k + 1]) > 12:
            vals = []
            for x in toks[k + 1:]:
                if not isnum(x) or val(x) <= 12:
                    break
                vals.append(val(x))
            first = next(i for i, x in enumerate(toks) if isnum(x) and val(x) <= 12 and i + 1 < len(toks) and isnum(toks[i + 1]))
            heads = [h for h in toks[:first] if h and not isnum(h)][-len(vals):] if len(vals) > 1 else []
            pick = next((i for i, h in enumerate(heads) if re.search(r"udr[žz]|mainten", h, re.I)), 0)
            col = heads[pick] if heads else "4 kg, granule"
            if not heads and re.search(r"weight loss|snižov|úbyt", text[:400], re.I):
                col = "4 kg — tabuľka na chudnutie"
            return vals[pick], col
    m = re.search(r"2\s*-\s*4\s*¦\s*\d+\s*-\s*(\d+)", text)            # "2-4 ¦ 30-55"
    if m:
        return num(m.group(1)), "rozsah 2–4 kg, horná hodnota"
    a = re.search(r"Cat Weight: 3kg, Total daily amount[^:]*: (\d+)g", text)
    b = re.search(r"Cat Weight: 5kg, Total daily amount[^:]*: (\d+)g", text)
    if a and b:
        return (num(a.group(1)) + num(b.group(1))) / 2, "priemer 3 kg a 5 kg (4 kg na stránke nie je)"
    return None, None


def proplan():
    d = json.load(open(os.path.join(HERE, "raw_data", "proplan_dry.json"), encoding="utf-8"))
    out = {}
    for mk, recs in d["markets"].items():
        for r in recs:
            if r.get("fetch_status") != "ok":
                continue
            fg = r.get("sections", {}).get("feeding-guide", "")
            if re.search(r"kot[ěe]|ma[čc]iat|kitten", r.get("h1", "") + r["url"], re.I):
                continue
            g, how = proplan_row(fg)
            out[r["url"]] = {"table_raw": fg[:1500], "g_day_4kg": g, "column": how}
    return out


def main():
    others = json.load(open(os.path.join(HERE, "raw_data", "others_vet.json"), encoding="utf-8"))
    curated = json.load(open(os.path.join(HERE, "raw_data", "gi_dry.json"), encoding="utf-8"))
    urls = [(p["brand"], p["url"]) for p in others["products"] if p.get("fetch_status") == "ok" and p["brand"] in ("Brit", "Virbac", "Trovet")]
    urls += [(p["brand"], p["url"]) for p in curated["products"] if p["brand"] == "Brit"]
    res = proplan()
    for brand, u in dict.fromkeys(urls):
        r = {"Brit": brit, "Virbac": virbac, "Trovet": trovet}[brand](u)
        res[u] = r or {"table_raw": "", "g_day_4kg": None, "column": "tabuľka sa nenašla"}
        print(brand, res[u]["g_day_4kg"], u.rsplit("/", 2)[-2:])
        time.sleep(2.0)                        # sk.virbac.com answers HTTP 429 to faster requests
    data = {"fetched_at": str(date.today()),
            "not_available": {"Royal Canin": "stránka uvádza len „ODPORÚČANÉ DÁVKOVANIE: uvedené v tabuľke“ (tabuľka je na obale)",
                              "Farmina": "kŕmna tabuľka je na stránke len ako súbor na stiahnutie („Dávkovací tabulka – Stáhnout“)"},
            "products": res}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print("saved", OUT, len(res), "with value:", sum(1 for v in res.values() if v["g_day_4kg"]))


if __name__ == "__main__":
    main()
