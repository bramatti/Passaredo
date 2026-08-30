#!/usr/bin/env python3
"""Gera model/l18n/labels_pt-BR.json a partir da taxonomia do eBird (locale=pt_BR),
usando os nomes cientificos do BirdNET (labels_en.json) como lista mestra.

Uso:
    EBIRD_API_KEY=sua_chave python3 build_pt_br_labels.py

Roda a partir do diretorio raiz do BirdNET-Pi (onde existe model/l18n/).
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

EBIRD_KEY = os.environ.get("EBIRD_API_KEY", "")
if not EBIRD_KEY:
    print("error: defina EBIRD_API_KEY no ambiente", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.ebird.org/v2/ref/taxonomy/ebird"

def fetch_taxonomy(locale):
    """Baixa a taxonomia completa do eBird para um locale e retorna
    dict sci_name -> common_name."""
    url = BASE + "?fmt=json&locale=" + locale
    req = urllib.request.Request(url, headers={"X-eBirdApiToken": EBIRD_KEY})
    print("baixando taxonomia eBird locale=" + locale + " ...")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = {}
    for row in data:
        sci = row.get("sciName")
        com = row.get("comName")
        if sci and com:
            out[sci] = com
    print("  -> " + str(len(out)) + " taxa recebidos")
    return out


def main():
    here = os.getcwd()
    en_path = os.path.join(here, "model", "l18n", "labels_en.json")
    pt_path = os.path.join(here, "model", "l18n", "labels_pt.json")
    out_path = os.path.join(here, "model", "l18n", "labels_pt-BR.json")

    if not os.path.isfile(en_path):
        print("error: nao encontrei " + en_path + " -- rode a partir da raiz do BirdNET-Pi",
              file=sys.stderr)
        return 1

    with open(en_path, encoding="utf-8") as f:
        labels_en = json.load(f)
    with open(pt_path, encoding="utf-8") as f:
        labels_pt = json.load(f) if os.path.isfile(pt_path) else {}

    ebird_ptbr = fetch_taxonomy("pt_BR")
    time.sleep(1)
    ebird_en = fetch_taxonomy("en")

    result = {}
    stats = {"ebird_ptbr": 0, "fallback_pt": 0, "fallback_en": 0}

    for sci, en_name in labels_en.items():
        ptbr_name = ebird_ptbr.get(sci)
        en_from_ebird = ebird_en.get(sci)

        has_real_ptbr = ptbr_name and (
            en_from_ebird is None or ptbr_name.strip().lower() != en_from_ebird.strip().lower()
        )

        if has_real_ptbr:
            result[sci] = ptbr_name
            stats["ebird_ptbr"] += 1
        elif sci in labels_pt and labels_pt[sci].strip().lower() != en_name.strip().lower():
            result[sci] = labels_pt[sci]
            stats["fallback_pt"] += 1
        else:
            result[sci] = en_name
            stats["fallback_en"] += 1

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)

    print("")
    print("escrito: " + out_path)
    print("  nomes pt_BR reais do eBird: " + str(stats["ebird_ptbr"]))
    print("  fallback para pt (Portugal): " + str(stats["fallback_pt"]))
    print("  fallback para en (sem traducao em nenhum dos dois): " + str(stats["fallback_en"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
