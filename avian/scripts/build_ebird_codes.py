#!/usr/bin/env python3
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


def fetch_taxonomy(retries=5):
    url = BASE + "?fmt=json"
    req = urllib.request.Request(url, headers={"X-eBirdApiToken": EBIRD_KEY})
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
            data = json.loads(raw.decode("utf-8"))
            out = {}
            for row in data:
                sci = row.get("sciName")
                code = row.get("speciesCode")
                if sci and code:
                    out[sci] = code
            return out
        except Exception as e:
            last_err = e
            print("  tentativa " + str(attempt) + " falhou (" + str(e) + "), tentando de novo...")
            time.sleep(3 * attempt)
    raise last_err


def main():
    here = os.getcwd()
    en_path = os.path.join(here, "model", "l18n", "labels_en.json")
    out_path = os.path.join(here, "avian", "frontend", "ebird-codes.json")

    if not os.path.isfile(en_path):
        print("error: nao encontrei " + en_path + " -- rode a partir da raiz do BirdNET-Pi",
              file=sys.stderr)
        return 1

    with open(en_path, encoding="utf-8") as f:
        labels_en = json.load(f)

    print("baixando taxonomia eBird (codigos de especie)...")
    ebird_codes = fetch_taxonomy()
    print("  -> " + str(len(ebird_codes)) + " taxa recebidos")

    result = {}
    unmatched = []
    for sci in labels_en:
        code = ebird_codes.get(sci)
        if code:
            result[sci] = code
        else:
            unmatched.append(sci)

    with open(out_path, "w", encoding="ascii") as f:
        json.dump(result, f, indent=0, sort_keys=True)

    print("")
    print("escrito: " + out_path)
    print("  codigos encontrados: " + str(len(result)) + " de " + str(len(labels_en)))
    print("  sem correspondencia: " + str(len(unmatched)))
    if unmatched:
        print("  amostra sem correspondencia (10):")
        for s in unmatched[:10]:
            print("   -", s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
