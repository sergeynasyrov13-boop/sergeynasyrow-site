#!/usr/bin/env python3
"""ЗАЧЕМ. Питерский сервер Beget, где жил сайт, уничтожен атакой 1–2.11.2026. Сергей 07.11 решил
временно держать nasyrov.pro в Яндекс Облаке: страницы в бакете `nasyrov.pro` (Object Storage),
форма — функцией, всё в России (уведомление в РКН: трансграничной передачи нет).

Uploads the site from this repo to the bucket. Clean URLs (/offer → offer.html) are served by also
uploading every page under its extensionless key with Content-Type text/html — Object Storage has
no rewrite rules. Files that never ship (blocks/, netlify/, container/, md, git) are skipped.

Usage: /root/.claude/tools/.venv/bin/python container/yc-publish.py [--dry]
Keys: /root/.config/yandex-cloud/site-admin-s3.json (static key of service account site-admin).
"""
import json
import mimetypes
import pathlib
import sys

import boto3

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUCKET = "nasyrov.pro"
SKIP_DIRS = {".git", "blocks", "netlify", "container", ".impeccable", "node_modules"}
SKIP_FILES = {"CLAUDE.md", "README.md", "netlify.toml", ".gitignore", ".dockerignore"}
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "application/javascript",
         ".json": "application/json; charset=utf-8", ".webp": "image/webp", ".woff2": "font/woff2",
         ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".ico": "image/x-icon"}


def files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_file() and rel.parts[0] not in SKIP_DIRS and rel.name not in SKIP_FILES:
            yield p, rel.as_posix()


def main(dry):
    k = json.loads(pathlib.Path("/root/.config/yandex-cloud/site-admin-s3.json").read_text())
    s3 = boto3.client("s3", endpoint_url="https://storage.yandexcloud.net", region_name="ru-central1",
                      aws_access_key_id=k["accessKey"]["keyId"], aws_secret_access_key=k["secret"])
    n = 0
    for p, key in files():
        ctype = TYPES.get(p.suffix) or mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        keys = [key] + ([key[:-5]] if p.suffix == ".html" and p.name != "index.html" else [])
        for kk in keys:
            if dry:
                print(kk, ctype)
            else:
                cache = "no-cache" if p.suffix == ".html" else "public, max-age=86400"
                s3.upload_file(str(p), BUCKET, kk, ExtraArgs={"ContentType": ctype, "CacheControl": cache})
            n += 1
    print(f"{'would upload' if dry else 'uploaded'} {n} objects to {BUCKET}")
    if not dry:  # success ≠ no crash: the bucket must hold at least what we sent
        got = sum(1 for _ in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET) for _ in _.get("Contents", []))
        if got < n:
            raise SystemExit(f"bucket has {got} objects, expected ≥ {n}")
        print(f"bucket check: {got} objects")


if __name__ == "__main__":
    main("--dry" in sys.argv)
