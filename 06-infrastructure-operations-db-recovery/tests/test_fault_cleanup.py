"""Offline TEST FIXTURE ONLY: uncertain firewall effects and cleanup failures."""
import subprocess
import unittest
from unittest.mock import patch
import guest_test as guest


class FaultCleanupTests(unittest.TestCase):
    def test_cleanup_attempts_exact_rule_removal_and_restart_even_on_failure(self):
        self.assertTrue(hasattr(guest, 'network_fault'), 'scoped cleanup context missing')
        rule = ['OUTPUT', '-m', 'comment', '--comment', 'ops-db-lab-fixture', '-j', 'REJECT']
        for scenario in ('insert_timeout', 'delete_failure', 'probe_failure', 'probe_timeout', 'restart_failure', 'body_failure', 'normal'):
            with self.subTest(scenario=scenario):
                calls = []
                probes = 0
                def execute(args, **kwargs):
                    nonlocal probes
                    calls.append(args)
                    if '-I' in args and scenario == 'insert_timeout':
                        raise subprocess.TimeoutExpired(args, 1)
                    code = 0
                    if '-C' in args:
                        probes += 1
                        if scenario == 'probe_timeout' and probes == 1:
                            raise subprocess.TimeoutExpired(args, 1)
                        if scenario == 'probe_failure' and probes == 1:
                            code = 2
                        elif probes > 1:
                            code = 0 if scenario == 'delete_failure' else 1
                    if '-D' in args and scenario == 'delete_failure':
                        code = 2
                    return subprocess.CompletedProcess(args, code, '', '')
                fixture = {'observations': {}}
                with patch.object(guest, 'command', side_effect=execute), \
                     patch.object(guest, 'restart', side_effect=RuntimeError('TEST FIXTURE restart failure') if scenario == 'restart_failure' else None) as restart, patch.object(guest, 'REPORT', fixture):
                    try:
                        with guest.network_fault(rule):
                            if scenario == 'body_failure':
                                raise AssertionError('TEST FIXTURE body failure')
                    except (subprocess.TimeoutExpired, RuntimeError, AssertionError):
                        self.assertNotEqual(scenario, 'normal')
                    else:
                        self.assertEqual(scenario, 'normal')
                    restart.assert_called_once()
                self.assertIn(['iptables', '-D'] + rule, calls)
                self.assertGreaterEqual(sum('-C' in call for call in calls), 2)
                outcome = fixture['observations']['network_cleanup']
                self.assertEqual(outcome['service_restored'], scenario != 'restart_failure')
                self.assertEqual(outcome['residual_rule'], scenario == 'delete_failure')
