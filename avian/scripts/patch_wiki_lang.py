#!/usr/bin/env python3
import os
import sys

OLD = """function preferredWikiLang(): string
{
    static $lang = null;
    if ($lang !== null) {
        return $lang;
    }
    $birdnetpiDir = dirname(__DIR__, 2);
    $conf = @parse_ini_file("$birdnetpiDir/birdnet.conf", false, INI_SCANNER_RAW);
    $dbLang = is_array($conf) ? (string)($conf['DATABASE_LANG'] ?? '') : '';
    $lang = (stripos($dbLang, 'pt') === 0) ? 'pt' : 'en';
    return $lang;
}"""

NEW = """function preferredWikiLang(): string
{
    static $lang = null;
    if ($lang !== null) {
        return $lang;
    }
    // birdnet.conf isn't strictly INI-valid (some comment lines contain
    // parentheses), so parse_ini_file can fail on the whole file. Read the
    // DATABASE_LANG value directly instead, the same way scripts/config.php
    // already does when it writes this file.
    $birdnetpiDir = dirname(__DIR__, 2);
    $raw = @file_get_contents("$birdnetpiDir/birdnet.conf");
    $dbLang = '';
    if ($raw !== false && preg_match('/^DATABASE_LANG=(.*)$/m', $raw, $m)) {
        $dbLang = trim($m[1]);
    }
    $lang = (stripos($dbLang, 'pt') === 0) ? 'pt' : 'en';
    return $lang;
}"""


def main():
    here = os.getcwd()
    path = os.path.join(here, "avian", "api", "wiki.php")
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return 1

    with open(path, encoding="utf-8") as f:
        content = f.read()

    count = content.count(OLD)
    if count != 1:
        print("error: padrao nao encontrado exatamente uma vez -- encontrado "
              + str(count) + " vezes. Nada foi alterado.", file=sys.stderr)
        return 1

    content = content.replace(OLD, NEW)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("wiki.php atualizado: preferredWikiLang() agora le DATABASE_LANG via regex.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
