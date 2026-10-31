# Verified console-kiosk deployment

Inspected on 2026-10-30: Raspberry Pi 3 Model B, armv7l, DietPi 10.5.2,
Debian 13, Chromium 149.0.7827.155. The live machine uses **DietPi autostart
mode 11**, root autologin on tty1, and xinit with a portrait launcher.
HDMI-1 uses native 1920x1080 at 60 Hz, rotated left to 1080x1920.

This is different from deploy.sh, which installs a non-root LightDM session.
The LightDM installer has fixture tests but was NOT deployed or hardware-validated
in this inspection. Do not run it on an existing working console kiosk merely to
install the nightly refresh. The observed root browser also has legacy compatibility
flags; these are observations, not recommended defaults for new installations.

## Add nightly recovery to an existing console kiosk

Confirm this is a dedicated display: the restart ends the entire tty1 login session.
SSH sessions are not targeted. It preserves the Chromium profile and login.

    sudo bash scripts/install-console-refresh.sh America/Chicago

The installer validates the existing console layout and backs up prior timer files.
It does not switch startup modes, update DietPi, change Chromium flags, or reboot.
The timer uses an explicit timezone (including daylight saving changes), runs at
00:05, and is not persistent: a missed midnight run will not interrupt the next boot.
The restart helper and generated service/timer were exercised successfully on the
live Pi; the installer wrapper is a reproducible packaging of those steps.

    sudo systemctl start theater-kiosk-restart.service
    systemctl show theater-kiosk-restart.service -p Result -p ExecMainStatus
    systemctl list-timers theater-kiosk-restart.timer
    ps -eo pid,ppid,args | grep '[x]init'

Live test: Result=success, ExecMainStatus=0; a new console session, xinit and
Chromium process appeared. This verifies process recovery, not every playback
provider or physical TV pixel. A fully frozen OS needs a separate watchdog.
Disable scheduling with sudo systemctl disable --now theater-kiosk-restart.timer.

## Home Assistant display

The live gold-frame dashboard renders idle posters and weather; its sidebar entry
is Theater Posters. It retains the previous decoded image while loading the next
and preloads one upcoming poster. Weather icons use HA vector icons, and the degree
mark is drawn with CSS to avoid missing emoji/font glyphs. Scheduling belongs on
the Pi, so no JavaScript midnight reload is needed in the dashboard.

The public dashboard is a configurable example, not a copy of the household's
entities or copyrighted poster collection. Configure players, weather and artwork
as described in home-assistant.md. The private repository stores the actual export.
