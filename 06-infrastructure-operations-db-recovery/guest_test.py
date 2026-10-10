"""Real guest-only acceptance runner. Synthetic TEST FIXTURE data; no token output."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from recovery_policy import validate_archive, validate_target

SOURCE = 'opslab_forum'
SERVICE = 'forum-api-lab.service'
ENV = Path('/etc/ops-db-lab/service.env')
BACKUPS = Path('/var/backups/ops-db-lab')
REPORTS = Path('/var/lib/ops-db-lab/evidence')
RUN = time.strftime('%Y%m%d%H%M%S') + '_' + secrets.token_hex(3)
REPORT = {'run_id': RUN, 'fixture_label': 'TEST FIXTURE ONLY — synthetic forum / positive amount',
          'checks': [], 'observations': {}, 'status': 'running'}


def bind_run_id(value):
    import re
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9_]{1,40}', value):
        raise ValueError('unsafe host run_id')
    global RUN
    RUN = value
    REPORT['run_id'] = value


def command(args, *, input=None, env=None, check=True):
    result = subprocess.run(args, input=input, env=env, capture_output=True, text=True, timeout=120)
    if check and result.returncode:
        raise RuntimeError(f'command failed: {args[0]} (exit {result.returncode})')
    return result


def sql(query, db=SOURCE, role=None, stop=True):
    prefix = f'SET ROLE {role};\n' if role else ''
    return command(['runuser', '-u', 'postgres', '--', 'psql', '-X', '-A', '-t',
                    '-v', 'VERBOSITY=verbose', '-v', 'ON_ERROR_STOP=' + ('1' if stop else '0'), '-d', db],
                   input=prefix + query, check=False)


def query(q, db=SOURCE):
    r = sql(q, db)
    if r.returncode:
        raise RuntimeError('SQL query failed (details withheld)')
    return r.stdout.strip()


def check(name, condition, details=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'details': details})
    if not condition:
        raise AssertionError(name)


def http(path='/', payload=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request('http://localhost:5050' + path,
        data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())
    except urllib.error.URLError:
        return 0, {}


def restart():
    # This lab deliberately starts the same unit repeatedly in a short window.
    # Reset only this unit's limit; do not disable systemd crash-loop protection.
    command(['systemctl', 'reset-failed', SERVICE])
    command(['systemctl', 'restart', SERVICE])
    for _ in range(50):
        if http()[0] == 200:
            return
        time.sleep(0.2)
    raise RuntimeError('HTTP readiness timed out')


@contextmanager
def network_fault(rule):
    """Remove this run's exact rule even if insertion timed out; always restart."""
    try:
        command(['iptables', '-I'] + rule)
        yield
    finally:
        errors = []
        residual = None
        restored = False
        try:
            present = command(['iptables', '-C'] + rule, check=False)
            if present.returncode not in (0, 1):
                errors.append('rule_probe_inconclusive')
            if present.returncode != 1:
                removed = command(['iptables', '-D'] + rule, check=False)
                if removed.returncode:
                    errors.append('exact_rule_removal_failed')
        except Exception as error:
            errors.append('rule_removal_' + type(error).__name__)
            # A failed existence probe is inconclusive; still attempt exact deletion.
            try:
                command(['iptables', '-D'] + rule, check=False)
            except Exception as error:
                errors.append('fallback_removal_' + type(error).__name__)
        finally:
            try:
                remaining = command(['iptables', '-C'] + rule, check=False)
                residual = remaining.returncode == 0 if remaining.returncode in (0, 1) else None
                if residual is not False:
                    errors.append('rule_absence_not_verified')
            except Exception as error:
                errors.append('rule_verification_' + type(error).__name__)
            finally:
                try:
                    restart()
                    restored = True
                except Exception as error:
                    errors.append('service_restore_' + type(error).__name__)
                REPORT['observations']['network_cleanup'] = {
                    'residual_rule': residual, 'service_restored': restored, 'errors': errors}
        if errors:
            raise RuntimeError('network cleanup incomplete: ' + ','.join(errors))


