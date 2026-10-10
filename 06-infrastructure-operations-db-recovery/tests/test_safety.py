import hashlib
import json
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
import recovery_policy as policy


class SafetyTests(unittest.TestCase):
    def test_restore_name_is_strict_new_namespace(self):
        self.assertEqual(policy.validate_target('opslab_restore_abc123'), 'opslab_restore_abc123')
        for value in ('opslab_forum', 'postgres', 'opslab_restore_', 'opslab_restore_A',
                      'opslab_restore_x; DROP TABLE users', 'opslab_restore_' + 'a' * 50):
            with self.subTest(value=value), self.assertRaises(ValueError):
                policy.validate_target(value)

    def test_preexisting_restore_target_is_refused(self):
        with self.assertRaises(ValueError):
            policy.validate_target('opslab_restore_existing', ['opslab_restore_existing'])

    def test_archive_must_resolve_inside_backup_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'backups'
            root.mkdir()
            good = root / 'good.dump'
            good.write_bytes(b'TEST FIXTURE')
            outside = base / 'outside.dump'
            outside.write_bytes(b'TEST FIXTURE')
            link = root / 'escape.dump'
            link.symlink_to(outside)
            digest = hashlib.sha256(good.read_bytes()).hexdigest()
            self.assertEqual(policy.validate_archive(good, root, digest), good.resolve())
            for value in (outside, link, root):
                with self.subTest(value=str(value)), self.assertRaises(ValueError):
                    policy.validate_archive(value, root, digest)

    def test_tampered_hash_refused_before_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'test.dump'
            archive.write_bytes(b'TEST FIXTURE')
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            policy.validate_archive(archive, directory, digest)
            archive.write_bytes(b'TAMPERED TEST FIXTURE')
            with self.assertRaises(ValueError):
                policy.validate_archive(archive, directory, digest)

    def test_source_pin_and_hash_are_both_required(self):
        root = Path(__file__).resolve().parents[1]
        archive = root / 'assets/forum-api.tar.gz'
        metadata = json.loads((root / 'assets/SOURCE.json').read_text())
        policy.validate_source(archive, metadata)
        for altered in (dict(metadata, commit='0' * 40), dict(metadata, sha256='0' * 64)):
            with self.subTest(metadata=altered), self.assertRaises(ValueError):
                policy.validate_source(archive, altered)

    def test_snapshot_members_cannot_escape_or_ship_extra_files(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, linked in (('../escape', False), ('src/../../escape', False),
                                 ('.env', False), ('src/link', True)):
                archive = Path(directory) / 'unsafe.tar.gz'
                with tarfile.open(archive, 'w:gz') as tar:
                    member = tarfile.TarInfo(name)
                    if linked:
                        member.type = tarfile.SYMTYPE
                        member.linkname = '/etc/passwd'
                        tar.addfile(member)
                    else:
                        member.size = 1
                        tar.addfile(member, io.BytesIO(b'x'))
                metadata = {'commit': '040a9bef5aa857b0251bf41a805dd75fc91f44ab',
                            'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
                with self.subTest(name=name), self.assertRaises(ValueError):
                    policy.validate_source(archive, metadata)
