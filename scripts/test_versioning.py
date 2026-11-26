"""Offline regression tests for the single-source application version workflow."""

import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_versions import ROOT, check_version, read_version, sync_version


class VersioningTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='dis-versioning-')
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('IMAGE_VERSION', None)
        self.manifest = {'name': 'fixture', 'version': '3.0.1'}
        self.lock = {
            'name': 'fixture',
            'version': '3.0.0',
            'lockfileVersion': 3,
            'packages': {
                '': {'version': '3.0.0', 'dependencies': {'example': '1.2.3'}},
                'node_modules/example': {'version': '1.2.3', 'integrity': 'sha512-unchanged'},
            },
        }
        self.write_json('package.json', self.manifest)
        self.write_json('package-lock.json', self.lock)
        (self.root / '.env').write_text('ACCESS_TOKEN=keep-exactly\nIMAGE_VERSION=0.6\nSECRET_KEY="unchanged"\n')
        (self.root / '.env').chmod(0o600)
        (self.root / '.env_example').write_text('# IMAGE_VERSION comes from package.json\nACCESS_TOKEN=example\n')
        for name in ('Dockerfile', 'Dockerfile_worker', 'Dockerfile_worker_base'):
            shutil.copyfile(ROOT / name, self.root / name)

    def write_json(self, name, data):
        (self.root / name).write_text(json.dumps(data, indent=2) + '\n')

    def test_check_is_read_only(self):
        before = {name: (self.root / name).read_bytes() for name in ('package-lock.json', '.env')}
        with self.assertRaisesRegex(ValueError, 'sync-version'):
            check_version(self.root)
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in before})

    def test_sync_changes_only_application_metadata_and_preserves_env(self):
        sync_version(self.root)
        actual = json.loads((self.root / 'package-lock.json').read_text())
        expected = copy.deepcopy(self.lock)
        expected['version'] = expected['packages']['']['version'] = '3.0.1'
        self.assertEqual(actual, expected)
        self.assertEqual(
            (self.root / '.env').read_text(),
            'ACCESS_TOKEN=keep-exactly\nIMAGE_VERSION=3.0.1\nSECRET_KEY="unchanged"\n',
        )
        self.assertEqual((self.root / '.env').stat().st_mode & 0o777, 0o600)
        self.assertEqual(check_version(self.root, tag='v3.0.1'), '3.0.1')
        before = {name: (self.root / name).stat().st_mtime_ns for name in ('package-lock.json', '.env')}
        sync_version(self.root)
        self.assertEqual(before, {name: (self.root / name).stat().st_mtime_ns for name in before})

    def test_missing_env_is_not_created(self):
        (self.root / '.env').unlink()
        sync_version(self.root)
        self.assertFalse((self.root / '.env').exists())
        self.assertEqual(check_version(self.root), '3.0.1')

    def test_adds_generated_env_value_and_removes_duplicate_overrides(self):
        for initial in ('ACCESS_TOKEN=keep', 'IMAGE_VERSION=old\nexport IMAGE_VERSION=older\nACCESS_TOKEN=keep\n'):
            with self.subTest(initial=initial):
                (self.root / '.env').write_text(initial)
                sync_version(self.root)
                content = (self.root / '.env').read_text()
                self.assertEqual(content.count('IMAGE_VERSION='), 1)
                self.assertIn('IMAGE_VERSION=3.0.1\n', content)
                self.assertIn('ACCESS_TOKEN=keep', content)

    def test_invalid_manifest_does_not_modify_derived_files(self):
        self.write_json('package.json', {'version': 'invalid'})
        before = (self.root / 'package-lock.json').read_bytes()
        with self.assertRaises(ValueError):
            sync_version(self.root)
        self.assertEqual((self.root / 'package-lock.json').read_bytes(), before)

    def test_tag_and_docker_defaults_cannot_drift(self):
        sync_version(self.root)
        with self.assertRaisesRegex(ValueError, 'release tag'):
            check_version(self.root, tag='v2.0.0')
        with (self.root / 'Dockerfile').open('a') as stream:
            stream.write('\nARG IMAGE_VERSION=0.6\n')
        with self.assertRaisesRegex(ValueError, 'remove the IMAGE_VERSION default'):
            check_version(self.root)

    @unittest.skipUnless(shutil.which('make'), 'GNU Make is required')
    def test_make_syncs_before_build_and_start_and_ignores_version_override(self):
        shutil.copyfile(ROOT / 'Makefile', self.root / 'Makefile')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copyfile(ROOT / 'scripts/check_versions.py', scripts / 'check_versions.py')
        binary = self.root / 'bin'
        binary.mkdir()
        docker = binary / 'docker'
        docker.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
version = os.environ['IMAGE_VERSION']
root = Path.cwd()
assert json.loads((root/'package-lock.json').read_text())['version'] == version
assert f'IMAGE_VERSION={version}\\n' in (root/'.env').read_text()
with (root/'calls.jsonl').open('a') as stream:
    stream.write(json.dumps({'args': args, 'version': version})+'\\n')
if 'config' in args:
    print('dvivanov/dis:worker-base-'+version)
elif args[:2] == ['image', 'inspect']:
    sys.exit(0 if (root/'base-built').exists() else 1)
elif 'build' in args and args[-1] == 'worker-base':
    (root/'base-built').touch()
elif 'build' in args and args[-1] == 'worker':
    assert (root/'base-built').exists(), 'worker built before base'
''')
        docker.chmod(0o755)
        env = {
            **os.environ,
            'PATH': str(binary) + os.pathsep + os.environ['PATH'],
            'VCS_REF': 'fixture',
            'SOURCE_BRANCH': 'fixture',
            'SOURCE_STATE': 'dirty',
            'BUILD_DATE': '2026-10-16T00:00:00Z',
        }
        for target, version in (('build-all', '3.0.1'), ('up-d', '3.0.2')):
            self.write_json('package.json', {**self.manifest, 'version': version})
            result = subprocess.run(
                ['make', '-s', '-j4', target, 'IMAGE_VERSION=99.0.0'],
                cwd=self.root,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = [json.loads(line) for line in (self.root / 'calls.jsonl').read_text().splitlines()]
            self.assertEqual(calls[-1]['version'], version)
            self.assertEqual(read_version(self.root), version)


if __name__ == '__main__':
    unittest.main()
