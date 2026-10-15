# -*- coding: utf-8 -*-
"""Download every Royal Canin veterinary cat product listed in the SK and CZ
product sitemaps -> raw_data/royalcanin_vet.json (verbatim sections).

The vet listing on royalcanin.com is assembled by JavaScript and hides some
products (e.g. Gastrointestinal Moderate Calorie), but the product sitemap lists
them all and the product pages are server-rendered. Wet vs dry comes from the
page's own "technology" code in __NEXT_DATA__. Only dry products are used by
build_dataset.py; wet ones are kept in the raw file for completeness.

Run:  python granule/scrape_royalcanin.py      (stdlib only)
"""
import html as htmllib, json, os, re, sys, time, urllib.request
from datetime import date
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "raw_data", "royalcanin_vet.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catfood-research (+https://github.com/bernysk/catfood)"
SITEMAPS = {"SK": "https://www.royalcanin.com/sk/sk-sk/sitemap/sitemap-products.xml",
            "CZ": "https://www.royalcanin.com/cz/cs-cz/sitemap/sitemap-products.xml"}
SECTION_KEYS = {
    "composition": r"^(ZLOŽENIE|SLOŽENÍ|COMPOSITION)$",
    "additives": r"^(DOPLNKOVÉ LÁTKY|DOPLŇKOVÉ LÁTKY|ADDITIVES)$",
    "analytical": r"^(ANALYTICKÉ ZLOŽKY|ANALYTICKÉ SLOŽKY|ANALYTICAL CONSTITUENTS)$",
    "feeding": r"^(ODPORÚČANÉ DÁVKOVANIE|DOPORUČENÉ DÁVKOVÁNÍ|FEEDING INSTRUCTIONS)$",
    "details": r"^(PODROBNOSTI O PRODUKTE|PODROBNOSTI O PRODUKTU|PRODUCT DETAILS)$",
    "dvp": r"^(VYHLÁSENIE O DIETETICKOM.*|PROHLÁŠENÍ O DIETETICK.*|.*DIETETIC.*STATEMENT.*)$",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def text(fragment):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"<(br|/p|/li|/div)[^>]*>", " ¦ ", t)
    t = htmllib.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"(\s*¦\s*)+", " ¦ ", t).strip(" ¦")


def product(url):
    st, h = get(url)
    rec = {"url": url, "http_status": st}
    if st != 200:
        rec["fetch_status"] = "failed"
        return rec
    nd = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    nds = nd.group(1) if nd else ""
    m = re.search(r'"technology":\{"code":"(\w+)"', nds)
    rec["technology"] = m.group(1) if m else None
    rec["packs"] = sorted(set(re.findall(r'"base_pack_size":"([^"]+)"', nds)))
    m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    rec["h1"] = text(m.group(1)) if m else ""
    heads = list(re.finditer(r"<h3[^>]*>(.*?)</h3>", h, re.S))
    sec = {}
    for i, hm in enumerate(heads):
        title = text(hm.group(1)).upper()
        end = heads[i + 1].start() if i + 1 < len(heads) else min(len(h), hm.end() + 20000)
        body = text(h[hm.end():end])[:4000]
        for key, pat in SECTION_KEYS.items():
            if re.match(pat, title) and body and key not in sec:
                sec[key] = body
    rec["sections"] = sec
    body = text(h)
    m = re.search(r"((Kompletné|Kompletní|Doplnkové|Doplňkové|Complete|Complementary)[^.¦]{0,25}(krmivo|feed|food)[^.¦]{0,120})", body)
    rec["statement_raw"] = m.group(1).strip() if m else ""
    rec["fetch_status"] = "ok"
    return rec


def main():
    data = {"fetched_at": str(date.today()), "method": "urllib; URLs from product sitemaps; sections = text under <h3> headings; technology from __NEXT_DATA__", "markets": {}}
    for mk, sm in SITEMAPS.items():
        st, xml = get(sm)
        urls = sorted(set(u for u in re.findall(r"<loc>([^<]+)</loc>", xml) if "/cats/products/vet-products/" in u))
        print(f"{mk}: {len(urls)} vet cat products in sitemap (HTTP {st})")
        recs = []
        for u in urls:
            r = product(u)
            r["market"] = mk
            recs.append(r)
            print(f"   {r['http_status']} {r.get('technology')} {u.rsplit('/', 1)[-1]}")
            time.sleep(0.5)
        data["markets"][mk] = recs
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("saved", OUT)


if __name__ == "__main__":
    main()
