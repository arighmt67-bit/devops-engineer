"""Ubuntu-only bootstrap; refuse unrelated or partially installed resources."""
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import subprocess
import tarfile
import urllib.request
from recovery_policy import validate_source, validate_installation

ROOT = Path('/opt/ops-db-lab')
BUNDLE = Path(__file__).resolve().parent
MARKER = ROOT / 'INSTALL.json'
PIN = '040a9bef5aa857b0251bf41a805dd75fc91f44ab'


def run(args, **kwargs):
    r = subprocess.run(args, capture_output=True, text=True, timeout=600, **kwargs)
    if r.returncode:
        # npm/apt messages do not include environment; do not print privileged SQL.
        if args[0] in ('apt-get',) or 'npm' in str(args):
            print(r.stdout[-4000:] + r.stderr[-4000:])
        raise RuntimeError(f'{args[0]} failed exit={r.returncode}')
    return r.stdout.strip()


def psql(text, db='postgres'):
    return run(['runuser', '-u', 'postgres', '--', 'psql', '-XAt', '-v', 'ON_ERROR_STOP=1', '-d', db], input=text)


if os.geteuid() != 0 or 'Ubuntu' not in Path('/etc/os-release').read_text():
    raise SystemExit('requires root in isolated Ubuntu ops-db-lab guest')
metadata = json.loads((BUNDLE / 'assets/SOURCE.json').read_text())
archive = BUNDLE / 'assets/forum-api.tar.gz'
validate_source(archive, metadata)

if MARKER.exists():
    if json.loads(MARKER.read_text()).get('sha256') != metadata['sha256']:
        raise SystemExit('existing lab snapshot differs: refusing replacement')
    validate_installation(ROOT / 'forum-api', archive, metadata)
    run(['systemctl', 'is-active', 'postgresql'])
    run(['systemctl', 'is-active', 'forum-api-lab.service'])
    print('Existing matching installation verified; unchanged.')
    raise SystemExit(0)
if ROOT.exists() or Path('/etc/ops-db-lab').exists():
    raise SystemExit('unmarked installation path exists: refuse overwrite')
if subprocess.run(['id', 'forumops'], capture_output=True).returncode == 0:
    raise SystemExit('preexisting forumops user: refuse unrelated installation')
run(['apt-get', 'update'])
run(['apt-get', 'install', '-y', 'postgresql', 'build-essential', 'python3', 'curl', 'xz-utils', 'iptables'],
    env=dict(os.environ, DEBIAN_FRONTEND='noninteractive'))
run(['systemctl', 'start', 'postgresql'])
conflicts = psql("SELECT rolname FROM pg_roles WHERE rolname IN ('opslab_owner','opslab_app','opslab_reader'); SELECT datname FROM pg_database WHERE datname='opslab_forum';")
if conflicts:
    raise SystemExit('preexisting lab database/role: refuse overwrite')
run(['useradd', '--system', '--create-home', '--home-dir', '/var/lib/forumops', '--shell', '/usr/sbin/nologin', 'forumops'])
ROOT.mkdir(mode=0o755)
arch = {'aarch64': 'arm64', 'x86_64': 'x64'}.get(platform.machine())
if not arch:
    raise SystemExit('unsupported node architecture')
node_name = f'node-v22.23.3-linux-{arch}'
base = 'https://nodejs.org/dist/v22.23.3/'
with urllib.request.urlopen(base + 'SHASUMS256.txt', timeout=60) as r:
    checksums = r.read().decode()
node_tar = ROOT / (node_name + '.tar.xz')
with urllib.request.urlopen(base + node_tar.name, timeout=60) as r, open(node_tar, 'wb') as stream:
    shutil.copyfileobj(r, stream)
expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1] == node_tar.name)
actual = hashlib.sha256(node_tar.read_bytes()).hexdigest()
if expected != actual or (arch == 'arm64' and actual != 'a44aeb94849a299b22df10b9e622ec2f605c2183501bc40590705131de7c740f'):
    raise SystemExit('official Node SHA256 mismatch')
