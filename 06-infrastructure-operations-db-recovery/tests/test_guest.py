"""Guest functions tested offline: every database/network response is TEST FIXTURE ONLY."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import guest_test as guest


class GuestSafetyTests(unittest.TestCase):
    def test_deliberate_restart_resets_systemd_start_limit_before_restart(self):
        calls = []
        def execute(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, '', '')
        with patch.object(guest, 'command', side_effect=execute), \
             patch.object(guest, 'http', return_value=(200, {})):
            guest.restart()
        self.assertEqual(calls, [
            ['systemctl', 'reset-failed', guest.SERVICE],
            ['systemctl', 'restart', guest.SERVICE]])

    def test_restore_revokes_public_database_privileges_before_loading_archive(self):
        # TEST FIXTURE ONLY: exercise ordering at the privileged command boundary.
        target = 'opslab_restore_fixture'
        events = []
        def query(statement, db=guest.SOURCE):
            events.append(('sql', statement, db))
            return 'opslab_forum' if statement.startswith('SELECT') else ''
        def command(args, **kwargs):
            events.append(('command', args))
            return subprocess.CompletedProcess(args, 0, '', '')
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / 'fixture.dump'
            archive.write_bytes(b'TEST FIXTURE ONLY')
            with patch.object(guest, 'query', side_effect=query), \
                 patch.object(guest, 'command', side_effect=command), \
                 patch.object(guest, 'validate_archive', return_value=archive), \
                 patch.object(guest.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, b'', b'')):
                guest.restore(archive, 'TEST FIXTURE SHA', target)
        expected = ('sql', f'REVOKE ALL ON DATABASE {target} FROM PUBLIC; GRANT CONNECT ON DATABASE {target} TO opslab_app,opslab_reader;', 'postgres')
        self.assertIn(expected, events)
        self.assertGreater(events.index(expected), next(i for i, e in enumerate(events) if e[0] == 'command' and 'createdb' in e[1]))

    def test_restored_access_keeps_reader_readonly_and_app_without_ddl(self):
        self.assertTrue(hasattr(guest, 'grant_restored_access'), 'target ACL helper missing')
        statements = []
        with patch.object(guest, 'query', side_effect=lambda sql, db: statements.append((sql, db))):
            guest.grant_restored_access('opslab_restore_fixture')
        self.assertTrue(all(db == 'opslab_restore_fixture' for _, db in statements))
        sql = ' '.join(statement for statement, _ in statements)
        self.assertIn('REVOKE CREATE ON SCHEMA public FROM PUBLIC', sql)
        self.assertIn('GRANT SELECT ON ALL TABLES IN SCHEMA public TO opslab_reader', sql)
        self.assertIn('GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO opslab_app', sql)
        self.assertNotIn('TO opslab_app,opslab_reader;', sql.split('GRANT SELECT,INSERT,UPDATE,DELETE')[1].split('GRANT')[0])

    def test_summary_written_to_fixed_protected_path_even_on_failure(self):
        self.assertTrue(hasattr(guest, 'write_report'), 'fixed summary writer is missing')
        fixture = {'run_id': 'fixture_run', 'fixture_label': 'TEST FIXTURE ONLY', 'checks': [],
                   'observations': {}, 'status': 'failed'}
        with tempfile.TemporaryDirectory() as temp, patch.object(guest, 'REPORTS', Path(temp)), \
             patch.object(guest, 'REPORT', fixture), patch.object(guest, 'RUN', 'fixture_run'):
            guest.write_report()
            summary = Path(temp) / 'report-summary.json'
            self.assertEqual(json.loads(summary.read_text())['status'], 'failed')
            self.assertEqual(summary.stat().st_mode & 0o777, 0o600)
            self.assertTrue((Path(temp) / 'fixture_run.json').is_file())

    def test_fingerprint_covers_nonpublic_rows_and_schema_definition(self):
        # TEST FIXTURE ONLY: query seam; all aggregation/hashing logic is real.
        def query(text, db):
            if 'pg_tables' in text:
                return json.dumps([{'schemaname': 'public', 'tablename': 'users'},
                                   {'schemaname': 'fixture_test', 'tablename': 'positive_amount'}])
            if 'count(*)' in text:
                return '1'
            return 'TEST FIXTURE row'
        dump = subprocess.CompletedProcess([], 0, 'TEST FIXTURE schema definition', '')
        with patch.object(guest, 'query', side_effect=query) as sql, \
             patch.object(guest, 'command', return_value=dump) as command:
            try:
                result = guest.fingerprint('fixture_db')
            except (AttributeError, TypeError) as error:
                self.fail('non-public schema fingerprint unsupported: ' + str(error))
        self.assertIn('schema_sha256', result)
        self.assertIn('fixture_test.positive_amount', result['tables'])
        self.assertTrue(any('"fixture_test"."positive_amount"' in c.args[0] for c in sql.call_args_list))
        self.assertTrue(any('--schema-only' in c.args[0] for c in command.call_args_list))

