#!/usr/bin/env python3
"""Ajusta model/l18n/labels_pt-BR.json para deixar so a primeira letra
maiuscula (mantendo o resto como veio da fonte), em vez de tudo minusculo
ou Title Case.

Uso:
    python3 fix_casing.py
"""
import json
import os
import sys


def sentence_case(s):
    if not s:
        return s
    return s[0].upper() + s[1:]


def main():
    here = os.getcwd()
    path = os.path.join(here, "model", "l18n", "labels_pt-BR.json")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        labels = json.load(f)

    changed = 0
    for sci, name in labels.items():
        fixed = sentence_case(name)
        if fixed != name:
            labels[sci] = fixed
            changed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2, sort_keys=True)

    print("ajustado: " + str(changed) + " de " + str(len(labels)) + " nomes tiveram a capitalizacao corrigida")
    return 0


if __name__ == "__main__":
    sys.exit(main())
