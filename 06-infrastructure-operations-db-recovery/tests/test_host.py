"""Offline host safety tests. Mocked Multipass responses are TEST FIXTURE ONLY."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import lab


class HostSafetyTests(unittest.TestCase):
    def test_upload_uses_recursive_fixed_package_without_overwrite(self):
        # TEST FIXTURE ONLY: a pristine guest path, no real Multipass invocation.
        calls = []
        def checked(args, timeout=900):
            calls.append(args)
            if 'transfer' in args:
                source = Path(args[-2])
                self.assertEqual(source.name, 'ops-db-package')
                self.assertTrue((source / 'assets/forum-api.tar.gz').is_file())
                self.assertEqual(args[-1], 'ops-db-lab:/home/ubuntu/')
                self.assertIn('--recursive', args)
            return 'absent'
        with patch.object(lab, 'checked', side_effect=checked):
            lab.upload()
        transfer = next(c for c in calls if 'transfer' in c)
        self.assertIn('--recursive', transfer)
        self.assertFalse(any('tar' in c for c in calls))

    def test_existing_unmarked_or_partial_package_is_never_overwritten(self):
        for state in ('unmarked', 'partial', 'symlink', 'wrong-hash'):
            with self.subTest(state=state), patch.object(lab, 'checked', return_value=state) as checked:
                with self.assertRaises(RuntimeError):
                    lab.upload()
                self.assertFalse(any('transfer' in c.args[0] for c in checked.call_args_list))

    def test_up_refuses_existing_unmarked_installation_before_upload(self):
        vm = {'name': lab.VM, 'release': 'Ubuntu 24.04 LTS', 'state': 'Running'}
        with patch.object(lab, 'vm_list', return_value=vm), \
             patch.object(lab, 'call', return_value=subprocess.CompletedProcess([], 0, '', '')), \
             patch.object(lab, 'checked', return_value='unmarked'), \
             patch.object(lab, 'upload') as upload:
            with self.assertRaises(RuntimeError):
                lab.up()
            upload.assert_not_called()

    def test_up_bootstraps_fixed_package_with_bytecode_disabled(self):
        calls = []
        def call(args, timeout=900):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, 'TEST FIXTURE ONLY', '')
        with patch.object(lab, 'vm_list', return_value=None), \
             patch.object(lab, 'call', side_effect=call), \
             patch.object(lab, 'checked', return_value='pristine'), \
             patch.object(lab, 'record'), patch.object(lab, 'upload'):
            lab.up()
        self.assertIn(['multipass', 'exec', 'ops-db-lab', '--', 'sudo', 'python3', '-B',
                       '/home/ubuntu/ops-db-package/bootstrap.py'], calls)
        self.assertEqual(calls[0], ['multipass', 'launch', '24.04', '--name', 'ops-db-lab',
                                   '--cpus', '2', '--memory', '1G', '--disk', '8G'])

    def test_test_fetches_fixed_summary_via_sudo_not_guest_report_paths(self):
        # TEST FIXTURE ONLY: guest output is not a trusted path/filename source.
        report = {'run_id': 'fixture_run', 'fixture_label': 'TEST FIXTURE ONLY', 'status': 'passed',
                  'passed': 1, 'total': 1, 'checks': [{'name': 'fixture', 'passed': True}], 'observations': {}}
        calls = []
        def call(args, timeout=900):
            calls.append(args)
            if lab.PACKAGE + '/guest_test.py' in args:
                run_id = args[-1]
                self.assertRegex(run_id, r'^[a-f0-9]{32}$')
                report['run_id'] = run_id
            return subprocess.CompletedProcess(args, 0, 'TEST FIXTURE ONLY', '')
        def checked(args, timeout=900):
            calls.append(args)
            return json.dumps(report)
        with tempfile.TemporaryDirectory() as temp, patch.object(lab, 'EVIDENCE', Path(temp)), \
             patch.object(lab, 'vm_list', return_value={'state': 'Running'}), \
             patch.object(lab, 'call', side_effect=call), patch.object(lab, 'checked', side_effect=checked), \
             patch.object(lab, 'upload'), patch.object(lab, 'record'):
            try:
                lab.test()
            except RuntimeError as error:
                self.fail('Fixed summary must be fetched without stdout paths: ' + str(error))
            self.assertTrue((Path(temp) / ('integration-' + report['run_id'] + '.json')).is_file())
            self.assertEqual(json.loads((Path(temp) / 'report-summary.json').read_text()), report)
        self.assertTrue(any('/var/lib/ops-db-lab/evidence/report-summary.json' in c and 'sudo' in c for c in calls))
        self.assertTrue(any('/home/ubuntu/ops-db-package/guest_test.py' in c and '-B' in c for c in calls))
        self.assertTrue(any('test*.py' in c for c in calls))

    def _run_summary_fixture(self, evidence, status, guest_exit, fresh):
        # TEST FIXTURE ONLY: intercept every guest/subprocess boundary, not report validation/export.
        report = {'run_id': 'old_run', 'fixture_label': 'TEST FIXTURE ONLY', 'status': status,
                  'passed': int(status == 'passed'), 'total': 1,
                  'checks': [{'name': 'fixture', 'passed': status == 'passed'}], 'observations': {}}
        def call(args, timeout=900):
            if lab.PACKAGE + '/guest_test.py' in args:
                if fresh:
                    report['run_id'] = args[-1]
                return subprocess.CompletedProcess(args, guest_exit, 'TEST FIXTURE ONLY',
                                                   'TEST FIXTURE ONLY guest failure' if guest_exit else '')
            return subprocess.CompletedProcess(args, 0, 'TEST FIXTURE ONLY safety tests', '')
        with patch.object(lab, 'EVIDENCE', evidence), \
             patch.object(lab, 'vm_list', return_value={'state': 'Running'}), \
             patch.object(lab, 'call', side_effect=call), \
             patch.object(lab, 'checked', side_effect=lambda *args, **kwargs: json.dumps(report)), \
             patch.object(lab, 'upload'):
            lab.test()

    def test_stale_success_is_never_published_for_either_guest_exit(self):
        for guest_exit in (1, 0):
            with self.subTest(guest_exit=guest_exit), tempfile.TemporaryDirectory() as temp:
                evidence = Path(temp)
                latest = evidence / 'report-summary.json'
                previous = b'TEST FIXTURE ONLY: previously published evidence\n'
                latest.write_bytes(previous)
                with self.assertRaisesRegex(RuntimeError, 'fresh|run_id'):
                    self._run_summary_fixture(evidence, 'passed', guest_exit, fresh=False)
                self.assertEqual(latest.read_bytes(), previous)
                self.assertFalse(list(evidence.glob('integration-*.json')))

    def test_fresh_status_exit_mismatch_is_never_published(self):
        for status, guest_exit in (('passed', 1), ('failed', 0)):
            with self.subTest(status=status, guest_exit=guest_exit), tempfile.TemporaryDirectory() as temp:
                evidence = Path(temp)
                latest = evidence / 'report-summary.json'
                previous = b'TEST FIXTURE ONLY: previously published evidence\n'
                latest.write_bytes(previous)
                with self.assertRaisesRegex(RuntimeError, 'status.*exit|exit.*status|consistent'):
                    self._run_summary_fixture(evidence, status, guest_exit, fresh=True)
                self.assertEqual(latest.read_bytes(), previous)
                self.assertFalse(list(evidence.glob('integration-*.json')))

    def test_fresh_failed_report_is_retained_with_cli_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)
            with self.assertRaisesRegex(RuntimeError, 'integration failed'):
                self._run_summary_fixture(evidence, 'failed', 1, fresh=True)
            report = json.loads((evidence / 'report-summary.json').read_text())
            self.assertRegex(report['run_id'], r'^[a-f0-9]{32}$')
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['fixture_label'], 'TEST FIXTURE ONLY')
            self.assertEqual(json.loads((evidence / ('integration-' + report['run_id'] + '.json')).read_text()), report)
            logs = list(evidence.glob('*-integration.log'))
            self.assertEqual(len(logs), 1)
            self.assertIn('exit_code=1', logs[0].read_text())
            self.assertIn('TEST FIXTURE ONLY guest failure', logs[0].read_text())

    def test_guest_report_rejects_path_injection_and_secret_fields(self):
        self.assertTrue(hasattr(lab, 'validate_report'), 'guest report safety validator is missing')
        good = {'run_id': 'fixture_123', 'fixture_label': 'TEST FIXTURE ONLY', 'status': 'passed',
                'passed': 1, 'total': 1, 'checks': [{'name': 'fixture', 'passed': True}], 'observations': {}}
        lab.validate_report(good)
        for bad in (dict(good, run_id='../escape'), dict(good, PGPASSWORD='TEST FIXTURE SECRET'),
                    dict(good, observations={'accessToken': 'TEST FIXTURE SECRET'}),
                    dict(good, total=2)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lab.validate_report(bad)



