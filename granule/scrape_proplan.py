# -*- coding: utf-8 -*-
"""Download every Pro Plan / Pro Plan Veterinary Diets DRY cat food from the
manufacturer's CZ, SK, UK and EU sites -> raw_data/proplan_dry.json.

The listing pages' pagination is broken in the browser, but the server renders
?page=N fine, so product links are collected from the HTML of every page.
Product pages are Drupal: each section lives in a block with the class
"product-detail-item-parent--field-product-<name>". The text is kept verbatim,
with "¦" between paragraphs / list items so ingredients don't run together.

Run:  python granule/scrape_proplan.py      (stdlib only)
"""
import json, os, re, sys, time, urllib.request
from html.parser import HTMLParser
from datetime import date
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "raw_data", "proplan_dry.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catfood-research (+https://github.com/bernysk/catfood)"
BRANDS = ["brand%5B221%5D=221", "brand%5B271%5D=271", "brand%5B221%5D=221&brand%5B271%5D=271"]

MARKETS = {
    "CZ": {"host": "https://www.purina.cz", "listing": "/kocka/krmivo-pro-kocky/granule", "link": r'href="(/kocka/krmivo-pro-kocky/produkt-[^"#?]+)"',
           # the CZ "granule" listing misses some vet diets; they appear in the general listing with "granule" in the slug
           "extra_listing": "/kocka/krmivo-pro-kocky", "extra_filter": r"granul"},
    "SK": {"host": "https://www.purina.sk", "listing": "/macka/krmivo-pre-macky/granule", "link": r'href="(/macka/krmivo-pre-macky/produkt[^"#?]+)"'},
    "UK": {"host": "https://www.purina.co.uk", "listing": "/cat/cat-food/dry", "link": r'href="(/cat/cat-food/product-[^"#?]+)"'},
    "EU": {"host": "https://www.purina.eu", "listing": "/cat/cat-food/proplan-veterinary-diets", "link": r'href="(/cat/cat-food/product-[^"#?]+)"',
           "query": ["category%5B51%5D=51"]},
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "sk,cs,en"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # network error
        return 0, str(e)


def listing(m):
    found = []
    queries = m.get("query", BRANDS)
    paths = [(m["listing"], None)] + ([(m["extra_listing"], m["extra_filter"])] if m.get("extra_listing") else [])
    for path, filt in paths:
        for q in queries:
            for page in range(0, 20):
                st, html = get(f"{m['host']}{path}?{q}&page={page}")
                links = re.findall(m["link"], html)
                if filt:
                    links = [l for l in links if re.search(filt, l)]
                new = [l for l in dict.fromkeys(links) if l not in found]
                found += new
                if page > 0 and not new:
                    break
                time.sleep(0.4)
    return found


class Sections(HTMLParser):
    BLOCK = {"p", "li", "div", "br", "tr", "td", "h1", "h2", "h3", "h4", "h5", "ul", "ol", "section", "dt", "dd"}
    SKIP = {"script", "style", "button", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # (tag, section_name or None)
        self.active = []     # section names currently open
        self.buf = {}
        self.skip = 0
        self.title = ""
        self.h1 = ""
        self._in = None

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        m = re.search(r"product-detail-item-parent--field-product-([a-z_-]+)", cls)
        sec = m.group(1) if m else None
        if tag in self.SKIP:
            self.skip += 1
        if tag in ("title", "h1"):
            self._in = tag
        if tag in self.BLOCK:
            for s in self.active:
                self.buf[s] += " ¦ "
        if tag not in ("br",) and tag not in ("img", "meta", "link", "input", "source", "hr"):
            self.stack.append((tag, sec))
            if sec:
                self.active.append(sec)
                self.buf.setdefault(sec, "")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in ("title", "h1"):
            self._in = None
        while self.stack:
            t, sec = self.stack.pop()
            if sec and sec in self.active:
                self.active.remove(sec)
            if t == tag:
                break
        if tag in self.BLOCK:
            for s in self.active:
                self.buf[s] += " ¦ "

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1 += data
        if self.skip:
            return
        for s in self.active:
            self.buf[s] += data


def clean(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(\s*¦\s*)+", " ¦ ", s)
    return s.strip(" ¦")


def product(url):
    st, html = get(url)
    rec = {"url": url, "http_status": st}
    if st != 200 or not html:
        rec["fetch_status"] = "failed"
        return rec
    p = Sections()
    p.feed(html)
    rec["title"] = clean(p.title)
    rec["h1"] = clean(p.h1)
    rec["sections"] = {k: clean(v)[:4000] for k, v in p.buf.items() if clean(v)}
    body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    m = re.search(r"(Dostupné velikosti balení|Dostupné veľkosti|Available sizes?)\s*:?\s*((?:\d+(?:[.,]\d+)?\s?(?:kg|g)\s*(?:x\s*\d+\s*)?){1,8})", body, re.I)
    rec["sizes_raw"] = m.group(2).strip() if m else ""
    rec["fetch_status"] = "ok"
    return rec


def main():
    data = {"fetched_at": str(date.today()), "method": "urllib + html.parser; listing ?page=N on the server; sections = Drupal blocks product-detail-item-parent--field-product-*", "markets": {}}
    for mk, m in MARKETS.items():
        links = listing(m)
        print(f"{mk}: {len(links)} product links")
        recs = []
        for l in links:
            r = product(m["host"] + l)
            r["market"] = mk
            recs.append(r)
            print(f"   {r['http_status']} {l[-70:]}")
            time.sleep(0.5)
        data["markets"][mk] = recs
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("saved", OUT)


if __name__ == "__main__":
    main()
