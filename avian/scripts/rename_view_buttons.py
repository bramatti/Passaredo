#!/usr/bin/env python3
import os
import sys


def main():
    here = os.getcwd()
    path = os.path.join(here, "avian", "frontend", "index.html")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    replacements = [
        ('<button type="button" data-i="0" aria-current="true">collage</button>',
         '<button type="button" data-i="0" aria-current="true">passaredo</button>'),
        ('<button type="button" data-i="1">stats</button>',
         '<button type="button" data-i="1">dados</button>'),
        ('<button type="button" data-i="2">atlas</button>',
         '<button type="button" data-i="2">galeria</button>'),
    ]

    for old, new in replacements:
        count = content.count(old)
        if count != 1:
            print("error: '" + old + "' encontrado " + str(count)
                  + "x (esperado 1). Nada foi alterado.", file=sys.stderr)
            return 1

    for old, new in replacements:
        content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("3 botoes atualizados: passaredo / dados / galeria")
    return 0


if __name__ == "__main__":
    sys.exit(main())
