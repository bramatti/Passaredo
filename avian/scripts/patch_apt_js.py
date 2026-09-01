#!/usr/bin/env python3
"""Corrige avian/frontend/apt.js para usar pt.wikipedia.org como link
padrao e aceitar tanto en quanto pt na verificacao de URL retornada
pela API.

Uso:
    python3 patch_apt_js.py
"""
import os
import sys

OLD_1 = "return 'https://en.wikipedia.org/wiki/' + encodeURIComponent(sci.replace(/ /g, '_'));"
NEW_1 = "return 'https://pt.wikipedia.org/wiki/' + encodeURIComponent(sci.replace(/ /g, '_'));"

OLD_2 = r"/^https:\/\/en\.wikipedia\.org\/wiki\//.test(j.source.url || '')"
NEW_2 = r"/^https:\/\/(?:en|pt)\.wikipedia\.org\/wiki\//.test(j.source.url || '')"


def main():
    here = os.getcwd()
    path = os.path.join(here, "avian", "frontend", "apt.js")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    if content.count(OLD_1) != 1:
        print("error: padrao 1 (wikiUrl) nao encontrado exatamente uma vez -- encontrado "
               + str(content.count(OLD_1)) + " vezes. Nada foi alterado.", file=sys.stderr)
        return 1
    if content.count(OLD_2) != 1:
        print("error: padrao 2 (regex de validacao) nao encontrado exatamente uma vez -- encontrado "
              + str(content.count(OLD_2)) + " vezes. Nada foi alterado.", file=sys.stderr)
        return 1

    content = content.replace(OLD_1, NEW_1)
    content = content.replace(OLD_2, NEW_2)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("apt.js atualizado com sucesso: 2 substituicoes aplicadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
