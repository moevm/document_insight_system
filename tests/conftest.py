import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def reports_fixture_dir():
    return Path(__file__).parent / "fixtures" / "reports"