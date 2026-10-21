#!/bin/bash
# Single entry point: configure, install, validate, reboot.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ ${1:-} == --help ]]; then
    cat <<'HELP'
Usage: sudo bash deploy.sh [options]
First run asks for the dashboard URL and display settings. Later runs preserve them.
  --url URL                  Home Assistant dashboard URL
  --profile pi3-portrait      Apply 1080p left-portrait software-rendering preset
  --rendering MODE            software (Pi 3 default) or auto
  --graphics MODE             kms (default) or dietpi (upstream driver selection)
  --rotation VALUE           normal, left, right, inverted
  --output NAME              auto or an xrandr output name
  --mode WIDTHxHEIGHT        Native landscape mode, before rotation
  --reflection VALUE         normal, x, y or xy
  --rate HZ                  Refresh rate (blank for automatic)
  --reload-interval SECONDS   Periodic browser restart; 0 disables
  --restart-delay SECONDS     Delay between browser starts; minimum 1
  --hostname NAME            Optional hostname for this dedicated Pi
  --allow-insecure-tls       Explicitly allow untrusted HTTPS certificates
  --strict-tls               Restore certificate validation
  --allow-mixed-content      Allow HTTP resources inside HTTPS pages
  --block-mixed-content      Restore mixed-content blocking
  --non-interactive          No prompts; requires URL on first install
  --no-reboot                Install/configure without rebooting
  --help                    Show this help
HELP
    exit 0
fi
[[ $EUID -eq 0 ]] || { echo 'Run with sudo: sudo bash deploy.sh' >&2; exit 1; }
[[ -f /boot/dietpi.txt && -x /boot/dietpi/dietpi-autostart ]] || { echo 'DietPi is required.' >&2; exit 1; }
reboot=1; hostname=''; config_args=()
while (($#)); do
    case "$1" in
        --no-reboot) reboot=0; shift;;
        --hostname) [[ $# -ge 2 ]] || exit 2; hostname=$2; shift 2;;
        --url|--rotation|--output|--mode|--reflection|--rate|--reload-interval|--restart-delay|--profile|--rendering|--graphics)
            [[ $# -ge 2 ]] || { echo "Missing value: $1" >&2; exit 2; }
            config_args+=("$1" "$2"); shift 2;;
        --allow-insecure-tls|--strict-tls|--non-interactive|--allow-mixed-content|--block-mixed-content) config_args+=("$1"); shift;;
        *) echo "Unknown option: $1 (see --help)" >&2; exit 2;;
    esac
done
if [[ -n $hostname ]]; then
    [[ ${#hostname} -le 63 && $hostname =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$ ]] || { echo 'Invalid hostname' >&2; exit 2; }
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends python3 curl ca-certificates
backup="/var/backups/tv-poster-system/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$backup"
chmod 0700 "$backup"
for path in /etc/tv-poster-system /etc/hostname /etc/hosts /etc/chromium.d /boot/dietpi.txt /boot/dietpi/.dietpi-autostart_index /boot/firmware/config.txt /boot/config.txt /boot/firmware/cmdline.txt /boot/cmdline.txt /etc/modprobe.d /etc/asound.conf /root/.asoundrc /etc/lightdm /etc/systemd/system/display-manager.service /etc/systemd/system/getty@tty1.service.d /etc/systemd/system/console-getty.service.d /etc/systemd/system/dietpi-autostart_custom.service /etc/systemd/system/dietpi-autostart_custom.service.d; do
    if [[ -e $path || -L $path ]]; then cp -a --parents "$path" "$backup/"; fi
done
systemctl get-default > "$backup/default-target.txt"
echo "Backup: $backup"
python3 "$root/scripts/configure.py" "${config_args[@]}"
# Validate network/TLS before changing the boot mode. No root sourcing of settings.
python3 "$root/scripts/configure.py" --check-url
apt-get install -y --no-install-recommends chromium xserver-xorg x11-xserver-utils lightdm openbox unclutter dbus-x11 fonts-dejavu-core
if ! id poster-kiosk >/dev/null 2>&1; then useradd --create-home --shell /bin/bash poster-kiosk; fi
[[ $(id -u poster-kiosk) -ne 0 ]] || exit 1
for group in video render audio input; do
    if getent group "$group" >/dev/null; then usermod -aG "$group" poster-kiosk; fi
done
install -d /opt/tv-poster-system/bin /opt/tv-poster-system/scripts /usr/share/xsessions
install -m 0755 "$root/bin/"* /opt/tv-poster-system/bin/
install -m 0755 "$root/scripts/"*.py /opt/tv-poster-system/scripts/
install -m 0644 "$root/config/tv-poster.desktop" /usr/share/xsessions/tv-poster.desktop
# Retire only the two known historical overrides; preserve them in the backup.
for name in 98-ha-portrait 99-ha-kiosk; do
    if [[ -f /etc/chromium.d/$name ]]; then mv "/etc/chromium.d/$name" "$backup/$name.disabled"; fi
done
if [[ -n $hostname ]]; then
    hostnamectl set-hostname "$hostname"
    python3 "$root/scripts/configure.py" --set-hosts "$hostname"
fi
graphics=$(python3 "$root/scripts/configure.py" --print-graphics)
if [[ $graphics == kms ]]; then
    [[ -x /boot/dietpi/func/dietpi-set_hardware ]] || { echo 'DietPi graphics helper missing'; exit 1; }
    /boot/dietpi/func/dietpi-set_hardware rpi-opengl vc4-kms-v3d
    python3 "$root/scripts/firmware.py"
fi
/boot/dietpi/dietpi-autostart 16
install -d /etc/lightdm/lightdm.conf.d
install -m 0644 "$root/config/90-tv-poster.conf" /etc/lightdm/lightdm.conf.d/90-tv-poster.conf
systemctl set-default graphical.target
systemctl enable lightdm
systemctl is-enabled lightdm >/dev/null
echo 'Installation complete. On first boot, sign in to Home Assistant on the screen.'
echo 'After boot: sudo /opt/tv-poster-system/bin/check-health'
if (( reboot )); then
    echo 'Rebooting in 5 seconds...'; sleep 5; systemctl reboot
else
    echo 'Reboot deferred (--no-reboot). Reboot to activate this configuration.'
fi
