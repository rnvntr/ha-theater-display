import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('firmware', Path(__file__).resolve().parents[1] / 'scripts/firmware.py')
firmware = importlib.util.module_from_spec(spec)
spec.loader.exec_module(firmware)


class FirmwareTests(unittest.TestCase):
    def test_rotation_normalization_preserves_unrelated_settings(self):
        source = '[all]\ndtoverlay=vc4-kms-v3d\ngpu_mem_1024=76\ntemp_limit=75\ndisplay_rotate=1\n[pi4]\ndisplay_hdmi_rotate=3\n'
        result = firmware.normalize(source)
        self.assertIn('gpu_mem_1024=76', result)
        self.assertIn('temp_limit=75', result)
        self.assertIn('dtoverlay=vc4-kms-v3d', result)
        self.assertIn('# Rotation managed by X11: display_rotate=1', result)
        self.assertIn('# Rotation managed by X11: display_hdmi_rotate=3', result)
        self.assertIn('[all]\ndisable_overscan=1\ndisable_splash=1', result)
        self.assertEqual(result.count('\ndisplay_rotate=0\n'), 1)

    def test_redeployment_does_not_duplicate_firmware_changes(self):
        first = firmware.normalize('display_rotate=1\ndisable_overscan=0\n')
        self.assertEqual(firmware.normalize(first), first)


if __name__ == '__main__':
    unittest.main()
