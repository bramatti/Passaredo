#!/usr/bin/env python3
"""Adiciona link para WikiAves e conserta EBIRD_CODES para usar o
mapeamento completo gerado via API (avian/frontend/ebird-codes.json)
em vez do pequeno objeto fixo (so especies norte-americanas).

Uso:
    python3 add_wikiaves.py
"""
import os
import sys

ARROW = "\u2197"


def patch_file(path, replacements):
    if not os.path.isfile(path):
        print("error: nao encontrei " + path, file=sys.stderr)
        return False
    with open(path, encoding="utf-8") as f:
        content = f.read()
    for label, old, new in replacements:
        count = content.count(old)
        if count != 1:
            print("error: [" + path + "] padrao '" + label + "' encontrado "
                  + str(count) + "x (esperado 1). Nada foi alterado neste arquivo.",
                  file=sys.stderr)
            return False
    for label, old, new in replacements:
        content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(path + ": " + str(len(replacements)) + " substituicoes aplicadas.")
    return True


def main():
    here = os.getcwd()

    html_path = os.path.join(here, "avian", "frontend", "index.html")
    html_old = ('          <a id="modalEbird" target="_blank" rel="noopener">eBird '
                '<span aria-hidden="true">' + ARROW + '</span></a>')
    html_new = (html_old + "\n"
                '          <a id="modalWikiAves" target="_blank" rel="noopener">WikiAves '
                '<span aria-hidden="true">' + ARROW + '</span></a>')
    ok1 = patch_file(html_path, [("botao modalWikiAves", html_old, html_new)])

    js_path = os.path.join(here, "avian", "frontend", "apt.js")

    ebird_codes_old = """  var EBIRD_CODES = {
    'Agelaius phoeniceus': 'rewbla',
    'Aix sponsa': 'wooduc',
    'Anas platyrhynchos': 'mallar3',
    'Aphelocoma californica': 'cowscj1',
    'Aphelocoma woodhouseii': 'wooscj2',
    'Archilochus alexandri': 'bkchum',
    'Ardea herodias': 'grbher3',
    'Baeolophus inornatus': 'oaktit',
    'Bombycilla cedrorum': 'cedwax',
    'Branta canadensis': 'cangoo',
    'Bubo virginianus': 'grhowl',
    'Buteo jamaicensis': 'rethaw',
    'Calypte anna': 'annhum',
    'Corvus brachyrhynchos': 'amecro',
    'Haemorhous mexicanus': 'houfin',
    'Larus occidentalis': 'wesgul',
    'Mimus polyglottos': 'normoc',
    'Passer domesticus': 'houspa',
    'Sayornis nigricans': 'blkpho',
    'Spinus psaltria': 'lesgol',
    'Turdus migratorius': 'amerob',
    'Zenaida macroura': 'moudov',
    'Zonotrichia leucophrys': 'whcspa'
  };"""

    ebird_codes_new = """  // Populated asynchronously from ebird-codes.json (built by
  // avian/scripts/build_ebird_codes.py against the eBird taxonomy API,
  // covering the full BirdNET species list rather than a handful of
  // North American backyard birds).
  var EBIRD_CODES = {};"""

    loadtables_old = """    return Promise.all([
      fetch('./dims.json' + q).then(function (r) { return r.json(); }),
      fetch('./masks.json' + q).then(function (r) { return r.json(); })
    ]).then(function (loaded) {
      DIMS = loaded[0];
      MASKS = loaded[1];"""

    loadtables_new = """    return Promise.all([
      fetch('./dims.json' + q).then(function (r) { return r.json(); }),
      fetch('./masks.json' + q).then(function (r) { return r.json(); }),
      fetch('./avian/frontend/ebird-codes.json' + q).then(function (r) { return r.json(); }).catch(function () { return {}; })
    ]).then(function (loaded) {
      DIMS = loaded[0];
      MASKS = loaded[1];
      EBIRD_CODES = loaded[2] || {};"""

    ebirdurl_old = """  function ebirdUrl(sci) {
    var code = EBIRD_CODES[sci];
    return code ? 'https://ebird.org/species/' + code : '';
  }"""

    ebirdurl_new = """  function ebirdUrl(sci) {
    var code = EBIRD_CODES[sci];
    return code ? 'https://ebird.org/species/' + code : '';
  }
  function wikiavesUrl(com) {
    if (!com) return '';
    var slug = com.toLowerCase()
      .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
    return slug ? 'https://www.wikiaves.com.br/wiki/' + slug : '';
  }"""

    card_vars_old = """        var birdWiki = wikiUrl(s.sci);
        var birdEbird = ebirdUrl(s.sci);"""

    card_vars_new = """        var birdWiki = wikiUrl(s.sci);
        var birdEbird = ebirdUrl(s.sci);
        var birdWikiAves = wikiavesUrl(s.com);"""

    card_chip_old = """          + (birdEbird ? '<a class="chip ext" href="' + escHtml(birdEbird) + '" target="_blank" rel="noopener" aria-label="eBird">ebird</a>' : '')
          + '</div>'"""

    card_chip_new = """          + (birdEbird ? '<a class="chip ext" href="' + escHtml(birdEbird) + '" target="_blank" rel="noopener" aria-label="eBird">ebird</a>' : '')
          + (birdWikiAves ? '<a class="chip ext" href="' + escHtml(birdWikiAves) + '" target="_blank" rel="noopener" aria-label="WikiAves">wikiaves</a>' : '')
          + '</div>'"""

    modal_old = """    var ebirdLink = document.getElementById('modalEbird');
    var ebirdHref = ebirdUrl(sci);
    ebirdLink.hidden = !ebirdHref;
    if (ebirdHref) ebirdLink.href = ebirdHref;
    else ebirdLink.removeAttribute('href');"""

    modal_new = """    var ebirdLink = document.getElementById('modalEbird');
    var ebirdHref = ebirdUrl(sci);
    ebirdLink.hidden = !ebirdHref;
    if (ebirdHref) ebirdLink.href = ebirdHref;
    else ebirdLink.removeAttribute('href');
    var wikiavesLink = document.getElementById('modalWikiAves');
    var wikiavesHref = wikiavesUrl((lifelistBird && lifelistBird.com) || '');
    wikiavesLink.hidden = !wikiavesHref;
    if (wikiavesHref) wikiavesLink.href = wikiavesHref;
    else wikiavesLink.removeAttribute('href');"""

    ok2 = patch_file(js_path, [
        ("EBIRD_CODES hardcoded -> vazio", ebird_codes_old, ebird_codes_new),
        ("loadTables fetch ebird-codes.json", loadtables_old, loadtables_new),
        ("wikiavesUrl function", ebirdurl_old, ebirdurl_new),
        ("card vars birdWikiAves", card_vars_old, card_vars_new),
        ("card chip wikiaves", card_chip_old, card_chip_new),
        ("modal wikiaves link", modal_old, modal_new),
    ])

    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(main())
