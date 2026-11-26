"""Application build information, baked into Docker images as environment values."""

import json
import os
from pathlib import Path


def get_build_info():
    version = os.environ.get('APP_VERSION')
    if not version:
        # Local development uses the application manifest; Docker needs no manifest copy.
        manifest = Path(__file__).resolve().parents[1] / 'package.json'
        try:
            version = json.loads(manifest.read_text())['version']
        except (OSError, ValueError, KeyError):
            version = 'unknown'
    return {
        'version': version,
        'commit': os.environ.get('APP_COMMIT', 'unknown'),
        'date': os.environ.get('APP_BUILD_DATE', 'unknown'),
        'branch': os.environ.get('APP_BRANCH', 'unknown'),
        'source_state': os.environ.get('APP_SOURCE_STATE', 'unknown'),
    }
