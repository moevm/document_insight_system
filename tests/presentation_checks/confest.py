import pytest
from unittest.mock import Mock
from tests.presentation_checks.mock_presentation import MockPresentation


@pytest.fixture
def mock_presentation():
    return MockPresentation()


@pytest.fixture
def mock_file():
    mock = Mock()
    mock.get_text_from_slides.return_value = []
    mock.get_titles.return_value = []
    mock.found_index = {}
    return mock