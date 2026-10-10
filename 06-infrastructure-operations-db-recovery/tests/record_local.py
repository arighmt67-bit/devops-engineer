"""Save actual offline TDD execution; never overwrite prior evidence."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
phase, label, *selection = sys.argv[1:]
args = [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']
if selection:
    args += ['-k', selection[0]]
result = subprocess.run(args, cwd=root, capture_output=True, text=True)
path = root / 'evidence/tdd' / (label + '-' + phase + '.json')
with path.open('x') as stream:
    json.dump({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'cwd': str(root), 'command': args, 'interpreter': sys.executable,
               'exit_code': result.returncode, 'stdout': result.stdout,
               'stderr': result.stderr}, stream, indent=2)
    stream.write('\n')
print(path.name + ': exit=' + str(result.returncode))
print(result.stderr)
sys.exit(result.returncode)

# All mocked guest/subprocess responses in tests are labeled TEST FIXTURE ONLY.
