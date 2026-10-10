"""TEST FIXTURE ONLY: bind host request identity before privileged operations."""
import unittest
from unittest.mock import patch
import guest_test as guest


class RunBindingTests(unittest.TestCase):
    def test_host_run_id_binds_report_and_rejects_unsafe_identifiers(self):
        self.assertTrue(hasattr(guest, 'bind_run_id'), 'host run binding missing')
        report = {'run_id': 'fixture_old'}
        value = 'f' * 32
        with patch.object(guest, 'REPORT', report), patch.object(guest, 'RUN', 'fixture_old'):
            guest.bind_run_id(value)
            self.assertEqual(guest.RUN, value)
            self.assertEqual(report['run_id'], value)
            for invalid in ('../escape', 'A' * 32, 'x' * 64, '', None):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    guest.bind_run_id(invalid)
            self.assertEqual(guest.RUN, value)
            self.assertEqual(report['run_id'], value)
