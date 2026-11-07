"""Read, sync or validate the application version declared in package.json."""

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_version(root=ROOT):
    version = json.loads((root / 'package.json').read_text())['version']
    if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError(f'Expected a stable SemVer application version, got {version!r}')
    return version


def sync_version(root=ROOT):
    version = read_version(root)
    path = root / 'package-lock.json'
    lock = json.loads(path.read_text())
    if lock['version'] != version or lock['packages']['']['version'] != version:
        # Only application metadata changes; dependency pins and hashes stay intact.
        lock['version'] = version
        lock['packages']['']['version'] = version
        path.write_text(json.dumps(lock, indent=2) + '\n')
    path = root / '.env'
    if path.exists():
        original = path.read_text()
        lines = original.splitlines(keepends=True)
        updated = []
        found = False
        for line in lines:
            if re.match(r'^\s*(?:export\s+)?IMAGE_VERSION\s*=', line):
                if not found:
                    updated.append(f'IMAGE_VERSION={version}\n')
                    found = True
            else:
                updated.append(line)
        if not found:
            if updated and not updated[-1].endswith('\n'):
                updated[-1] += '\n'
            updated.append(f'IMAGE_VERSION={version}\n')
        content = ''.join(updated)
        if content != original:
            path.write_text(content)
    return version


def check_version(root=ROOT, tag=None):
    version = read_version(root)
    errors = []
    lock = json.loads((root / 'package-lock.json').read_text())
    values = {
        'package-lock.json': lock['version'],
        'package-lock.json packages[""]': lock['packages']['']['version'],
    }
    for name in ('Dockerfile', 'Dockerfile_worker', 'Dockerfile_worker_base'):
        text = (root / name).read_text()
        if not re.search(r'^ARG IMAGE_VERSION\s*$', text, re.MULTILINE):
            errors.append(f'{name}: declare ARG IMAGE_VERSION without a hardcoded default')
        if re.search(r'^ARG IMAGE_VERSION=', text, re.MULTILINE):
            errors.append(f'{name}: remove the IMAGE_VERSION default; use the manifest')
    if re.search(r'^\s*(?:export\s+)?IMAGE_VERSION\s*=', (root / '.env_example').read_text(), re.MULTILINE):
        errors.append('.env_example: IMAGE_VERSION is generated locally; remove its value')
    path = root / '.env'
    if path.exists():
        match = re.search(r'^IMAGE_VERSION=(.+)$', path.read_text(), re.MULTILINE)
        values['generated .env IMAGE_VERSION'] = match.group(1) if match else None
    if 'IMAGE_VERSION' in os.environ:
        values['IMAGE_VERSION environment override'] = os.environ['IMAGE_VERSION']
    if tag:
        values['release tag'] = tag.removeprefix('v')
    for name, actual in values.items():
        if actual != version:
            errors.append(f'{name}: expected {version}, got {actual!r}')
    if errors:
        raise ValueError('\n'.join(errors) + '\nRun make sync-version after changing package.json.')
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '--sync', action='store_true', help='Sync npm lock metadata and local .env without resolving packages'
    )
    mode.add_argument('--print-version', action='store_true', help='Print only the manifest version')
    parser.add_argument('--tag', help='Optional release tag, for example v3.0.0')
    args = parser.parse_args()
    try:
        if args.print_version:
            print(read_version())
            return
        if args.sync:
            sync_version()
        version = check_version(tag=args.tag)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error)) from None
    print(f'Application version {version}: manifest, npm lock and generated Docker version agree')


if __name__ == '__main__':
    main()
