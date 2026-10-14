# Export pre NotebookLM

NotebookLM neprijíma súbory `.json`, preto sú tu tie isté dáta ako `.txt`.
**Súbory sa generujú automaticky** pri každom `python build_dataset.py` — ručne ich neupravujte,
zmeny by sa pri ďalšom builde prepísali.

| Súbor | Obsah |
|---|---|
| `bozita.txt` … `shelma.txt` | doslovné kópie [`raw_data/*.json`](../raw_data/) — text etikiet zo stránok výrobcov, vrátane `fetch_notes` |
| `dataset_skore.txt` | kópia [`dataset.json`](../dataset.json) — prepočty na sušinu, čiastkové skóre, známky |

## Ako to používať

- **Dobré otázky:** „Ktoré produkty obsahujú psyllium?", „Čo uvádza Sheba CZ ako zloženie?",
  „Ktoré etikety sa líšia medzi SK a CZ verziou?" — vyhľadávanie a porovnávanie textu.
- **Nepoužívať na výpočty ani hodnotenie.** Prepočty a skóre robí `build_dataset.py`;
  NotebookLM pri číslach chybuje (pozri [`KontrolaLM.md`](../KontrolaLM.md)).
- Ku každej odpovedi si v NotebookLM otvorte citáciu a overte ju v pôvodnom texte.
- Odbornú literatúru (PDF) nahrajte zvlášť z [`literatura/`](../literatura/).
