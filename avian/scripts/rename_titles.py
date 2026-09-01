#!/usr/bin/env python3
import os
import sys


def patch_file(path, old, new, expected_count):
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return False
    with open(path, encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != expected_count:
        print("error: [" + path + "] '" + old + "' encontrado " + str(count)
              + "x (esperado " + str(expected_count) + "). Nada foi alterado.", file=sys.stderr)
        return False
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(path + ": " + str(count) + " ocorrencias substituidas.")
    return True


def main():
    here = os.getcwd()
    html_path = os.path.join(here, "avian", "frontend", "index.html")
    js_path = os.path.join(here, "avian", "frontend", "apt.js")

    ok1 = patch_file(html_path,
                      '<h1 id="staticTitle">Heard Recently</h1>',
                      '<h1 id="staticTitle">Cantos dos Ganchos</h1>',
                      1)

    ok2 = patch_file(js_path,
                      "'Heard Recently'",
                      "'Cantos dos Ganchos'",
                      2)

    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(main())