def fingerprint(db):
    tables = json.loads(query("SELECT coalesce(json_agg(json_build_object('schemaname',schemaname,'tablename',tablename) ORDER BY schemaname,tablename),'[]') FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') AND schemaname NOT LIKE 'pg_toast%'", db))
    definition = command(['runuser', '-u', 'postgres', '--', 'pg_dump', '--schema-only',
                          '--no-owner', '--no-acl', db]).stdout
    # pg_dump random restriction keys and version comments are not schema content.
    definition = '\n'.join(line for line in definition.splitlines()
        if not line.startswith(('\\restrict ', '\\unrestrict ', '--')) and line.strip())
    result = {'schema_sha256': hashlib.sha256(definition.encode()).hexdigest(), 'tables': {}}
    for table in tables:
        schema, name = table['schemaname'], table['tablename']
        quoted = '.'.join('"' + part.replace('"', '""') + '"' for part in (schema, name))
        # Full rows stay in memory only. Password hashes NEVER appear in logs/JSON.
        rows = query(f'SELECT row_to_json(t)::text FROM {quoted} t ORDER BY row_to_json(t)::text COLLATE "C"', db)
        result['tables'][schema + '.' + name] = {'rows': int(query(f'SELECT count(*) FROM {quoted}', db)),
                                               'sha256': hashlib.sha256(rows.encode()).hexdigest()}
    return result


def restore(archive, expected_hash, target):
    validate_target(target, query('SELECT datname FROM pg_database').splitlines())
    archive = validate_archive(archive, BACKUPS, expected_hash)
    command(['runuser', '-u', 'postgres', '--', 'createdb', '--owner=opslab_owner', target])
    query(f'REVOKE ALL ON DATABASE {target} FROM PUBLIC; GRANT CONNECT ON DATABASE {target} TO opslab_app,opslab_reader;', 'postgres')
    # Protected root archive streamed via stdin; postgres cannot traverse backup root.
    with open(archive, 'rb') as stream:
        r = subprocess.run(['runuser', '-u', 'postgres', '--', 'pg_restore', '--exit-on-error',
            '--role=opslab_owner', '--no-owner', '--no-acl', '-d', target], stdin=stream,
            capture_output=True, timeout=120)
    if r.returncode:
        raise RuntimeError('pg_restore failed; new target retained for diagnosis')


def grant_restored_access(target):
    query('REVOKE CREATE ON SCHEMA public FROM PUBLIC; GRANT USAGE ON SCHEMA public TO opslab_app,opslab_reader; GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO opslab_app; GRANT SELECT ON ALL TABLES IN SCHEMA public TO opslab_reader; GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO opslab_app;', target)


