#!/usr/bin/env python3
import json, os, sys, time, urllib.request

EBIRD_KEY = os.environ.get("EBIRD_API_KEY", "")
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

here = os.getcwd()
with open(os.path.join(here, "model", "l18n", "labels_en.json"), encoding="utf-8") as f:
    labels_en = json.load(f)

print("baixando pt_BR...")
ebird_ptbr = fetch("pt_BR")
print("  -> " + str(len(ebird_ptbr)) + " taxa")
time.sleep(1)
print("baixando pt...")
ebird_pt = fetch("pt")
print("  -> " + str(len(ebird_pt)) + " taxa")

not_found_at_all = []
found_but_matches_pt = 0
found_and_distinct = 0

for sci in labels_en:
    if sci not in ebird_ptbr:
        not_found_at_all.append(sci)
    else:
        ptbr_val = ebird_ptbr[sci]
        pt_val = ebird_pt.get(sci)
        if pt_val and ptbr_val.strip().lower() == pt_val.strip().lower():
            found_but_matches_pt += 1
        else:
            found_and_distinct += 1

print("")
print("total especies BirdNET:", len(labels_en))
print("nao encontradas em ebird_ptbr (mismatch de nome cientifico):", len(not_found_at_all))
print("encontradas mas identicas ao nome de Portugal (fallback interno do eBird):", found_but_matches_pt)
print("encontradas e distintas (provavel nome brasileiro real):", found_and_distinct)
print("")
print("amostra de nao encontradas (10):")
for s in not_found_at_all[:10]:
    print(" -", s)
