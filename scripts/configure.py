#!/usr/bin/env python3
"""Read simple assignments as data, never execute configuration as root."""
import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

DEFAULTS = dict(KIOSK_URL='', DISPLAY_OUTPUT='auto', DISPLAY_ROTATION='left',
                DISPLAY_REFLECTION='normal', DISPLAY_MODE='1920x1080', DISPLAY_RATE='',
                RESTART_DELAY='10', RELOAD_INTERVAL='1800', IGNORE_CERT_ERRORS='false',
                ALLOW_MIXED_CONTENT='false', BROWSER_RENDERING='software', GRAPHICS_DRIVER='kms')


def read_config(path):
    values = DEFAULTS.copy()
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, sep, value = line.partition('=')
            if not sep or key not in values:
                raise ValueError('Unsupported configuration key: ' + key)
            parts = shlex.split(value, comments=True)
            if len(parts) != 1:
                raise ValueError('Expected one quoted value for ' + key)
            values[key] = parts[0]
    return values


def validate(values):
    url = urlsplit(values['KIOSK_URL'])
    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
        raise ValueError('Provide an HTTP(S) dashboard URL without embedded credentials.')
    if any(c in values['KIOSK_URL'] for c in '\r\n\t'):
        raise ValueError('Invalid whitespace in URL')
    if values['DISPLAY_ROTATION'] not in ('normal', 'left', 'right', 'inverted'):
        raise ValueError('Invalid rotation')
    if values['DISPLAY_REFLECTION'] not in ('normal', 'x', 'y', 'xy'):
        raise ValueError('Invalid reflection')
    if not re.fullmatch(r'[A-Za-z0-9_.:-]+', values['DISPLAY_OUTPUT']):
        raise ValueError('Invalid display output')
    for key, pattern in [('DISPLAY_MODE', r'\d+x\d+'), ('DISPLAY_RATE', r'\d+(\.\d+)?')]:
        if values[key] and not re.fullmatch(pattern, values[key]):
            raise ValueError('Invalid ' + key)
    for key in ('RESTART_DELAY', 'RELOAD_INTERVAL'):
        if not re.fullmatch(r'0|[1-9][0-9]*', values[key]):
            raise ValueError('Invalid ' + key)
    if int(values['RESTART_DELAY']) < 1:
        raise ValueError('RESTART_DELAY must be positive')
    for key in ('IGNORE_CERT_ERRORS', 'ALLOW_MIXED_CONTENT'):
        if values[key] not in ('true', 'false'):
            raise ValueError('Invalid ' + key)
    if values['BROWSER_RENDERING'] not in ('software', 'auto'):
        raise ValueError('Invalid browser rendering mode')
    if values['GRAPHICS_DRIVER'] not in ('kms', 'dietpi'):
        raise ValueError('Invalid graphics driver setting')


