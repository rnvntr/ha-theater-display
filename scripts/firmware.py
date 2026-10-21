#!/usr/bin/env python3
"""Normalize legacy rotation after DietPi enables KMS. All changes backed up by deploy.sh."""
from pathlib import Path
import re
import sys

BEGIN = '# BEGIN HA THEATER DISPLAY'
END = '# END HA THEATER DISPLAY'


def normalize(text):
    text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', '', text, flags=re.S)
    lines = []
    for line in text.splitlines():
        if re.match(r'^\s*display_(?:hdmi_|lcd_)?rotate\s*=', line):
            line = '# Rotation managed by X11: ' + line.strip()
        lines.append(line)
    return '\n'.join(lines).rstrip() + '\n\n' + '\n'.join([
        BEGIN, '[all]', 'disable_overscan=1', 'disable_splash=1',
        '# Rotate only in the X11 session; do not rotate firmware a second time.',
        'display_rotate=0', END, ''])


def main():
    candidates = [Path('/boot/firmware/config.txt'), Path('/boot/config.txt')]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        sys.exit('No Raspberry Pi boot configuration found; cannot configure KMS display.')
    # Preserve symlink target and file permissions used by DietPi.
    path.write_text(normalize(path.read_text()))
    print('Configured overscan, splash and single X11 rotation.')


if __name__ == '__main__':
    main()