run(['tar', '-xJf', str(node_tar), '-C', str(ROOT)])
(ROOT / 'node').symlink_to(node_name)
app = ROOT / 'forum-api'
app.mkdir()
run(['tar', '-xzf', str(archive), '-C', str(app)])
node_bin = str(ROOT / 'node/bin')
build_env = dict(os.environ, PATH=node_bin + ':' + os.environ['PATH'], npm_config_cache='/var/lib/forumops/.npm')
run(['chown', '-R', 'forumops:forumops', str(app)])
run(['runuser', '-u', 'forumops', '--', str(ROOT / 'node/bin/npm'), 'ci', '--omit=dev'], cwd=app, env=build_env)
config_dir = Path('/etc/ops-db-lab')
config_dir.mkdir(mode=0o750)
run(['chown', 'root:forumops', str(config_dir)])
cfg = {'NODE_ENV': 'development', 'PORT': '5050', 'PGHOST': '127.0.0.1', 'PGPORT': '5432',
       'PGUSER': 'opslab_app', 'PGPASSWORD': secrets.token_hex(24), 'PGDATABASE': 'opslab_forum',
       'ACCESS_TOKEN_KEY': secrets.token_hex(32), 'REFRESH_TOKEN_KEY': secrets.token_hex(32),
       'ACCESS_TOKEN_AGE': '30m', 'READER_PASSWORD': secrets.token_hex(24)}
env_file = config_dir / 'service.env'
env_file.write_text(''.join(k + '=' + v + '\n' for k,v in cfg.items()))
env_file.chmod(0o640)
run(['chown', 'root:forumops', str(env_file)])
psql(f"CREATE ROLE opslab_owner NOLOGIN; CREATE ROLE opslab_app LOGIN PASSWORD '{cfg['PGPASSWORD']}'; CREATE ROLE opslab_reader LOGIN PASSWORD '{cfg['READER_PASSWORD']}'; CREATE DATABASE opslab_forum OWNER opslab_owner;")
psql('REVOKE ALL ON DATABASE opslab_forum FROM PUBLIC; GRANT CONNECT ON DATABASE opslab_forum TO opslab_app,opslab_reader;', 'postgres')
psql('REVOKE CREATE ON SCHEMA public FROM PUBLIC; GRANT USAGE,CREATE ON SCHEMA public TO opslab_app;', 'opslab_forum')
run(['runuser', '-u', 'forumops', '--', str(ROOT / 'node/bin/npm'), 'run', 'migrate', 'up'],
    cwd=app, env=dict(build_env, **cfg))
psql('REASSIGN OWNED BY opslab_app TO opslab_owner; REVOKE CREATE ON SCHEMA public FROM opslab_app; GRANT USAGE ON SCHEMA public TO opslab_app,opslab_reader; GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO opslab_app; GRANT SELECT ON ALL TABLES IN SCHEMA public TO opslab_reader; GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO opslab_app;', 'opslab_forum')
run(['chown', '-R', 'root:root', str(app)])
run(['chmod', '-R', 'a-w', str(app)])
backup = Path('/var/backups/ops-db-lab')
backup.mkdir(mode=0o700)
Path('/var/lib/ops-db-lab/evidence').mkdir(parents=True, mode=0o700)
unit = '''[Unit]
Description=Forum API Infrastructure Operations Lab
After=network.target postgresql.service
Requires=postgresql.service
[Service]
User=forumops
Group=forumops
WorkingDirectory=/opt/ops-db-lab/forum-api
EnvironmentFile=/etc/ops-db-lab/service.env
ExecStart=/opt/ops-db-lab/node/bin/node src/app.js
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadOnlyPaths=/opt/ops-db-lab/forum-api
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=
UMask=0077
[Install]
WantedBy=multi-user.target
'''
Path('/etc/systemd/system/forum-api-lab.service').write_text(unit)
run(['systemctl', 'daemon-reload'])
run(['systemctl', 'enable', '--now', 'forum-api-lab.service'])
metadata['node_sha256'] = actual
MARKER.write_text(json.dumps(metadata, indent=2) + '\n')
print('Bootstrap complete: pinned unchanged app, protected VM-only secrets, nonroot service.')
