#!/usr/bin/env python3
import os
import sys

OLD = "./avian/frontend/ebird-codes.json"
NEW = "./ebird-codes.json"


def main():
    here = os.getcwd()
    path = os.path.join(here, "avian", "frontend", "apt.js")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    count = content.count(OLD)
    if count != 1:
        print("error: padrao encontrado " + str(count) + "x (esperado 1). Nada foi alterado.",
              file=sys.stderr)
        return 1

    content = content.replace(OLD, NEW)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("caminho corrigido: " + OLD + " -> " + NEW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
