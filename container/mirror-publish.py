#!/usr/bin/env python3
"""ЗАЧЕМ. Сергей 08.11.2026 решил застраховать nasyrov.pro на случай падения Яндекс Облака урезанной
копией на франкфуртском сервере — без заявления в РКН. Чтобы копия не принимала персональные данные:
формы заменены ссылкой на Телеграм, Метрика выключена, Caddy не пишет журнал запросов. В обычные дни
копию никто не видит: DNS переключает на неё сторож `mirror-watch.py` только когда Яндекс лежит.

Builds the stripped copy from this repo and syncs it to Frankfurt (/root/nasyrov-mirror/site).
Called by yc-publish.py after every bucket upload; can be run alone.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from importlib import import_module
yc = import_module("yc-publish")

HOST = "root@38.54.84.115"
KEY = "/root/.ssh/frankfurt_bot"
DEST = "/root/nasyrov-mirror/site"
MIRROR_JS = pathlib.Path(__file__).resolve().parent / "mirror.js"


def build(out):
    n = 0
    for p, key in yc.files():
        dst = out / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == ".html":
            s = p.read_text(encoding="utf-8")
            s = s.replace("YANDEX_METRIKA_ID = 110507843;", "YANDEX_METRIKA_ID = 0;").replace("METRIKA_ID = 110507843;", "METRIKA_ID = 0;")
            s = s.replace("</body>", '<script src="/mirror.js"></script>\n</body>', 1)
            dst.write_text(s, encoding="utf-8")
        else:
            shutil.copy2(p, dst)
        n += 1
    shutil.copy2(MIRROR_JS, out / "mirror.js")
    return n + 1


def main():
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d)
        n = build(out)
        if "110507843" in "".join(f.read_text(errors="ignore") for f in out.rglob("*.html")):
            raise SystemExit("Metrika id left in mirror build")
        ssh = f"ssh -i {KEY} -o ConnectTimeout=20"
        subprocess.run(["ssh", "-i", KEY, HOST, f"mkdir -p {DEST}"], check=True)
        subprocess.run(["rsync", "-a", "--delete", "-e", ssh, f"{out}/", f"{HOST}:{DEST}/"], check=True)
    got = int(subprocess.run(["ssh", "-i", KEY, HOST, f"find {DEST} -type f | wc -l"],
                             capture_output=True, text=True, check=True).stdout)
    if got != n:  # success ≠ no crash
        raise SystemExit(f"mirror has {got} files, expected {n}")
    print(f"mirror: {n} files on Frankfurt")


if __name__ == "__main__":
    main()
