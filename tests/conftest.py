import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def presentations_fixtures_dir():
    return Path(__file__).parent / "fixtures" / "presentations"

@pytest.fixture
def find_tasks_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "find_tasks"

@pytest.fixture
def further_dev_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "further_dev"

@pytest.fixture
def image_capture_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "image_capture"

@pytest.fixture
def right_words_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "right_words"

@pytest.fixture
def sld_enum_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "sld_enum"

@pytest.fixture
def sld_similarity_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "sld_similarity"

@pytest.fixture
def task_tracker_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "task_tracker"

@pytest.fixture
def title_format_fixtures_dir(presentations_fixtures_dir):
    return presentations_fixtures_dir / "title_format"