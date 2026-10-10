"""Offline TEST FIXTURE ONLY: real pinned archive extracted into temporary files."""
import ast
import contextlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import recovery_policy as policy


BUNDLE = Path(__file__).resolve().parents[1]
ARCHIVE = BUNDLE / 'assets/forum-api.tar.gz'
METADATA = json.loads((BUNDLE / 'assets/SOURCE.json').read_text())


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Canonical fixture parent avoids the macOS system /var -> /private/var alias.
        self.base = Path(self.temp.name).resolve()
        self.app = self.base / 'forum-api'
        self.app.mkdir()
        policy.validate_source(ARCHIVE, METADATA)
        with tarfile.open(ARCHIVE) as tar:
            # The fixed archive is validated above; compatible with older local Python.
            tar.extractall(self.app)

    def validate(self, app=None, metadata=None):
        self.assertTrue(hasattr(policy, 'validate_installation'),
                        'installed pinned-source integrity validator missing')
        return policy.validate_installation(self.app if app is None else app,
                                            ARCHIVE, METADATA if metadata is None else metadata)

    def tracked_examples(self):
        return [self.app / 'src/app.js', self.app / 'package.json',
                self.app / 'package-lock.json',
                next(path for path in (self.app / 'migrations').iterdir() if path.is_file())]

    def test_installation_accepts_archive_fixture_with_runtime_node_modules(self):
        runtime = self.app / 'node_modules/TEST_FIXTURE_ONLY'
        runtime.mkdir(parents=True)
        (runtime / 'index.js').write_text('// TEST FIXTURE ONLY: npm runtime extra\n')
        self.assertEqual(self.validate(), self.app)

    def test_installation_rejects_modified_tracked_contents(self):
        for path in self.tracked_examples():
            with self.subTest(path=str(path.relative_to(self.app))):
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b'\n// TEST FIXTURE ONLY: mutation\n')
                    with self.assertRaises(ValueError):
                        self.validate()
                finally:
                    path.write_bytes(original)

    def test_installation_rejects_missing_tracked_files_or_directories(self):
        for path in self.tracked_examples() + [self.app / 'src', self.app / 'migrations']:
            with self.subTest(path=str(path.relative_to(self.app))):
                saved = self.base / 'TEST_FIXTURE_ONLY_saved'
                path.rename(saved)
                try:
                    with self.assertRaises(ValueError):
                        self.validate()
                finally:
                    saved.rename(path)

    def test_installation_validates_source_before_inspecting_installation(self):
        for changes, message in [({'commit': 'not-the-pin'}, 'source commit'),
                                 ({'sha256': '0' * 64}, 'source SHA256')]:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, message):
                    self.validate(self.base / 'missing', dict(METADATA, **changes))

    def test_installation_rejects_noncanonical_pinned_tree_symlinks(self):
        paths = self.tracked_examples() + [self.app / 'src', self.app / 'migrations',
                                          self.app / 'src/Applications', self.app]
        for path in paths:
            with self.subTest(path=str(path.relative_to(self.app))):
                saved = self.base / 'TEST_FIXTURE_ONLY_saved'
                path.rename(saved)
                path.symlink_to(saved, target_is_directory=saved.is_dir())
                try:
                    with self.assertRaises(ValueError):
                        self.validate()
                finally:
                    path.unlink()
                    saved.rename(path)
        ancestor = self.base / 'TEST_FIXTURE_ONLY_linked_ancestor'
        ancestor.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.validate(ancestor / 'forum-api')

    def test_installation_rejects_noncanonical_pinned_tree_extra_entries(self):
        for relative, directory in [('src/TEST_FIXTURE_ONLY_added.js', False),
                                    ('src/Applications/TEST_FIXTURE_ONLY_empty', True),
                                    ('migrations/TEST_FIXTURE_ONLY_added.js', False),
                                    ('TEST_FIXTURE_ONLY_added.js', False)]:
            with self.subTest(path=relative):
                path = self.app / relative
                if directory:
                    path.mkdir()
                else:
                    path.write_text('// TEST FIXTURE ONLY: untracked source\n')
                try:
                    with self.assertRaises(ValueError):
                        self.validate()
                finally:
                    path.rmdir() if directory else path.unlink()

    def bootstrap_matching_branch(self):
        # Execute the actual matching branch only; no root guard, apt, service, or VM effects.
        tree = ast.parse((BUNDLE / 'bootstrap.py').read_text())
        imports = [node for node in tree.body
                   if isinstance(node, ast.ImportFrom) and node.module == 'recovery_policy']
        branch = next(node for node in tree.body if isinstance(node, ast.If)
                      and ast.unparse(node.test) == 'MARKER.exists()')
        marker = self.base / 'INSTALL.json'
        marker.write_text(json.dumps(METADATA))
        calls = []
        namespace = {'ROOT': self.base, 'MARKER': marker, 'archive': ARCHIVE,
                     'metadata': METADATA, 'json': json,
                     'run': lambda args: calls.append(args)}  # TEST FIXTURE ONLY service boundary.
        exec(compile(ast.Module(body=imports, type_ignores=[]), 'bootstrap.py', 'exec'), namespace)
        return branch, namespace, calls

    def test_installation_bootstrap_rejects_mutation_before_unchanged_claim(self):
        (self.app / 'src/app.js').write_text('// TEST FIXTURE ONLY: modified installed app\n')
        branch, namespace, calls = self.bootstrap_matching_branch()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(ValueError):
            exec(compile(ast.Module(body=[branch], type_ignores=[]), 'bootstrap.py', 'exec'), namespace)
        self.assertEqual(calls, [])
        self.assertEqual(output.getvalue(), '')

    def test_installation_bootstrap_accepts_exact_archive_fixture(self):
        branch, namespace, calls = self.bootstrap_matching_branch()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as caught:
            exec(compile(ast.Module(body=[branch], type_ignores=[]), 'bootstrap.py', 'exec'), namespace)
        self.assertEqual(caught.exception.code, 0)
        self.assertIn('unchanged', output.getvalue())
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
