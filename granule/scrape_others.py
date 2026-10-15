# -*- coding: utf-8 -*-
"""Download dry veterinary cat diets of Brit (brit.pet/sk), Farmina Vet Life
(farmina.com/cz), Virbac Veterinary HPM (sk.virbac.com) and Trovet (trovet.com,
English page; the manufacturer has no SK/CZ site) -> raw_data/others_vet.json
(verbatim text cut into sections).

Both sites are server-rendered. Brit: product list = the "VD granule pre mačky"
collection page. Farmina: the Vet Life feline list is built by JavaScript, so the
product URLs below were read from that page in a browser on 2026-10-15; wet foods
and treats are dropped (URL contains "wet"/"treat", or only pack sizes < 400 g).
Hill's and Calibra block scripts / serve an empty page to them and are collected
in a browser instead (raw_data/hills_vet.json, raw_data/calibra_vet.json).

Run:  python granule/scrape_others.py      (stdlib only)
"""
import html as htmllib, json, os, re, sys, time, urllib.request
from datetime import date
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "raw_data", "others_vet.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catfood-research (+https://github.com/bernysk/catfood)"
FARMINA = "https://www.farmina.com/cz/eshop/krmivo-pro-va%C5%A1i-ko%C4%8Dku/farmina-vet-life-feline/"
FARMINA_IDS = ["79-gastrointestinal-feline", "90-hepatic-feline", "80-struvite-feline", "81-struvite-management-feline",
               "82-renal-feline", "89-cardiac-feline", "83-obesity-feline", "84-diabetic-feline", "85-ultrahypo-feline",
               "967-hypoallergenic-pork-&-potato-feline", "86-neutered-male-feline", "87-neutered-female-feline",
               "88-hairball-feline", "1035-struvite-management-feline"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def text(h):
    t = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", h, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)          # every tag boundary becomes a space
    return re.sub(r"\s+", " ", htmllib.unescape(t)).strip()


def cut(t, start, stop, n=4000):
    m = re.search(start, t)
    if not m:
        return ""
    rest = t[m.end():m.end() + n]
    s = re.search(stop, rest) if stop else None
    return (rest[:s.start()] if s else rest).strip(" :")


def brit():
    st, h = get("https://brit.pet/sk/kolekcie/vd-granule-pra-macky")
    urls = sorted(set("https://brit.pet" + u for u in re.findall(r'href="(/sk/produkty/[^"?#]+)"', h)))
    out = []
    for u in urls:
        st, h = get(u)
        r = {"brand": "Brit", "market": "SK", "url": u, "http_status": st}
        if st != 200:
            r["fetch_status"] = "failed"; out.append(r); continue
        t = text(h)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        name = text(m.group(1)) if m else ""
        r.update({
            "name": name,
            "statement_raw": cut(t, re.escape("Go to slide 1 " + name), r"(Veterinárne|Bez obilnín|Dospelá mačka|Veľkosť)", 400),
            "sizes": re.findall(r"\d+(?:[.,]\d+)?\s?k?g\b", cut(t, r"Veľkosť:", r"[A-ZŽŠČ][a-zžščťďňľáéíóúý]{3}", 80)),
            "composition_raw": cut(t, r"(?:Späť |Výživové údaje )Zloženie", r"(Výživové doplnkové látky|Doplnkové látky|Analytické zložky)"),
            "additives_raw": cut(t, r"(Výživové doplnkové látky na 1 kg|Doplnkové látky na 1 kg|Výživové doplnkové látky)", r"Analytické zložky"),
            "analytical_raw": cut(t, r"Analytické zložky", r"(Pokyny na kŕmenie|Koľko krmiva|Tabuľka krmív)", 1200),
            "period_raw": cut(t, r"Pokyny pre kŕmenie", r"(Dennú dávku|Tabuľka|Recenzie|Hmotnosť mačky|Doručenie)", 900),
            "fetch_status": "ok"})
        out.append(r)
        print("  Brit", st, u.rsplit("/", 1)[-1])
        time.sleep(0.5)
    return out


def farmina():
    out = []
    for pid in FARMINA_IDS:
        u = FARMINA + pid + ".html"
        st, h = get(u)
        r = {"brand": "Farmina", "market": "CZ", "url": u, "http_status": st}
        if st != 200:
            r["fetch_status"] = "failed"; out.append(r); continue
        t = text(h)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        sizes = re.findall(r"\d+(?:[.,]\d+)?\s?k?g\b", cut(t, r"dostupné ve velikostech", r"[a-zěščřžýáíéů]{4}", 80))
        grams = [float(re.sub(r"[^\d.,]", "", s).replace(",", ".")) * (1000 if "kg" in s else 1) for s in sizes]
        r.update({
            "name": "Vet Life " + (text(m.group(1)) if m else pid),
            "statement_raw": cut(t, r"Farmina Vet Life [^.]{0,40}? je ", r"\.", 300),
            "period_raw": cut(t, r"Doporučená doba užívání", r"\.", 200),
            "sizes": sizes,
            "composition_raw": cut(t, r"\bsložení\b", r"(přísady a výživa aditiva|Doplňkové látky na|composizione2)"),
            "additives_raw": cut(t, r"Doplňkové látky na 1 ?kg", r"analytické složky"),
            "analytical_raw": cut(t, r"analytické složky", r"(Dávkovací tabulka|Stáhnout|Prohlášení)", 900),
            "is_dry": bool(grams) and max(grams) >= 400,
            "fetch_status": "ok"})
        out.append(r)
        print("  Farmina", st, pid, sizes)
        time.sleep(0.5)
    return out


VIRBAC = "https://sk.virbac.com"
TROVET_LISTS = ["https://www.trovet.com/dietaryfoodforcats/", "https://www.trovet.com/hypoallergenicdietsforcats/"]


def cells(h):
    """Page text with every tag boundary turned into ' | ' (Virbac tables have no % signs)."""
    t = re.sub(r"<(script|style|svg)[^>]*>.*?</>", " ", h, flags=re.S)
    t = htmllib.unescape(re.sub(r"<[^>]+>", " | ", t))
    t = re.sub(r"(\s*\|\s*)+", " | ", t)
    return re.sub(r"\s+", " ", t)


def virbac():
    st, h = get(VIRBAC + "/macky/granule-pre-macky")
    urls = sorted(set(VIRBAC + u for u in re.findall(r'href="(/produkty/[^"?#]+)"', h) if "wet-food" not in u and "kapsick" not in u))
    out = []
    for u in urls:
        st, h = get(u)
        r = {"brand": "Virbac", "market": "SK", "url": u, "http_status": st}
        if st != 200:
            r["fetch_status"] = "failed"; out.append(r); continue
        t = cells(h)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        ana_at = t.find("| Analytické zložky |")
        comp_at = t.rfind("| Zloženie |", 0, ana_at if ana_at > 0 else None)
        r.update({
            "name": text(m.group(1)) if m else u.rsplit("/", 1)[-1],
            "purpose_raw": cut(t[t.rfind("Podrobnosti o produkte |", 0, comp_at):], r"Podrobnosti o produkte \|", r"\| (Výhody|Dávkovanie) \|", 1500),
            "sizes": list(dict.fromkeys(re.findall(r'btn__qty-label">\s*([^<]+?)\s*<', h))),
            "composition_raw": cut(t[comp_at:], r"\| Zloženie \|", r"\| (VETERINARY HPM® neobsahuje|Hlavné zložky|Analytické zložky)", 3000) if comp_at >= 0 else "",
            "analytical_cells": cut(t[ana_at:], r"\| Analytické zložky \|", r"\| Pridané vitamíny", 1500) if ana_at >= 0 else "",
            "additives_cells": cut(t[ana_at:], r"\| Pridané vitamíny \|", r"\| Pridané funkčné zložky", 3000) if ana_at >= 0 else "",
            "energy_cells": cut(t[ana_at:], r"\| Pridané funkčné zložky \|", r"\| FAQ", 800) if ana_at >= 0 else "",
            "fetch_status": "ok"})
        out.append(r)
        print("  Virbac", st, u.rsplit("/", 1)[-1][:60])
        time.sleep(0.5)
    return out


def trovet():
    urls = []
    for lst in TROVET_LISTS:
        st, h = get(lst)
        urls += re.findall(r'href="(https://www\.trovet\.com/(?:en/)?product/[^"#?]+-cat/)"', h)
    out = []
    for u in sorted(set(urls)):
        st, h = get(u)
        r = {"brand": "Trovet", "market": "EN", "url": u, "http_status": st}
        if st != 200:
            r["fetch_status"] = "failed"; out.append(r); continue
        m = re.search(r'id="productvorm-Dry"(.*?)(?=id="productvorm-|<footer|\Z)', h, re.S)
        if not m:
            r["fetch_status"] = "no dry form"; out.append(r)
            print("  Trovet (no dry)", u); continue
        box = m.group(1)
        ing = re.search(r"<h3>Ingredients[^<]*</h3>.*?<p>(.*?)</p>", box, re.S)
        pairs = re.findall(r'samenstelling-element">([^<]+)</span><span class="samenstelling-hoeveelheid">([^<]+)<', box)
        en = re.search(r'titel-energie">[^<]*</span>([^<]+)', box)
        adv = re.search(r'id="afwijkende-gebruikers-advies-Dry"[^>]*>(.*?)</div>', h, re.S)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        sub = re.search(r"<h2[^>]*>(.*?)</h2>", h, re.S)
        r.update({
            "name": "Trovet " + (text(h1.group(1)) if h1 else u.rstrip("/").rsplit("/", 1)[-1]),
            "statement_raw": text(sub.group(1)) if sub else "",
            "composition_raw": text(ing.group(1)) if ing else "",
            "analytical_raw": ", ".join(f"{a.strip()} {b.strip()}" for a, b in pairs) + (" ¦ Energy: " + en.group(1).strip() if en else ""),
            "period_raw": text(adv.group(1)) if adv else "",
            "fetch_status": "ok"})
        out.append(r)
        print("  Trovet", st, u.rstrip("/").rsplit("/", 1)[-1])
        time.sleep(0.5)
    return out


def main():
    data = {"fetched_at": str(date.today()), "method": "urllib; text = HTML with tags replaced by spaces; sections cut at the label headings", "products": brit() + farmina() + virbac() + trovet()}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("saved", OUT, len(data["products"]))


if __name__ == "__main__":
    main()
