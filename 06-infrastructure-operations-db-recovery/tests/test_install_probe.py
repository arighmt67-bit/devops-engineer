"""TEST FIXTURE ONLY: execute actual installation probe against temporary files."""
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
import lab


class InstallationProbeTests(unittest.TestCase):
    def test_matching_marker_does_not_hide_installed_source_mutation(self):
        metadata = json.loads((lab.ROOT / 'assets/SOURCE.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            # macOS /var is a system symlink; keep fixture root canonical.
            base = Path(temp).resolve()
            root = base / 'opt'
            app = root / 'forum-api'
            app.mkdir(parents=True)
            with tarfile.open(lab.ROOT / 'assets/forum-api.tar.gz') as archive:
                archive.extractall(app)
            (root / 'INSTALL.json').write_text(json.dumps(metadata))
            config = base / 'etc'
            config.mkdir()
            (config / 'service.env').write_text('TEST FIXTURE ONLY')
            # The guest package is data, not trusted root-executable Python.
            bundle = base / 'package'
            (bundle / 'assets').mkdir(parents=True)
            for name in ('forum-api.tar.gz', 'SOURCE.json'):
                (bundle / 'assets' / name).write_bytes((lab.ROOT / 'assets' / name).read_bytes())
            (bundle / 'recovery_policy.py').write_text('raise RuntimeError("TEST FIXTURE ONLY: untrusted guest module executed")')
            probe = lab.INSTALL_PROBE.replace('/opt/ops-db-lab', str(root)).replace('/etc/ops-db-lab', str(config)).replace('/home/ubuntu/ops-db-package', str(bundle))
            def classify():
                result = subprocess.run([sys.executable, '-c', probe, json.dumps(metadata)],
                                        cwd=lab.ROOT, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()
            self.assertEqual(classify(), 'matching')
            (app / 'src/app.js').write_text('// TEST FIXTURE tampered app')
            self.assertEqual(classify(), 'partial')
