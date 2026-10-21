# Contributing

This project is currently a DietPi kiosk deployment base. Hardware validation
and recovery of the original Home Assistant dashboard are ongoing.

1. Make a focused branch and explain the behavior being changed.
2. Keep shell scripts compatible with Bash on Debian/DietPi, using LF line endings.
3. Run `bash tests/check.sh` and `python3 -m unittest discover -s tests` before submitting changes.
4. For boot/display changes, report the Pi model, DietPi/Debian version, display
   mode, rotation, and results after a cold boot. Distinguish mock tests from
   testing on actual hardware.
5. Preserve local settings, browser sessions, and rollback information on updates.

Do not commit tokens, passwords, browser profiles, raw server backups, or private
conversation exports. Add sample configuration with placeholders instead.
Do not run `deploy.sh` on a development workstation: it changes boot behavior and reboots.

Artwork must have documented provenance and appropriate redistribution rights
before adding it for publication. See `THIRD_PARTY_NOTICES.md`.
