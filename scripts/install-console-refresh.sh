#!/bin/bash
# Add a nightly restart to an EXISTING DietPi mode-11 console kiosk.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if [[ ${1:-} == --help ]]; then
    echo 'Usage: sudo bash scripts/install-console-refresh.sh [IANA_TIMEZONE]'
    echo 'Restarts the dedicated tty1 kiosk at 00:05; does not reboot the Pi.'
    exit 0
fi
[[ $EUID -eq 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
zone=${1:-}
[[ -n $zone ]] || zone=$(timedatectl show -p Timezone --value)
[[ $zone =~ ^[A-Za-z0-9_+/-]+$ && $zone != *..* && -f /usr/share/zoneinfo/$zone ]] || { echo 'Invalid timezone' >&2; exit 1; }
[[ $(cat /boot/dietpi/.dietpi-autostart_index) == 11 ]] || { echo 'Requires an existing DietPi mode-11 Chromium kiosk.' >&2; exit 1; }
if systemctl is-active --quiet lightdm; then echo 'LightDM is active; this console recipe does not apply.' >&2; exit 1; fi
systemctl cat getty@tty1.service | grep -Eq 'agetty.*-a root' || { echo 'Expected dedicated root console autologin was not found.' >&2; exit 1; }
backup=/var/backups/theater-kiosk-refresh/$(date +%Y%m%d-%H%M%S)
install -d -m 0700 "$backup"
for f in /usr/local/sbin/theater-kiosk-restart /etc/systemd/system/theater-kiosk-restart.{service,timer}; do
    if [[ -f $f ]]; then cp -a "$f" "$backup/"; fi
done
install -m 0755 "$root/bin/theater-kiosk-restart" /usr/local/sbin/theater-kiosk-restart
cat > /etc/systemd/system/theater-kiosk-restart.service <<'UNIT'
[Unit]
Description=Restart theater poster kiosk session
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/theater-kiosk-restart
TimeoutStartSec=60
UNIT
cat > /etc/systemd/system/theater-kiosk-restart.timer <<UNIT
[Unit]
Description=Nightly theater poster refresh
[Timer]
OnCalendar=*-*-* 00:05:00 $zone
AccuracySec=1s
Persistent=false
[Install]
WantedBy=timers.target
UNIT
systemd-analyze verify /etc/systemd/system/theater-kiosk-restart.{service,timer}
systemctl daemon-reload
systemctl enable --now theater-kiosk-restart.timer
systemctl list-timers theater-kiosk-restart.timer --no-pager
