#!/usr/bin/env python3
"""ЗАЧЕМ. Страховка nasyrov.pro (решение Сергея 08.11.2026): основной сайт в Яндекс Облаке, урезанная
копия на Франкфурте (mirror-publish.py). Сторож раз в минуту проверяет Яндекс; после 3 провалов подряд
переводит DNS в Cloudflare на Франкфурт, после 5 успехов подряд возвращает. О каждом переключении —
сообщение Сергею. Раз в сутки забирает сертификат из Yandex Certificate Manager на Франкфурт, чтобы
копия была готова к HTTPS до аварии.

Usage: mirror-watch.py            # one tick (systemd timer, every minute)
       mirror-watch.py --cert     # only refresh the certificate on Frankfurt
       mirror-watch.py --status
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

PRIMARY = "https://d5dpjm73r03uq9ukal8j.764nr5vy.apigw.yandexcloud.net/"
MIRROR = "https://mirror.38-54-84-115.sslip.io/"
MARKER = "Насыров"
MIRROR_IP = "38.54.84.115"
NORMAL = {"nasyrov.pro": ("CNAME", "d5dpjm73r03uq9ukal8j.764nr5vy.apigw.yandexcloud.net"),
          "www.nasyrov.pro": ("CNAME", "www.nasyrov.pro.website.yandexcloud.net")}
CERT_ID = "fpqb0ubpkao29alcqvdc"
KEY = "/root/.ssh/frankfurt_bot"
HOST = "root@38.54.84.115"
STATE = pathlib.Path("/root/.config/nasyrov-mirror/state.json")
CF_ENV = "/root/.config/cloudflare/.env"
FAIL_N, OK_N = 3, 5


def up(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "nasyrov-mirror-watch"}), timeout=15)
        return r.status == 200 and MARKER in r.read(200000).decode("utf-8", "ignore")
    except Exception:
        return False


def cf(method, path, body=None):
    tok = next(l.split("=", 1)[1].strip().strip('"') for l in open(CF_ENV) if l.startswith("CLOUDFLARE_API_TOKEN"))
    req = urllib.request.Request("https://api.cloudflare.com/client/v4" + path,
                                 json.dumps(body).encode() if body else None,
                                 {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}, method=method)
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if not d.get("success"):
        raise RuntimeError(d.get("errors"))
    return d["result"]


def set_dns(to_mirror):
    zone = cf("GET", "/zones?name=nasyrov.pro")[0]["id"]
    for name, (typ, target) in NORMAL.items():
        rec = [r for r in cf("GET", f"/zones/{zone}/dns_records?name={name}") if r["type"] in ("A", "CNAME")]
        body = {"type": "A", "name": name, "content": MIRROR_IP, "ttl": 60, "proxied": False} if to_mirror \
            else {"type": typ, "name": name, "content": target, "ttl": 60, "proxied": False}
        if rec:
            cf("PUT", f"/zones/{zone}/dns_records/{rec[0]['id']}", body)
        else:
            cf("POST", f"/zones/{zone}/dns_records", body)


def tg(text):
    subprocess.run(["tgsend"], input=text, text=True)


def refresh_cert():
    iam = subprocess.run(["/root/.claude/tools/yc-iam.py"], capture_output=True, text=True, check=True).stdout.strip()
    req = urllib.request.Request(f"https://data.certificate-manager.api.cloud.yandex.net/certificate-manager/v1/certificates/{CERT_ID}:getContent",
                                 headers={"Authorization": f"Bearer {iam}"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    chain, key = "".join(d["certificateChain"]), d["privateKey"]
    if "BEGIN CERTIFICATE" not in chain or "PRIVATE KEY" not in key:
        raise SystemExit("certificate content looks wrong")
    script = ("umask 077; mkdir -p /root/nasyrov-mirror/certs && cd /root/nasyrov-mirror/certs && "
              "cat > fullchain.pem.new && mv fullchain.pem.new fullchain.pem")
    subprocess.run(["ssh", "-i", KEY, HOST, script], input=chain, text=True, check=True)
    subprocess.run(["ssh", "-i", KEY, HOST, script.replace("fullchain", "key")], input=key, text=True, check=True)
    subprocess.run(["ssh", "-i", KEY, HOST, "chmod 644 /root/nasyrov-mirror/certs/fullchain.pem; chmod 640 /root/nasyrov-mirror/certs/key.pem; "
                    "docker exec medbook-web caddy reload --config /etc/caddy/Caddyfile"], check=True)
    print("cert refreshed")


def main():
    STATE.parent.mkdir(parents=True, exist_ok=True)
    st = json.loads(STATE.read_text()) if STATE.exists() else {"mode": "primary", "fails": 0, "oks": 0, "cert_day": ""}
    if "--status" in sys.argv:
        return print(st)
    if "--cert" in sys.argv:
        return refresh_cert()
    today = time.strftime("%Y-%m-%d")
    if st.get("cert_day") != today:
        try:
            refresh_cert()
            st["cert_day"] = today
        except Exception as e:
            print("cert refresh failed:", e)
    ok = up(PRIMARY)
    st["fails"], st["oks"] = (0, st["oks"] + 1) if ok else (st["fails"] + 1, 0)
    if st["mode"] == "primary" and st["fails"] >= FAIL_N:
        if up(MIRROR):
            set_dns(True)
            st["mode"] = "mirror"
            tg("⚠️ nasyrov.pro: Яндекс Облако не отвечает 3 минуты, переключил сайт на запасную копию во Франкфурте (без формы заявок).")
        elif not st.get("mirror_alerted"):
            tg("⚠️ nasyrov.pro: Яндекс Облако не отвечает, а запасная копия во Франкфурте тоже лежит. Сайт недоступен.")
            st["mirror_alerted"] = True
    elif st["mode"] == "mirror" and st["oks"] >= OK_N:
        set_dns(False)
        st["mode"], st["mirror_alerted"] = "primary", False
        tg("✅ nasyrov.pro: Яндекс Облако снова отвечает, вернул сайт на основной адрес.")
    if ok:
        st["mirror_alerted"] = False
    STATE.write_text(json.dumps(st))


if __name__ == "__main__":
    main()
