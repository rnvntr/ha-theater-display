# HA Theater Display

[![Checks](https://github.com/rnvntr/ha-theater-display/actions/workflows/check.yml/badge.svg)](https://github.com/rnvntr/ha-theater-display/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A lightweight portrait kiosk for a Raspberry Pi 3 B running DietPi. It opens a
dashboard on your existing Home Assistant server. One deployment script installs
the display software, configures automatic startup and reboots the Pi.

**Status:** scripts tested with simulated displays and configuration fixtures.
Real hardware acceptance is pending. A configurable HA poster dashboard is included. Follow [Home Assistant setup](docs/home-assistant.md) to install the card, configure your players and upload idle posters before deploying the Pi.

## First deployment

Start with DietPi installed, networking working, and the TV connected by HDMI.
Use the dedicated display Pi: deployment takes over its graphical boot session.

```sh
sudo apt-get update
sudo apt-get install -y git
git clone --depth 1 https://github.com/rnvntr/ha-theater-display.git
cd ha-theater-display
sudo bash deploy.sh
```

Authenticate to GitHub if the repository is private. On first run the script asks
for the dashboard URL, rotation, and optional native resolution. It installs the
dependencies, checks the endpoint, enables startup, and reboots automatically.
Choose `inverted` for upside-down or `left`/`right` for portrait.
Fresh installs default to the Pi 3 baseline: native 1920x1080, left rotation,
software browser rendering, and a 1080x1920 fullscreen browser at scale factor 1.
The setup also asks whether this local endpoint needs certificate or mixed-content
compatibility; both protections remain enabled unless you explicitly opt out.

When the browser first opens, sign in to HA with a dedicated non-admin display
account. Sign-in persists across boots and updates. Kiosk mode does not bypass HA
authentication. A reachable URL does not prove that the view exists or that the
browser is signed in; confirm the screen after first deployment.

## Update: pull and run one script

```sh
git pull --ff-only
sudo bash deploy.sh
```

Saved settings and the browser profile are retained. The script reboots after
successful deployment. If validation fails, it exits without scheduling a reboot.
Backups are printed during deployment and remain private on the Pi.

## Fully scripted configuration

```sh
sudo bash deploy.sh --non-interactive \
  --url 'https://homeassistant.example.com/lovelace/streaming' \
  --profile pi3-portrait --hostname theater-display
```

Replace the example URL. The mode is the monitor's **landscape mode before
rotation**: `1920x1080` rotated left becomes `1080x1920`. Use `--mode ''` to use the
preferred mode. `--output HDMI-1` selects an explicit output; otherwise the first
connected output is used. Omit `--hostname` to preserve the existing name.
`--no-reboot` defers reboot. `--help` lists all options.

For an endpoint using an untrusted certificate, prefer fixing its certificate or
using a trusted hostname. For a trusted local endpoint only, explicitly opt in:

```sh
sudo bash deploy.sh --allow-insecure-tls
```

This disables certificate verification for the kiosk browser and its endpoint
check. It persists until `sudo bash deploy.sh --strict-tls` is run.
If the dashboard also embeds insecure HTTP resources, `--allow-mixed-content`
enables that independently; `--block-mixed-content` restores blocking. The Pi 3
preset does not enable either exception. Chromium's sandbox remains enabled.

To reproduce the recovered browser compatibility settings on a trusted local
dashboard, while using modern graphics and a dedicated non-root account:

```sh
sudo bash deploy.sh --profile pi3-portrait --allow-insecure-tls --allow-mixed-content
```

On a new install this still asks for the URL; for a saved setup it reuses the URL.
`--rendering auto` restores Chromium's default GPU behavior. `--profile
pi3-portrait` intentionally reapplies display/rendering settings, so omit it for
ordinary updates if you have customized them.

## How it works

- LightDM autostarts a dedicated `poster-kiosk` user and minimal Openbox X11 session.
- Screen blanking is disabled, the cursor is hidden, and Chromium is fullscreen.
- Rotation follows the inherited X11 display, not a hardcoded display number.
- Missing monitors are retried; the browser restarts after exit.
- A periodic restart (default 30 minutes) reloads the dashboard after outages.
- Known old Chromium overrides are backed up and retired to avoid conflicting flags.
- DietPi's supported LightDM mode replaces console kiosk startup.
- Full KMS is explicitly selected through DietPi; legacy firmware rotation is
  disabled so X11 rotates once. Overscan and the boot splash are disabled.
- No root browser and no patching of DietPi's Chromium launcher.

Configuration: `/etc/tv-poster-system/kiosk.conf`. Scripts: `/opt/tv-poster-system`.
These paths stay stable across updates. Set advanced options through the script:
`--reflection normal|x|y|xy`, `--rate 60`, `--restart-delay 10`, and
`--reload-interval 1800` (`0` disables periodic reload). No file editing is required.

## Check after reboot

```sh
sudo /opt/tv-poster-system/bin/check-health
```

This verifies autostart, running session/browser and dashboard reachability. It
does not certify authentication, artwork or visible orientation. Confirm these
on the actual screen.

Troubleshooting:

```sh
sudo journalctl -u lightdm -b --no-pager
sudo tail -n 100 /home/poster-kiosk/.local/state/tv-poster-system/session.log
sudo tail -n 100 /home/poster-kiosk/.xsession-errors
```

Rotation applies to X11, not early boot text. Connect a monitor that advertises
a valid mode. The old FKMS driver is not copied onto fresh systems; KMS is used
with X11 rotation. Existing memory splits, temperature limits, audio and unrelated
firmware settings are not copied from another machine. DietPi may adjust HDMI audio
when enabling KMS. Those settings are backed up before changes.
Advanced `--graphics dietpi` skips the project's explicit driver and firmware
normalization; DietPi's LightDM setup can still enable a graphics driver. Use this
only when maintaining a separately configured display stack.

## Backups and rollback

Before configuration changes, the script saves existing boot, LightDM, Chromium
overrides, hostname, boot command line, audio configuration and kiosk settings
under `/var/backups/tv-poster-system/`.
Backups may contain sensitive settings. Package installation is not automatically
rolled back if a later step fails.

To disable the kiosk and boot to a console:

```sh
sudo systemctl disable --now lightdm
sudo /boot/dietpi/dietpi-autostart 0
sudo systemctl set-default multi-user.target
```

This is not a full restoration. To recover a prior installation, review the backup,
restore its settings and select its original DietPi startup mode. Browser profile
data is retained.

## Development

```sh
bash tests/check.sh
python3 -m unittest discover -s tests
```

See [the command audit](docs/command-audit.md), [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md). Raw recovery material,
private settings and unused artwork are excluded from the repository.

Code and documentation: [MIT](LICENSE). Dependencies retain their licenses;
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Upstream: [DietPi desktop documentation](https://dietpi.com/docs/software/desktop/)
and [autostart implementation](https://github.com/MichaIng/DietPi/blob/master/dietpi/dietpi-autostart).
