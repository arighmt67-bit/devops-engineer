"""Pure recovery/provenance gates; privileged effects live in guest_test.py."""


def validate_source(archive, metadata):
    import hashlib
    from pathlib import Path
    if metadata.get('commit') != '040a9bef5aa857b0251bf41a805dd75fc91f44ab':
        raise ValueError('source commit is not the pinned unchanged app')
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest() != metadata.get('sha256'):
        raise ValueError('source SHA256 mismatch')
    import tarfile
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            path = Path(member.name)
            if (path.is_absolute() or '..' in path.parts
                or path.parts[0] not in ('src', 'migrations', 'package.json', 'package-lock.json')
                or not (member.isfile() or member.isdir())):
                raise ValueError('unsafe or unexpected source archive member')


def validate_installation(app_root, archive, metadata):
    """Read-only exact pinned-tree check; only top-level npm node_modules is extra.

    Return the input root as a Path on success; raise ValueError on invalid source,
    unreadable/missing/modified entries, symlinks, or unexpected pinned inventory.
    """
    validate_source(archive, metadata)
    from pathlib import Path
    import stat
    import tarfile
    root = Path(app_root)

    def require_directory(path):
        # lstat deliberately checks the entry itself rather than its link target.
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError(f'installed source directory is not a real directory: {path}')

    try:
        absolute = root.absolute()
        for ancestor in reversed((absolute, *absolute.parents)):
            require_directory(ancestor)
        expected = set()
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                relative = Path(member.name)
                installed = root / relative
                for parent in relative.parents:
                    if parent != Path('.'):
                        require_directory(root / parent)
                        expected.add(('directory', parent))
                if member.isdir():
                    require_directory(installed)
                    expected.add(('directory', relative))
                else:
                    if not stat.S_ISREG(installed.lstat().st_mode):
                        raise ValueError(f'installed source file is not regular: {member.name}')
                    source = tar.extractfile(member)
                    if source is None:
                        raise ValueError(f'unreadable archived source file: {member.name}')
                    with source:
                        if installed.read_bytes() != source.read():
                            raise ValueError(f'modified installed source file: {member.name}')
                    expected.add(('file', relative))
        actual = set()
        pending = [root]
        while pending:
            directory = pending.pop()
            for entry in directory.iterdir():
                relative = entry.relative_to(root)
                if relative == Path('node_modules'):
                    continue  # npm runtime inventory is deliberately outside the pinned tree.
                mode = entry.lstat().st_mode
                if stat.S_ISDIR(mode):
                    actual.add(('directory', relative))
                    pending.append(entry)
                elif stat.S_ISREG(mode):
                    actual.add(('file', relative))
                else:
                    raise ValueError(f'nonregular or symlink installed source entry: {relative}')
        if actual != expected:
            raise ValueError('installed pinned source inventory differs from archive')
    except OSError as error:
        raise ValueError('cannot read installed pinned source') from error
    return root


import re


def validate_target(name, existing=()):
    if not isinstance(name, str) or not re.fullmatch(r'opslab_restore_[a-z0-9_]{1,40}', name):
        raise ValueError('restore target must be in the dedicated safe namespace')
    if name in existing:
        raise ValueError('target already exists; never overwrite')
    return name


def validate_archive(path, root, expected_sha256):
    from pathlib import Path
    candidate = Path(path).resolve()
    if not candidate.is_relative_to(Path(root).resolve()) or not candidate.is_file():
        raise ValueError('archive must be a regular file inside backup root')
    import hashlib
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('archive hash mismatch; refuse before database creation')
    return candidate
def validate_report(report):
    """Only metadata/check evidence may cross the guest boundary; never secrets."""
    if not isinstance(report, dict) or not re.fullmatch(r'[a-z0-9_]{1,63}', report.get('run_id', '')):
        raise ValueError('unsafe report run_id')
    allowed = {'run_id', 'fixture_label', 'status', 'passed', 'total', 'checks', 'observations', 'error'}
    if set(report) - allowed or report.get('status') not in ('passed', 'failed'):
        raise ValueError('unsafe report fields/status')
    checks = report.get('checks')
    if not isinstance(checks, list) or not all(isinstance(c, dict) and type(c.get('passed')) is bool for c in checks):
        raise ValueError('invalid checks')
    passed = sum(c['passed'] for c in checks)
    if report.get('total') != len(checks) or report.get('passed') != passed:
        raise ValueError('inconsistent report counts')
    if report['status'] == 'passed' and (not checks or passed != len(checks)):
        raise ValueError('false success report')
    def scan(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if re.search(r'password|token|credential|service[_.]env|dump|pgpass', key, re.I):
                    raise ValueError('secret-bearing evidence field')
                scan(child)
        elif isinstance(value, list):
            for child in value:
                scan(child)
        elif isinstance(value, str) and re.search(r'Bearer\s+\S+|PGPASSWORD=|ACCESS_TOKEN_KEY=|REFRESH_TOKEN_KEY=', value):
            raise ValueError('secret-bearing evidence value')
    scan(report)
    return report
