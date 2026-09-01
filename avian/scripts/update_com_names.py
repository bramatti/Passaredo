#!/usr/bin/env python3
"""Atualiza retroativamente Com_Name na tabela detections do birds.db
usando o mapeamento de model/l18n/labels_pt-BR.json.

Faz backup do banco antes de qualquer alteracao.

Uso:
    python3 update_com_names.py           # dry-run, so mostra o que mudaria
    python3 update_com_names.py --apply   # aplica de verdade
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                     help="aplica as mudancas de verdade (sem isso, so mostra o que mudaria)")
    args = ap.parse_args()

    here = os.getcwd()
    db_path = os.path.join(here, "scripts", "birds.db")
    labels_path = os.path.join(here, "model", "l18n", "labels_pt-BR.json")

    if not os.path.isfile(db_path):
        print("error: nao encontrei " + db_path + " -- rode a partir da raiz do BirdNET-Pi",
              file=sys.stderr)
        return 1
    if not os.path.isfile(labels_path):
        print("error: nao encontrei " + labels_path, file=sys.stderr)
        return 1

    with open(labels_path, encoding="utf-8") as f:
        labels = json.load(f)

    if args.apply:
        backup_path = db_path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
        shutil.copy2(db_path, backup_path)
        print("backup criado: " + backup_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT Sci_Name, Com_Name FROM detections")
    rows = cur.fetchall()

    to_update = []
    unmatched = set()
    already_ok = 0

    for sci, current_com in rows:
        new_com = labels.get(sci)
        if new_com is None:
            unmatched.add(sci)
            continue
        if new_com != current_com:
            to_update.append((sci, current_com, new_com))
        else:
            already_ok += 1

    print("")
    print("especies distintas no banco: " + str(len(rows)))
    print("ja com o nome correto: " + str(already_ok))
    print("precisam de atualizacao: " + str(len(to_update)))
    print("sem correspondencia em labels_pt-BR.json (ficam intocadas): " + str(len(unmatched)))

    if unmatched:
        print("")
        print("especies sem correspondencia (amostra ate 15):")
        for s in sorted(unmatched)[:15]:
            print(" -", s)

    if to_update:
        print("")
        print("amostra de mudancas (ate 15):")
        for sci, old, new in to_update[:15]:
            print(" - " + sci + ": '" + str(old) + "' -> '" + new + "'")

    if not args.apply:
        print("")
        print("modo dry-run -- nada foi alterado. Rode com --apply para aplicar de verdade.")
        conn.close()
        return 0

    total_rows_changed = 0
    for sci, old, new in to_update:
        cur.execute("UPDATE detections SET Com_Name = ? WHERE Sci_Name = ?", (new, sci))
        total_rows_changed += cur.rowcount

    conn.commit()
    conn.close()

    print("")
    print("aplicado: " + str(len(to_update)) + " especies atualizadas, "
          + str(total_rows_changed) + " linhas de deteccao alteradas no total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
