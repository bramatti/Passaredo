#!/usr/bin/env python3
"""Gera model/l18n/labels_pt-BR.json a partir da taxonomia do eBird.

Logica de prioridade por especie:
  1. Nome pt_BR real (distinto do fallback de Portugal que o eBird usa
     internamente) -> nome brasileiro genuino.
  2. Nome pt_BR que e identico ao nome "pt" (ou seja, o eBird nao tem
     nome brasileiro proprio e caiu para o de Portugal) -> ainda assim
     fica em portugues, so que de Portugal (melhor que ingles).
  3. Especie nao encontrada em nenhum dos dois locales do eBird
     (mismatch de nome cientifico/taxonomia) -> tenta o labels_pt.json
     local do BirdNET; se tambem nao tiver, cai para o nome em ingles.

Uso:
    EBIRD_API_KEY=sua_chave python3 build_pt_br_labels_v2.py
"""
import json
import os
import sys
import time
import urllib.request

EBIRD_KEY = os.environ.get("EBIRD_API_KEY", "")
if not EBIRD_KEY:
    print("error: defina EBIRD_API_KEY no ambiente", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.ebird.org/v2/ref/taxonomy/ebird"

def fetch(locale, retries=5):
    url = BASE + "?fmt=json&locale=" + locale
    req = urllib.request.Request(url, headers={"X-eBirdApiToken": EBIRD_KEY})
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
            data = json.loads(raw.decode("utf-8"))
            return {r["sciName"]: r["comName"] for r in data if r.get("sciName") and r.get("comName")}
        except Exception as e:
            last_err = e
            print("  tentativa " + str(attempt) + " falhou (" + str(e) + "), tentando de novo...")
            time.sleep(3 * attempt)
    raise last_err


def main():
    here = os.getcwd()
    en_path = os.path.join(here, "model", "l18n", "labels_en.json")
    pt_local_path = os.path.join(here, "model", "l18n", "labels_pt.json")
    out_path = os.path.join(here, "model", "l18n", "labels_pt-BR.json")

    if not os.path.isfile(en_path):
        print("error: nao encontrei " + en_path + " -- rode a partir da raiz do BirdNET-Pi",
              file=sys.stderr)
        return 1

    with open(en_path, encoding="utf-8") as f:
        labels_en = json.load(f)
    with open(pt_local_path, encoding="utf-8") as f:
        labels_pt_local = json.load(f) if os.path.isfile(pt_local_path) else {}

    print("baixando pt_BR...")
    ebird_ptbr = fetch("pt_BR")
    print("  -> " + str(len(ebird_ptbr)) + " taxa")
    time.sleep(1)
    print("baixando pt...")
    ebird_pt = fetch("pt")
    print("  -> " + str(len(ebird_pt)) + " taxa")

    result = {}
    stats = {"brasileiro_real": 0, "fallback_portugal_ebird": 0,
              "fallback_pt_local": 0, "fallback_en": 0}

    for sci, en_name in labels_en.items():
        ptbr_val = ebird_ptbr.get(sci)
        pt_val = ebird_pt.get(sci)

        if ptbr_val:
            if pt_val and ptbr_val.strip().lower() == pt_val.strip().lower():
                # eBird nao tem nome brasileiro proprio, usou o de Portugal
                # como fallback interno. Ainda assim fica em portugues.
                result[sci] = ptbr_val
                stats["fallback_portugal_ebird"] += 1
            else:
                result[sci] = ptbr_val
                stats["brasileiro_real"] += 1
        elif sci in labels_pt_local:
            result[sci] = labels_pt_local[sci]
            stats["fallback_pt_local"] += 1
        else:
            result[sci] = en_name
            stats["fallback_en"] += 1

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)

    print("")
    print("escrito: " + out_path)
    print("  nomes brasileiros reais (CBRO/eBird Brasil): " + str(stats["brasileiro_real"]))
    print("  fallback para Portugal (via eBird): " + str(stats["fallback_portugal_ebird"]))
    print("  fallback para labels_pt.json local (mismatch taxonomico): " + str(stats["fallback_pt_local"]))
    print("  fallback final para ingles (sem opcao em portugues): " + str(stats["fallback_en"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