def write_config(path, values):
    validate(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as output:
            output.write('# Managed by deploy.sh; local settings survive updates.\n')
            for key, value in values.items():
                output.write(key + '=' + shlex.quote(value) + '\n')
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main(config_path=Path('/etc/tv-poster-system/kiosk.conf')):
    parser = argparse.ArgumentParser()
    for option in ('url', 'rotation', 'output', 'mode', 'reflection', 'rate', 'reload-interval', 'restart-delay', 'rendering', 'graphics'):
        parser.add_argument('--' + option)
    parser.add_argument('--profile', choices=['pi3-portrait'])
    parser.add_argument('--print-graphics', action='store_true')
    tls = parser.add_mutually_exclusive_group()
    tls.add_argument('--allow-insecure-tls', action='store_true')
    tls.add_argument('--strict-tls', action='store_true')
    mixed = parser.add_mutually_exclusive_group()
    mixed.add_argument('--allow-mixed-content', action='store_true')
    mixed.add_argument('--block-mixed-content', action='store_true')
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--check-url', action='store_true')
    parser.add_argument('--set-hosts')
    args = parser.parse_args()
    if args.set_hosts:
        if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', args.set_hosts):
            raise ValueError('Invalid hostname')
        hosts = Path('/etc/hosts')
        lines = hosts.read_text().splitlines()
        lines = [line for line in lines if not re.match(r'^\s*127\.0\.1\.1\s', line)]
        hosts.write_text('\n'.join(lines) + '\n127.0.1.1\t' + args.set_hosts + '\n')
        return
    path = config_path
    values = read_config(path)
    if args.profile == 'pi3-portrait':
        values.update(DISPLAY_ROTATION='left', DISPLAY_MODE='1920x1080',
                      DISPLAY_OUTPUT='auto', DISPLAY_REFLECTION='normal', DISPLAY_RATE='',
                      BROWSER_RENDERING='software', GRAPHICS_DRIVER='kms')
    for option, key in [('url', 'KIOSK_URL'), ('rotation', 'DISPLAY_ROTATION'),
                        ('output', 'DISPLAY_OUTPUT'), ('mode', 'DISPLAY_MODE'),
                        ('reflection', 'DISPLAY_REFLECTION'), ('rate', 'DISPLAY_RATE'),
                        ('reload_interval', 'RELOAD_INTERVAL'), ('restart_delay', 'RESTART_DELAY'),
                        ('rendering', 'BROWSER_RENDERING'), ('graphics', 'GRAPHICS_DRIVER')]:
        if getattr(args, option) is not None:
            values[key] = getattr(args, option)
    if args.allow_insecure_tls:
        values['IGNORE_CERT_ERRORS'] = 'true'
    if args.strict_tls:
        values['IGNORE_CERT_ERRORS'] = 'false'
    if args.allow_mixed_content:
        values['ALLOW_MIXED_CONTENT'] = 'true'
    if args.block_mixed_content:
        values['ALLOW_MIXED_CONTENT'] = 'false'
    if not path.exists() and not args.non_interactive and not args.check_url and not args.url:
        if not sys.stdin.isatty():
            parser.error('First install requires --url when no interactive terminal is available.')
        values['KIOSK_URL'] = input('Home Assistant dashboard URL: ').strip()
        values['DISPLAY_ROTATION'] = input('Rotation [left/right/normal/inverted] (left): ').strip() or 'left'
        answer = input('Native resolution [1920x1080], or auto: ').strip()
        values['DISPLAY_MODE'] = '' if answer == 'auto' else (answer or values['DISPLAY_MODE'])
        if not args.allow_insecure_tls and not args.strict_tls:
            values['IGNORE_CERT_ERRORS'] = 'true' if input('Ignore TLS certificate errors for this trusted local endpoint? [y/N]: ').strip().lower() == 'y' else 'false'
        if not args.allow_mixed_content and not args.block_mixed_content:
            values['ALLOW_MIXED_CONTENT'] = 'true' if input('Allow insecure HTTP content inside the HTTPS dashboard? [y/N]: ').strip().lower() == 'y' else 'false'
    validate(values)
    if args.print_graphics:
        print(values['GRAPHICS_DRIVER'])
    elif args.check_url:
        command = ['curl', '--silent', '--show-error', '--fail', '--location',
                   '--connect-timeout', '10', '--max-time', '30', '--output', '/dev/null']
        if values['IGNORE_CERT_ERRORS'] == 'true':
            command.append('--insecure')
        result = subprocess.run(command + ['--', values['KIOSK_URL']], check=False)
        if result.returncode:
            raise ValueError('Dashboard check failed. Fix URL/network/certificate and rerun. '
                             'Only for a trusted local endpoint with an untrusted certificate, '
                             'explicitly select --allow-insecure-tls.')
        print('Dashboard endpoint reachable (does not verify HA login or view contents).')
    else:
        write_config(path, values)
        if values['IGNORE_CERT_ERRORS'] == 'true':
            print('WARNING: certificate validation is disabled for this kiosk browser.')
        if values['ALLOW_MIXED_CONTENT'] == 'true':
            print('WARNING: insecure active content is allowed inside HTTPS pages.')
        print('Configuration saved.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
