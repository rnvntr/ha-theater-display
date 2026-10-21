import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('configure', Path(__file__).resolve().parents[1] / 'scripts/configure.py')
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class ConfigurationTests(unittest.TestCase):
    def values(self):
        return {**config.DEFAULTS, 'KIOSK_URL': 'https://ha.example.test/lovelace/streaming'}

    def test_round_trip_preserves_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            values = self.values()
            values.update(DISPLAY_ROTATION='right', DISPLAY_MODE='1920x1080', IGNORE_CERT_ERRORS='true')
            config.write_config(path, values)
            self.assertEqual(config.read_config(path), values)

    def test_shell_characters_are_quoted_as_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            values = self.values()
            values['KIOSK_URL'] += '?q=$(touch%20UNEXPECTED)&quote=\'test'
            config.write_config(path, values)
            self.assertEqual(config.read_config(path), values)
            self.assertFalse((Path(directory) / 'UNEXPECTED').exists())

    def test_invalid_config_does_not_overwrite_working_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            config.write_config(path, self.values())
            previous = path.read_bytes()
            for key, value in [('KIOSK_URL', 'file:///etc/passwd'), ('DISPLAY_ROTATION', 'sideways'),
                               ('DISPLAY_OUTPUT', 'HDMI-1;reboot'), ('RESTART_DELAY', '0'),
                               ('IGNORE_CERT_ERRORS', 'yes'), ('KIOSK_URL', 'https://user:pass@ha.test')]:
                with self.subTest(key=key, value=value):
                    values = self.values()
                    values[key] = value
                    with self.assertRaises(ValueError):
                        config.write_config(path, values)
                    self.assertEqual(path.read_bytes(), previous)

    def test_existing_shell_commands_are_rejected_not_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            path.write_text('touch UNEXPECTED\n')
            with self.assertRaises(ValueError):
                config.read_config(path)
            self.assertFalse((Path(directory) / 'UNEXPECTED').exists())

    def test_noninteractive_first_install_and_update_preserve_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            args = ['configure.py', '--non-interactive', '--url', self.values()['KIOSK_URL'],
                    '--rotation', 'right', '--mode', '1920x1080', '--allow-insecure-tls']
            with patch('sys.argv', args):
                config.main(path)
            with patch('sys.argv', ['configure.py', '--non-interactive', '--strict-tls']):
                config.main(path)
            values = config.read_config(path)
            self.assertEqual(values['DISPLAY_ROTATION'], 'right')
            self.assertEqual(values['DISPLAY_MODE'], '1920x1080')
            self.assertEqual(values['IGNORE_CERT_ERRORS'], 'false')

    def test_endpoint_failure_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            config.write_config(path, self.values())
            with patch('sys.argv', ['configure.py', '--check-url']), patch.object(config.subprocess, 'run') as run:
                run.return_value.returncode = 60
                with self.assertRaisesRegex(ValueError, 'Dashboard check failed'):
                    config.main(path)
                self.assertNotIn('--insecure', run.call_args.args[0])

    def test_profile_and_explicit_overrides_and_security_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'kiosk.conf'
            values = self.values()
            values.update(IGNORE_CERT_ERRORS='false', ALLOW_MIXED_CONTENT='false')
            config.write_config(path, values)
            with patch('sys.argv', ['configure.py', '--profile', 'pi3-portrait', '--rotation', 'right', '--allow-mixed-content']):
                config.main(path)
            saved = config.read_config(path)
            self.assertEqual(saved['DISPLAY_ROTATION'], 'right')
            self.assertEqual(saved['DISPLAY_MODE'], '1920x1080')
            self.assertEqual(saved['BROWSER_RENDERING'], 'software')
            self.assertEqual(saved['GRAPHICS_DRIVER'], 'kms')
            self.assertEqual(saved['IGNORE_CERT_ERRORS'], 'false')
            self.assertEqual(saved['ALLOW_MIXED_CONTENT'], 'true')
            with patch('sys.argv', ['configure.py', '--block-mixed-content']):
                config.main(path)
            self.assertEqual(config.read_config(path)['ALLOW_MIXED_CONTENT'], 'false')


if __name__ == '__main__':
    unittest.main()
