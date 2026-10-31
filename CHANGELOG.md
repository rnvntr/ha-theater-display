# Changelog

## 2026-10-30

- Document the verified DietPi mode-11 console deployment separately from LightDM.
- Add an opt-in 00:05 systemd kiosk-session restart installer.
- Preserve the live installation details in the private repository only.

## Unreleased

- Reconciled running-server display and browser settings with a Pi 3 portrait preset.
- Software rendering, scale factor 1 and rotation-aware browser dimensions.
- Separate explicit mixed-content compatibility option.
- Full KMS setup, overscan/splash configuration and legacy rotation normalization.
- Firmware and browser-option regression checks; raw local leftovers removed.

- One deploy.sh entry point for configuration, installation and reboot.
- First-run prompts, non-interactive options and persistent local settings.
- Endpoint/TLS validation and optional untrusted-certificate compatibility.
- Non-root Chromium profile and LightDM startup.
- Configurable rotation, output, resolution, refresh rate and reflection.
- Missing-display retry and bounded periodic browser restarts.
- Optional hostname configuration, backups and retirement of known old overrides.
- Health check and command audit without identifying information.
- Obsolete launcher and unused artwork excluded from the active repository.
- Generic examples, authorship and licensing.

Real hardware acceptance and the HA movie dashboard remain unverified.
