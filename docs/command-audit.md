# Command-history audit

The recovered history was reviewed as evidence, not executed as a script.
Personal names, device names, addresses, entity IDs and raw transcripts are excluded.

| Historical operation | Deployment coverage |
| --- | --- |
| Install Chromium and display software | Install X11, LightDM, Openbox, Chromium and utilities |
| Select startup / start LightDM | DietPi mode 16, dedicated autologin session, service enabled |
| Find the X11 display | Inherit DISPLAY from the login session |
| Rotate HDMI left | Configurable rotation, reflection, resolution and refresh rate |
| Portrait window size | Native 1920x1080 with left rotation produces explicit 1080x1920 browser dimensions; automatic mode omits a fixed window size |
| Disable screensaver/DPMS, hide pointer | xset, unclutter and LightDM settings |
| Set URL and check endpoint | First-run prompts or CLI; check before activation |
| Ignore certificate errors | Explicit --allow-insecure-tls option; default off |
| Allow mixed content | Explicit --allow-mixed-content option; default off |
| Root browser with no sandbox | Replaced by a dedicated non-root browser |
| Edit global Chromium overrides | Two known overrides backed up and retired |
| Patch DietPi launcher | Independent installed session replaces this |
| Change hostname/hosts | Optional --hostname sets both |
| Remove root browser locks | Separate dedicated profile avoids old root profile locks; no blind deletion of live locks |
| Repeated reboot commands | One reboot after successful deployment |
| Check processes and logs | Installed check-health plus documented logs |
| Software browser rendering | Pi 3 baseline disables GPU, GPU compositing and accelerated 2D canvas, matching the supplied working flags |
| Browser scale and kiosk interaction | Scale factor 1, maximized/fullscreen, fixed origin, pinch/overscroll navigation disabled, translation and crash-bubble flags carried over |
| Experimental GPU rasterization | Not forced; the final supplied browser config disables GPU rendering |
| FKMS overlay and display_rotate=1 | Modern full KMS through DietPi; legacy firmware rotation neutralized to avoid double rotation; X11 rotates left |
| disable_overscan=1 / disable_splash=1 | Managed boot block configures both |
| GPU memory split 76 MB / thermal and turbo settings | Existing values left to the OS/device; not blindly copied to new hardware |
| hdmi_blanking=1 | Firmware idle policy left alone; kiosk disables X11 blanking and DPMS |
| Framebuffer 1920x1080 / browser 1080x1920 | Native landscape display mode and rotated browser dimensions handled separately |
| Inspect crontab | Final contents unknown; no schedule invented |
| Edit .xprofile/.xsessionrc | Dedicated LightDM session replaces these experiments |

The running server files now confirm the browser flags and firmware settings above.
The AUTO_SETUP_AUTOSTART_TARGET_INDEX in dietpi.txt is a first-setup preference,
not proof of the current live startup mode; deployment configures the live mode
through dietpi-autostart. No legacy .xprofile or patched root launcher is needed.
The unused historical --disable-infobars flag is omitted; kiosk/fullscreen and
no-first-run options cover the intended presentation without relying on that flag.

Crontab contents, the HA view, authentication and actual graphics performance still
need verification on hardware. The deployment base does not create an HA dashboard
or claim hardware acceptance has passed.

Driver rationale: https://www.raspberrypi.com/documentation/computers/legacy_config_txt.html
