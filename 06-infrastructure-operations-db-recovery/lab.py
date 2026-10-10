#!/usr/bin/env python3
"""Small stdlib host CLI, permanently bound to ops-db-lab (no host service/firewall edits)."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile
import time
import uuid
import inspect
from recovery_policy import validate_source, validate_report, validate_installation

ROOT = Path(__file__).resolve().parent
VM = 'ops-db-lab'
EVIDENCE = ROOT / 'evidence'


def call(args, timeout=900):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def checked(args, timeout=900):
    r = call(args, timeout)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f'{args[0]} exit={r.returncode}')
    return r.stdout


def vm_list():
    data = json.loads(checked(['multipass', 'list', '--format', 'json'], 60))
    return next((v for v in data['list'] if v['name'] == VM), None)


def exec_guest(*args):
    return ['multipass', 'exec', VM, '--', *args]


def record(action, result):
    EVIDENCE.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
    (EVIDENCE / f'{timestamp}-{action}.log').write_text(
        f'action={action}\nexit_code={result.returncode}\n' + result.stdout + result.stderr)
    print(result.stdout.strip())
    if result.returncode:
        print(result.stderr.strip(), file=sys.stderr)
        raise RuntimeError(f'{action} failed; log retained')


PACKAGE = '/home/ubuntu/ops-db-package'
PACKAGE_FILES = ('bootstrap.py', 'guest_test.py', 'recovery_policy.py', 'assets/SOURCE.json', 'assets/forum-api.tar.gz')
PACKAGE_PROBE = '''from pathlib import Path
import hashlib,json,sys
p=Path(sys.argv[1]); expected=json.loads(sys.argv[2])
if p.is_symlink(): print('symlink')
elif not p.exists(): print('absent')
elif not p.is_dir(): print('partial')
else:
    valid=all((p/n).is_file() and not (p/n).is_symlink() and
              hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in expected.items())
    actual={str(n.relative_to(p)) for n in p.rglob('*') if not n.is_dir()}
    valid=valid and actual==set(expected) and not any(n.is_symlink() for n in p.rglob('*'))
    print('matching' if valid else 'unmarked-or-partial')
'''


def upload():
    validate_source(ROOT / 'assets/forum-api.tar.gz', json.loads((ROOT / 'assets/SOURCE.json').read_text()))
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PACKAGE_FILES}
    state = checked(exec_guest('python3', '-c', PACKAGE_PROBE, PACKAGE, json.dumps(hashes))).strip()
    if state == 'matching':
        return
    if state != 'absent':
        raise RuntimeError('existing package is unrelated/partial; refuse overwrite')
    with tempfile.TemporaryDirectory() as directory:
        bundle = Path(directory) / 'ops-db-package'
        for name in ('bootstrap.py', 'guest_test.py', 'recovery_policy.py', 'assets/SOURCE.json', 'assets/forum-api.tar.gz'):
            destination = bundle / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        checked(['multipass', 'transfer', '--recursive', str(bundle), VM + ':/home/ubuntu/'])


# Ship the trusted host validator as source; never import guest-writable Python as root.
INSTALL_PROBE = inspect.getsource(validate_source) + '\n' + inspect.getsource(validate_installation) + '''\nfrom pathlib import Path
import json,sys,subprocess
root=Path('/opt/ops-db-lab'); marker=root/'INSTALL.json'
expected=json.loads(sys.argv[1])
paths=[root,Path('/etc/ops-db-lab'),Path('/var/lib/ops-db-lab'),
       Path('/var/backups/ops-db-lab'),Path('/etc/systemd/system/forum-api-lab.service')]
if marker.is_file() and not marker.is_symlink() and not root.is_symlink():
    try:
        data=json.loads(marker.read_text())
        valid=all(data.get(k)==expected[k] for k in ('commit','sha256'))
        valid=valid and Path('/etc/ops-db-lab/service.env').is_file()
        bundle=Path('/home/ubuntu/ops-db-package')
        validate_installation(root/'forum-api',bundle/'assets/forum-api.tar.gz',expected)
        print('matching' if valid else 'partial')
    except (ValueError,OSError): print('partial')
elif any(p.exists() or p.is_symlink() for p in paths): print('unmarked')
elif subprocess.run(['id','forumops'],capture_output=True).returncode==0: print('unmarked')
else: print('pristine')
'''


def up():
    vm = vm_list()
    if vm is None:
        # Exactly one isolated small Ubuntu guest. No resume/start of any other VM.
        record('launch', call(['multipass', 'launch', '24.04', '--name', VM, '--cpus', '2', '--memory', '1G', '--disk', '8G'], 1200))
    elif vm['release'] != 'Ubuntu 24.04 LTS':
        raise RuntimeError('existing fixed-name VM is not Ubuntu24.04; refuse replacement')
    elif vm['state'] == 'Stopped':
        checked(['multipass', 'start', VM])
    elif vm['state'] not in ('Running', 'Starting'):
        raise RuntimeError('existing VM state not safe to use')
    # Finite readiness wait; no blind launch replacement or open-ended parent polling.
    for _ in range(40):
        result = call(exec_guest('true'), 15)
        if result.returncode == 0:
            break
        time.sleep(3)
    else:
        raise RuntimeError('isolated guest readiness timeout')
    metadata = json.loads((ROOT / 'assets/SOURCE.json').read_text())
    state = checked(exec_guest('sudo', 'python3', '-c', INSTALL_PROBE, json.dumps(metadata))).strip()
    if state not in ('pristine', 'matching'):
        raise RuntimeError('unmarked/partial guest installation; refuse overwrite')
    upload()
    record('up', call(exec_guest('sudo', 'python3', '-B', PACKAGE + '/bootstrap.py'), 1800))
    for _ in range(30):
        result = call(exec_guest('curl', '--fail', '--silent', 'http://localhost:5050/'), 15)
        if result.returncode == 0:
            print('HTTP ready (not DB-aware; run test for DB validation).')
            return
        time.sleep(0.5)
    raise RuntimeError('HTTP readiness failed after provision')


def test():
    unit = call([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-p', 'test*.py', '-v'])
    record('safety-tests', unit)
    vm = vm_list()
    if not vm or vm['state'] != 'Running':
        raise RuntimeError('ops-db-lab is not running; use up first')
    upload()
    expected_run_id = uuid.uuid4().hex
    result = call(exec_guest('sudo', 'python3', '-B', PACKAGE + '/guest_test.py', expected_run_id), 900)
    # Fixed root-owned sanitized summary; never trust stdout as a path source.
    raw = checked(exec_guest('sudo', 'python3', '-c',
        'from pathlib import Path; import sys; print(Path(sys.argv[1]).read_text())',
        '/var/lib/ops-db-lab/evidence/report-summary.json'))
    report = validate_report(json.loads(raw))
    if report['run_id'] != expected_run_id:
        raise RuntimeError('guest report run_id is not fresh for this invocation; refuse publication')
    if (report['status'] == 'passed') != (result.returncode == 0):
        raise RuntimeError('guest report status is inconsistent with guest exit code; refuse publication')
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / ('integration-' + report['run_id'] + '.json')).write_text(raw)
    (EVIDENCE / 'report-summary.json').write_text(raw)
    record('integration', result)
    if report['status'] != 'passed':
        raise RuntimeError('missing or failing guest evidence')


def status():
    vm = vm_list()
    output = {'vm': vm}
    if vm and vm['state'] == 'Running':
        for name, args in [('systemd', ('systemctl', 'is-active', 'forum-api-lab.service')),
                           ('http', ('curl', '--fail', '--silent', 'http://localhost:5050/')),
                           ('postgres', ('pg_isready', '-h', '127.0.0.1'))]:
            result = call(exec_guest(*args), 30)
            output[name] = {'exit_code': result.returncode, 'output': result.stdout.strip()}
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('up', 'test', 'status', 'stop'))
    action = parser.parse_args().action
    try:
        if action == 'stop':
            # Explicit opt-in command only; never delete guest or databases.
            record('stop', call(['multipass', 'stop', VM]))
        else:
            globals()[action]()
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
