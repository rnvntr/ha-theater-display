# Security

This project launches a persistent browser session logged into Home Assistant.
Use a dedicated non-admin HA account and restrict physical/network access to
the display. Hiding a dashboard or entering kiosk mode does not enforce access
control. Do not store an administrator session on a public-facing screen.

Keep DietPi and browser packages updated. Use a trusted HTTPS endpoint. The
launcher does not disable Chromium's sandbox. Certificate checks are enabled by
default; `--allow-insecure-tls` explicitly disables them for the kiosk browser.
Use it only for a trusted local endpoint, and prefer a trusted certificate.
Use `--strict-tls` to restore verification.
`--allow-mixed-content` separately permits insecure active resources within HTTPS
pages; it is disabled by default. Use `--block-mixed-content` to restore blocking.

`/etc/tv-poster-system/kiosk.conf` is sourced as shell code by the kiosk user.
It should remain root-owned and not writable by untrusted users. Treat the
Chromium profile as sensitive session data; never attach it to an issue.

## Reporting

Use GitHub's private vulnerability reporting feature if it is enabled for this
repository. Otherwise, contact the repository owner through an existing private
channel. Do not post credentials or exploitable details in a public issue.
No response-time or supported-release guarantee is currently offered; this is
an early deployment base awaiting hardware validation.