def integration():
    cfg = dict(line.split('=', 1) for line in ENV.read_text().splitlines() if '=' in line)
    check('initial_source_configuration', cfg.get('PGDATABASE') == SOURCE)
    state = command(['systemctl', 'is-active', SERVICE]).stdout.strip()
    pid = command(['systemctl', 'show', SERVICE, '-p', 'MainPID', '--value']).stdout.strip()
    uid = Path('/proc/' + pid + '/status').read_text().split('Uid:\t')[1].splitlines()[0].split()[0]
    expected_uid = command(['id', '-u', 'forumops']).stdout.strip()
    check('systemd_active_nonroot', state == 'active' and uid == expected_uid and uid != '0', {'state': state, 'pid': pid, 'uid': uid})
    denied = command(['runuser', '-u', 'nobody', '--', 'test', '-r', str(ENV)], check=False)
    check('outsider_cannot_read_secrets', denied.returncode == 1,
          {'mode': oct(ENV.stat().st_mode & 0o777), 'returncode': denied.returncode})
    listeners = command(['ss', '-ltnp']).stdout
    app_listeners = [line for line in listeners.splitlines() if ':5050 ' in line]
    check('localhost_listener', bool(app_listeners) and all('127.0.0.1:5050' in x or '[::1]:5050' in x for x in app_listeners), app_listeners)
    resolution = sorted(set(item[4][0] for item in socket.getaddrinfo('localhost', 5432)))
    with socket.create_connection(('localhost', 5432), timeout=3):
        tcp_ok = True
    check('hostname_resolution_tcp', tcp_ok, {'localhost': resolution, 'port': 5432})

    username = 'fixture_' + RUN
    password = secrets.token_urlsafe(20)
    status, body = http('/users', {'username': username, 'password': password, 'fullname': 'TEST FIXTURE synthetic user'})
    check('api_register', status == 201, {'http_status': status})
    user_id = body['data']['addedUser']['id']
    status, body = http('/authentications', {'username': username, 'password': password})
    check('api_login', status == 201, {'http_status': status})
    token = body['data']['accessToken']
    title = 'TEST FIXTURE ' + RUN
    status, body = http('/threads', {'title': title, 'body': 'Synthetic recovery fixture, not financial data'}, token)
    check('api_create_thread', status == 201, {'http_status': status})
    thread_id = body['data']['addedThread']['id']
    path = '/threads/' + thread_id
    status, original = http(path)
    check('api_read_thread', status == 200 and original['data']['thread']['title'] == title
          and original['data']['thread']['username'] == username, {'http_status': status, 'thread_id': thread_id})

    failures = {
        'primary_key': (f"INSERT INTO users SELECT * FROM users WHERE id='{user_id}';", '23505'),
        'unique': (f"INSERT INTO users VALUES ('dup_{RUN}','{username}','TEST FIXTURE','TEST FIXTURE');", '23505'),
        'not_null': (f"INSERT INTO users VALUES ('null_{RUN}','null_{RUN}','TEST FIXTURE',NULL);", '23502'),
        'foreign_key': (f"INSERT INTO threads(id,title,body,owner,date) VALUES ('fk_{RUN}','TEST FIXTURE','TEST FIXTURE','missing_{RUN}',now());", '23503')}
    for name, (statement, code) in failures.items():
        r = sql(statement)
        check('constraint_' + name, r.returncode != 0 and code in r.stderr, {'sqlstate': code, 'exit_code': r.returncode})
    schema = 'fixture_' + RUN
    query(f'CREATE SCHEMA {schema} AUTHORIZATION opslab_owner; CREATE TABLE {schema}.positive_amount (id integer PRIMARY KEY, amount integer CHECK(amount>0));')
    r = sql(f'INSERT INTO {schema}.positive_amount VALUES (1,-1);')
    check('constraint_check_positive_fixture', r.returncode != 0 and '23514' in r.stderr,
          {'sqlstate': '23514', 'scope': schema + '.positive_amount TEST FIXTURE'})
    query(f'BEGIN; INSERT INTO {schema}.positive_amount VALUES(1,10); COMMIT; BEGIN; INSERT INTO {schema}.positive_amount VALUES(2,20); ROLLBACK;')
    check('commit_rollback', query(f'SELECT id FROM {schema}.positive_amount ORDER BY id') == '1')
    r = sql(f'BEGIN; INSERT INTO {schema}.positive_amount VALUES(3,30); INSERT INTO {schema}.positive_amount VALUES(1,40); INSERT INTO {schema}.positive_amount VALUES(4,40); COMMIT;', stop=False)
    check('failed_transaction_no_partial_records', '23505' in r.stderr and '25P02' in r.stderr
          and query(f'SELECT id FROM {schema}.positive_amount ORDER BY id') == '1',
          {'sqlstates': ['23505', '25P02'], 'psql_exit': r.returncode, 'transaction_result': r.stdout.strip()})
    r = sql(f'CREATE TABLE public.forbidden_{RUN}(id int);', role='opslab_app')
    check('app_cannot_create_table', r.returncode != 0 and '42501' in r.stderr, {'sqlstate': '42501'})
    reader_env = dict(os.environ, PGHOST='127.0.0.1', PGPORT='5432', PGDATABASE=SOURCE,
                      PGUSER='opslab_reader', PGPASSWORD=cfg['READER_PASSWORD'])
    r = command(['psql', '-XAt', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose', '-c',
                 f"SELECT count(*) FROM threads WHERE id='{thread_id}'"], env=reader_env)
    check('readonly_select', r.stdout.strip() == '1', {'rows': int(r.stdout.strip())})
    r = command(['psql', '-XAt', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose', '-c',
                 f"UPDATE threads SET title='TEST FIXTURE forbidden' WHERE id='{thread_id}'"], env=reader_env, check=False)
    check('readonly_update_denied', r.returncode != 0 and '42501' in r.stderr, {'sqlstate': '42501'})
    joined = json.loads(query(f"SELECT json_build_object('username',u.username,'threads',count(t.id)) FROM users u JOIN threads t ON t.owner=u.id WHERE u.id='{user_id}' GROUP BY u.username"))
    check('sql_join_aggregate', joined == {'username': username, 'threads': 1}, joined)
    benchmark = sql('CREATE TEMP TABLE index_fixture AS SELECT i AS id, md5(i::text) AS payload FROM generate_series(1,50000) i; ANALYZE index_fixture; EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM index_fixture WHERE id=49999; CREATE INDEX ON index_fixture(id); EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM index_fixture WHERE id=49999;')
    check('index_benchmark', benchmark.returncode == 0 and 'Seq Scan' in benchmark.stdout and 'Index Scan' in benchmark.stdout)
    REPORT['observations']['index_benchmark'] = {'label': 'TEST FIXTURE temporary 50000 rows, no universal speedup claim', 'actual_psql_output': benchmark.stdout}

    wrong_env = dict(reader_env, PGUSER='opslab_app', PGPASSWORD=secrets.token_urlsafe(16), PGCONNECT_TIMEOUT='3')
    wrong = command(['runuser', '-u', 'forumops', '--', 'psql', '-XAt', '-c', 'SELECT 1'], env=wrong_env, check=False)
    check('wrong_password_authentication_error', wrong.returncode != 0 and 'password authentication failed' in wrong.stderr,
          {'exit_code': wrong.returncode, 'diagnosis': wrong.stderr.strip()})
    rule = ['OUTPUT', '-p', 'tcp', '--dport', '5432', '-m', 'owner', '--uid-owner', 'forumops',
            '-m', 'comment', '--comment', 'ops-db-lab-' + RUN, '-j', 'REJECT', '--reject-with', 'tcp-reset']
    with network_fault(rule):
        restart()  # clear pooled connections
        root_status = http()[0]
        thread_status = http(path)[0]
        ready = command(['pg_isready', '-h', '127.0.0.1'], check=False)
        blocked_env = dict(wrong_env, PGPASSWORD=cfg['PGPASSWORD'])
        blocked = command(['runuser', '-u', 'forumops', '--', 'psql', '-XAt', '-c', 'SELECT 1'], env=blocked_env, check=False)
        diagnosis = command(['iptables', '-S', 'OUTPUT']).stdout
        check('http_health_not_db_readiness', root_status == 200 and thread_status == 500 and ready.returncode == 0,
              {'root_http': root_status, 'thread_http': thread_status, 'pg_isready': ready.stdout.strip(),
               'iptables': diagnosis.strip(), 'systemd': command(['systemctl', 'is-active', SERVICE]).stdout.strip()})
        check('network_refused_not_password_error', blocked.returncode != 0 and 'Connection refused' in blocked.stderr,
              {'exit_code': blocked.returncode, 'diagnosis': blocked.stderr.strip()})
    check('network_fault_recovered', http(path)[0] == 200)
    try:
        command(['systemctl', 'stop', SERVICE])
        inactive = command(['systemctl', 'is-active', SERVICE], check=False).stdout.strip()
        check('service_stop_http_unavailable', inactive == 'inactive' and http()[0] == 0,
              {'systemd': inactive, 'http_status': 0})
        journal = command(['journalctl', '-u', SERVICE, '-n', '40', '--no-pager', '-o', 'short-iso']).stdout
        # App exception stack only; app does not print tokens/passwords. Still exclude body/request lines.
        REPORT['observations']['journal'] = '\n'.join(x for x in journal.splitlines()
            if 'systemd[' in x or 'ECONNREFUSED' in x or 'port: 5432' in x or 'address:' in x)
    finally:
        restart()
    check('service_restart_thread_restored', http(path)[0] == 200)

    directory = BACKUPS / RUN
    directory.mkdir(mode=0o700)
    archive = directory / 'forum.dump'
    # Quiesce API writes while dump + source fingerprints are captured.
    started = time.monotonic()
    try:
        command(['systemctl', 'stop', SERVICE])
        with open(archive, 'xb') as stream:
            r = subprocess.run(['runuser', '-u', 'postgres', '--', 'pg_dump', '--format=custom',
                '--no-owner', '--no-acl', SOURCE], stdout=stream, stderr=subprocess.PIPE, timeout=120)
        if r.returncode:
            raise RuntimeError('pg_dump failed')
        archive.chmod(0o600)
        original_fingerprints = fingerprint(SOURCE)
    finally:
        restart()
    backup_seconds = time.monotonic() - started
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest = {'source': SOURCE, 'archive': archive.name, 'sha256': digest, 'tables': original_fingerprints}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    (directory / 'manifest.json').chmod(0o600)
    target = 'opslab_restore_' + RUN
    before = query('SELECT datname FROM pg_database').splitlines()
    negative = []
    for name, candidate, expected in [('source', SOURCE, digest), ('invalid', 'invalid;name', digest),
        ('tampered_hash', target, '0' * 64)]:
        try:
            restore(archive, expected, candidate)
        except ValueError:
            negative.append(name)
        else:
            raise AssertionError('unsafe restore accepted: ' + name)
    outside = Path('/var/lib/ops-db-lab/outside.dump')
    outside.write_bytes(b'TEST FIXTURE invalid outside archive')
    try:
        restore(outside, hashlib.sha256(outside.read_bytes()).hexdigest(), target)
    except ValueError:
        negative.append('outside_root')
    else:
        raise AssertionError('outside root accepted')
    check('restore_gates_before_createdb', query('SELECT datname FROM pg_database').splitlines() == before,
          {'rejections': negative, 'target_not_created': target not in before})
    started = time.monotonic()
    restore(archive, digest, target)
    restore_seconds = time.monotonic() - started
    started = time.monotonic()
    restored_fingerprints = fingerprint(target)
    check('restore_all_non_system_rows_and_schema', original_fingerprints == restored_fingerprints,
          {'source': original_fingerprints, 'restored': restored_fingerprints})
    verify_seconds = time.monotonic() - started
    r = sql(f"SELECT count(*) FROM threads t LEFT JOIN users u ON u.id=t.owner WHERE u.id IS NULL", target)
    check('restored_relationships', r.returncode == 0 and r.stdout.strip() == '0')
    # Restore archive intentionally has no ACLs; explicitly grant runtime role in ONLY target.
    grant_restored_access(target)
    inventory = query('SELECT datname FROM pg_database').splitlines()
    try:
        restore(archive, digest, target)
    except ValueError as error:
        check('existing_valid_restore_target_refused', 'already exists' in str(error)
              and query('SELECT datname FROM pg_database').splitlines() == inventory
              and fingerprint(target) == restored_fingerprints)
    else:
        raise AssertionError('preexisting target overwritten')
    for role in ('opslab_app', 'opslab_reader'):
        for kind, statement in [('public', f'CREATE TABLE public.forbidden_{RUN}(id int);'),
                                ('temp', 'CREATE TEMP TABLE forbidden_fixture(id int);')]:
            denied = sql(statement, target, role=role)
            check('restored_' + role + '_' + kind + '_ddl_denied', denied.returncode != 0 and '42501' in denied.stderr)
    selected = sql(f"SELECT count(*) FROM threads WHERE id='{thread_id}';", target, role='opslab_reader')
    check('restored_reader_select', selected.returncode == 0 and selected.stdout.strip().endswith('1'))
    denied = sql('UPDATE threads SET title=title WHERE false;', target, role='opslab_reader')
    check('restored_reader_update_denied', denied.returncode != 0 and '42501' in denied.stderr)
    original_env = ENV.read_text()
    try:
        ENV.write_text(original_env.replace('PGDATABASE=' + SOURCE, 'PGDATABASE=' + target))
        restart()
        status, restored_thread = http(path)
        check('app_reads_restored_database', status == 200 and restored_thread == original,
              {'http_status': status, 'database': target})
        check('app_connection_really_uses_restore', int(query(f"SELECT count(*) FROM pg_stat_activity WHERE usename='opslab_app' AND datname='{target}'", 'postgres')) > 0)
    finally:
        ENV.write_text(original_env)
        restart()
    check('source_configuration_reverted', 'PGDATABASE=' + SOURCE in ENV.read_text() and http(path)[0] == 200)
    check('app_connection_really_returns_to_source', int(query(f"SELECT count(*) FROM pg_stat_activity WHERE usename='opslab_app' AND datname='{SOURCE}'", 'postgres')) > 0)
    REPORT['observations']['recovery'] = {'source': SOURCE, 'target': target, 'sha256': digest,
        'backup_seconds': round(backup_seconds, 6), 'restore_seconds': round(restore_seconds, 6),
        'verify_seconds': round(verify_seconds, 6), 'scope': 'lab recovery observations only; not production RTO/RPO',
        'backup_root_mode': oct(BACKUPS.stat().st_mode & 0o777)}


def write_report():
    REPORTS.mkdir(parents=True, exist_ok=True, mode=0o700)
    REPORT['passed'] = sum(c['passed'] for c in REPORT['checks'])
    REPORT['total'] = len(REPORT['checks'])
    output = REPORTS / (RUN + '.json')
    raw = json.dumps(REPORT, indent=2) + '\n'
    for path in (output, REPORTS / 'report-summary.json'):
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600), 'w') as stream:
            stream.write(raw)
        path.chmod(0o600)
    print(json.dumps({'report': str(output), 'status': REPORT['status'],
                      'passed': REPORT['passed'], 'total': REPORT['total']}))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('requires host-provided run_id')
    bind_run_id(sys.argv[1])
    REPORTS.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        integration()
        REPORT['status'] = 'passed'
    except Exception as error:
        REPORT['status'] = 'failed'
        REPORT['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write_report()
