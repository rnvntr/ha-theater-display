#!/bin/bash
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
for script in "$root/deploy.sh" "$root/bin/"* "$root/tests/"*.sh; do bash -n "$script"; done
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
cp "$root/config/kiosk.conf.example" "$tmp/kiosk.conf"
export KIOSK_CONFIG="$tmp/kiosk.conf"
source "$root/bin/settings"
load_settings
[[ $DISPLAY_ROTATION == left ]]
printf "\nDISPLAY_ROTATION='sideways'\n" >> "$KIOSK_CONFIG"
if (load_settings) 2>/dev/null; then echo 'FAIL: invalid rotation accepted'; exit 1; fi
cp "$root/config/kiosk.conf.example" "$KIOSK_CONFIG"
printf "\nRELOAD_INTERVAL=-1\n" >> "$KIOSK_CONFIG"
if (load_settings) 2>/dev/null; then echo 'FAIL: invalid interval accepted'; exit 1; fi
cp "$root/config/kiosk.conf.example" "$KIOSK_CONFIG"
printf "\nKIOSK_URL='file:///etc/passwd'\n" >> "$KIOSK_CONFIG"
if (load_settings) 2>/dev/null; then echo 'FAIL: invalid URL accepted'; exit 1; fi
cp "$root/config/kiosk.conf.example" "$KIOSK_CONFIG"
mkdir "$tmp/bin"
cat > "$tmp/bin/xrandr" <<'MOCK'
#!/bin/bash
if [[ $1 == --query ]]; then
    printf 'HDMI-1 disconnected\nHDMI-2 connected primary 1920x1080+0+0\n'
else
    printf '%s\n' "$@" > "$XRANDR_ARGS"
fi
MOCK
chmod +x "$tmp/bin/xrandr"
export PATH="$tmp/bin:$PATH" XRANDR_ARGS="$tmp/args"
bash "$root/bin/configure-display"
printf '%s\n' --output HDMI-2 --primary --rotate left --reflect normal --mode 1920x1080 > "$tmp/expected"
diff -u "$tmp/expected" "$XRANDR_ARGS"
cat >> "$KIOSK_CONFIG" <<'CONFIG'
DISPLAY_OUTPUT='HDMI-2'
DISPLAY_ROTATION='inverted'
DISPLAY_REFLECTION='x'
DISPLAY_MODE='1920x1080'
DISPLAY_RATE='60'
CONFIG
bash "$root/bin/configure-display"
printf '%s\n' --output HDMI-2 --primary --rotate inverted --reflect x --mode 1920x1080 --rate 60 > "$tmp/expected"
diff -u "$tmp/expected" "$XRANDR_ARGS"
echo 'PASS: shell syntax, invalid settings, output selection, rotation, reflection and resolution'
source "$root/bin/browser-options"
cp "$root/config/kiosk.conf.example" "$KIOSK_CONFIG"
load_settings
build_browser_args
printf '%s\n' "${args[@]}" > "$tmp/browser-args"
grep -Fxq -- '--window-size=1080,1920' "$tmp/browser-args"
grep -Fxq -- '--disable-gpu' "$tmp/browser-args"
grep -Fxq -- '--force-device-scale-factor=1' "$tmp/browser-args"
if grep -Eq -- '--ignore-certificate-errors|--allow-running-insecure-content|--no-sandbox' "$tmp/browser-args"; then
    echo 'FAIL: unsafe flags enabled by default'; exit 1
fi
DISPLAY_ROTATION=normal; BROWSER_RENDERING=auto
IGNORE_CERT_ERRORS=true; ALLOW_MIXED_CONTENT=true
build_browser_args
printf '%s\n' "${args[@]}" > "$tmp/browser-args"
grep -Fxq -- '--window-size=1920,1080' "$tmp/browser-args"
grep -Fxq -- '--ignore-certificate-errors' "$tmp/browser-args"
grep -Fxq -- '--allow-running-insecure-content' "$tmp/browser-args"
if grep -Fxq -- '--disable-gpu' "$tmp/browser-args"; then echo 'FAIL: auto rendering disables GPU'; exit 1; fi
DISPLAY_MODE=''
build_browser_args
if printf '%s\n' "${args[@]}" | grep -q -- '--window-size='; then echo 'FAIL: automatic mode has fixed browser size'; exit 1; fi
echo 'PASS: portrait browser dimensions, scale, rendering and opt-in compatibility flags'
