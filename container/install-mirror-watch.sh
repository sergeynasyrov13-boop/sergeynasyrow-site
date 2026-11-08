#!/bin/bash
# ЗАЧЕМ. Сторож страховки nasyrov.pro (mirror-watch.py) должен тикать раз в минуту. Ставит systemd-таймер
# на стамбульском сервере. Запускает Сергей: ! bash /root/sergeynasyrow-site/container/install-mirror-watch.sh
set -e
cat > /etc/systemd/system/nasyrov-mirror-watch.service <<'U'
[Unit]
Description=nasyrov.pro failover watchdog (Yandex -> Frankfurt mirror)
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /root/sergeynasyrow-site/container/mirror-watch.py
TimeoutStartSec=900
U
cat > /etc/systemd/system/nasyrov-mirror-watch.timer <<'U'
[Unit]
Description=nasyrov.pro failover watchdog every minute
[Timer]
OnBootSec=2min
OnUnitActiveSec=60s
[Install]
WantedBy=timers.target
U
systemctl daemon-reload
systemctl enable --now nasyrov-mirror-watch.timer
systemctl list-timers nasyrov-mirror-watch.timer --no-pager | head -2
