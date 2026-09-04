#!/usr/bin/env python3
import os
import sys


def main():
    here = os.getcwd()
    path = os.path.join(here, "avian", "frontend", "apt.js")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    single_replacements = [
        ("btn.innerHTML = ICON_PAUSE + '<span>stop</span>';",
         "btn.innerHTML = ICON_PAUSE;"),
        ("btn.innerHTML = ICON_PLAY + '<span>...</span>';",
         "btn.innerHTML = ICON_PLAY;"),
        ("btn.innerHTML = ICON_PLAY + '<span>no audio</span>';",
         "btn.innerHTML = ICON_PLAY;"),
    ]

    for old, new in single_replacements:
        count = content.count(old)
        if count != 1:
            print("error: '" + old + "' encontrado " + str(count)
                  + "x (esperado 1). Nada foi alterado.", file=sys.stderr)
            return 1

    idle_old = "ICON_PLAY + '<span>play</span>'"
    idle_count = content.count(idle_old)
    if idle_count != 3:
        print("error: '" + idle_old + "' encontrado " + str(idle_count)
              + "x (esperado 3). Nada foi alterado.", file=sys.stderr)
        return 1

    for old, new in single_replacements:
        content = content.replace(old, new)
    content = content.replace(idle_old, "ICON_PLAY")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("botao de play do atlas agora e so icone (6 pontos atualizados: 3 unicos + 3 'play').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
