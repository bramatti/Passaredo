#!/usr/bin/env python3
"""Sobrescreve manualmente o nome de Troglodytes aedon em
model/l18n/labels_pt-BR.json para "Corruira" (nome tradicional
preferido pelo usuario, em vez do "Corruira-boreal" que veio da
taxonomia mais recente do eBird).

Uso:
    python3 fix_troglodytes.py
"""
import json
import os
import sys

SCI = "Troglodytes aedon"
NEW_NAME = "Corru\u00edra"


def main():
    here = os.getcwd()
    path = os.path.join(here, "model", "l18n", "labels_pt-BR.json")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        labels = json.load(f)

    if SCI not in labels:
        print("error: " + SCI + " nao encontrado no arquivo", file=sys.stderr)
        return 1

    old = labels[SCI]
    labels[SCI] = NEW_NAME

    with open(path, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2, sort_keys=True)

    print(SCI + ": '" + old + "' -> '" + NEW_NAME + "'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
