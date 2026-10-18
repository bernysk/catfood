# -*- coding: utf-8 -*-
"""Omega-3 / EPA+DHA and vitamin D3 read from the verbatim label text.

Shared by granule/build_dataset.py and mokre-krmivo/build_dataset.py.

Vitamin D3 legal maximum: Commission Implementing Regulation (EU) 2017/1492,
entry 3a671 cholecalciferol, "Other species" (cats included): 2 000 IU per kg of
complete feedingstuff with a moisture content of 12 %. The limit is on the total
content; most labels declare only the *added* amount (nutritional additives), so
an added figure is a lower bound of the total. A value listed among the
analytical constituents or marked "celkový obsah" is treated as total.
"""
import re

EU_D3_MAX_12 = 2000.0          # IU/kg at 12 % moisture
N = r"(\d+(?:[.,]\d+)?)"


def _num(s):
    return float(s.replace(" ", "").replace(",", "."))


def omega3_pct(text):
    """Omega-3 fatty acids, % as fed (None if not declared)."""
    m = re.search(r"omega[\s-]?3\s*%?[^\d%¦|]{0,32}?" + N + r"\s*%", text or "", re.I)
    return _num(m.group(1)) if m else None


def epa_dha_pct(text):
    """(EPA+DHA % as fed, how it was declared) — combined figure, or EPA and DHA summed."""
    t = text or ""
    m = re.search(r"EPA\s*(?:\+|/|a|and|&)\s*DHA[^\d%¦|]{0,15}?" + N + r"\s*%", t, re.I)
    if m:
        return _num(m.group(1)), "EPA+DHA"
    e = re.search(r"\bEPA\b[^\d%¦|]{0,6}" + N + r"\s*%", t)
    d = re.search(r"\bDHA\b[^\d%¦|]{0,6}" + N + r"\s*%", t)
    if e and d:
        return round(_num(e.group(1)) + _num(d.group(1)), 3), "EPA + DHA (súčet)"
    if d:
        return None, f"len DHA {d.group(1)} %"
    return None, None


D3 = (r"vit(?:am[íi]n|\.)?\s*D\s*3?\s*(?:\([^)]{1,20}\))?\s*:?\s*"
      r"(\d{1,3}(?:[  ,]\d{3})+(?!\d)|\d+)(?:[.,]\d+)?\s*(?:IU|I\.\s?U\.|m\.\s?j\.|MJ|UI)?")


def vitamin_d3(analytical, additives, typical=""):
    """(IU/kg as fed, 'celkový'|'pridaný') — analytical/total value preferred."""
    for text, kind in ((analytical, "celkový"), (additives, "pridaný"), (typical, "celkový")):
        for m in re.finditer(D3, text or "", re.I):
            ctx = m.group(0)
            g = m.group(1)
            v = float(re.sub(r"[  ,]", "", g)) if re.fullmatch(r"\d{1,3}(?:[  ,]\d{3})+", g) else _num(g)   # "1 700", UK "1,000"
            if v < 50:                      # e.g. "vitamín D3 (3a671)" with no amount
                continue
            k = "celkový" if re.search(r"celkov", ctx, re.I) else kind
            return v, k
    return None, None


def d3_at_12(iu_kg, moisture):
    """Convert IU/kg as fed to the regulation's 12 % moisture basis."""
    if iu_kg is None or moisture is None or moisture >= 100:
        return None
    return round(iu_kg * 88.0 / (100.0 - moisture))
