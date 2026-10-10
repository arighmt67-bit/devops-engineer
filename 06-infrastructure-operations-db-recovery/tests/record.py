"""Record actual unittest traces, return codes and interpreter at each TDD step."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
phase, testcase = sys.argv[1:]
r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_safety.py', '-v'],
                   cwd=root, capture_output=True, text=True)
folder = root / 'evidence' / 'tdd'
folder.mkdir(parents=True, exist_ok=True)
path = folder / f'{testcase}-{phase}.json'
path.write_text(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'cwd': str(root), 'command': [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_safety.py', '-v'],
    'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}, indent=2) + '\n')
print(f'{path.name}: exit={r.returncode}\n{r.stderr}')
sys.exit(r.returncode)
