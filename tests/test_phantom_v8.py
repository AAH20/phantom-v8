import unittest
from phantom_v8.models import HIDActionType
from phantom_v8.hid_kernel_injector import HIDKernelInjector
from phantom_v8.anti_fingerprint_core import AntiFingerprintCore


class TestPhantomV8(unittest.TestCase):
    def setUp(self):
        self.injector = HIDKernelInjector()
        self.anti_fp = AntiFingerprintCore()

    def test_hid_mouse_packet_packing(self):
        packet = self.injector.generate_mouse_hid_packet(
            x=250,
            y=400,
            button_mask=1,
            delta_x=15,
            delta_y=-5
        )
        self.assertEqual(packet.action_type, HIDActionType.MOUSE_DOWN)
        self.assertEqual(len(packet.hardware_report_bytes), 5)
        self.assertEqual(packet.x, 250)
        self.assertEqual(packet.y, 400)

    def test_natural_trajectory_generation(self):
        start = (10, 10)
        end = (100, 200)
        steps = 15
        trajectory = self.injector.generate_natural_trajectory(start, end, steps=steps)
        self.assertEqual(len(trajectory), steps)
        # Verify delta sum roughly covers the distance
        total_dx = sum(p.delta_x for p in trajectory)
        total_dy = sum(p.delta_y for p in trajectory)
        self.assertAlmostEqual(total_dx, end[0] - start[0], delta=10)
        self.assertAlmostEqual(total_dy, end[1] - start[1], delta=10)

    def test_anti_fingerprint_audit_clean_vs_leaked(self):
        # 1. Clean environment
        clean_audit = self.anti_fp.audit_environment({
            "navigator.webdriver": False,
            "canvas_fingerprint": "organic_noise",
            "input_delay_variance": 0.4
        })
        self.assertEqual(clean_audit.score, 1.0)
        self.assertFalse(clean_audit.cdp_leaks_detected)
        self.assertFalse(clean_audit.webdriver_flag_present)

        # 2. Leaked environment
        leaked_audit = self.anti_fp.audit_environment({
            "navigator.webdriver": True,
            "window.cdc_adoQpoasnfa76pfcZLmcfl_Array": True,
            "canvas_fingerprint": "deterministic_bot_hash",
            "input_delay_variance": 0.0
        })
        self.assertLess(leaked_audit.score, 0.5)
        self.assertTrue(leaked_audit.cdp_leaks_detected)
        self.assertTrue(leaked_audit.webdriver_flag_present)
        self.assertIn("navigator.webdriver is exposed as True", leaked_audit.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
