import pytest
import sys
import types
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))


def _install_checks_package_shim(package_name, package_path):
    package = types.ModuleType(package_name)
    package.__path__ = [str(package_path)]
    package.__package__ = package_name
    sys.modules.setdefault(package_name, package)


def _is_reports_test_run():
    return any("tests/reports" in arg.replace("\\", "/") for arg in sys.argv)


if _is_reports_test_run():
    for prefix in ("app.main.checks", "main.checks"):
        _install_checks_package_shim(prefix, project_root / "app" / "main" / "checks")
        _install_checks_package_shim(
            f"{prefix}.report_checks",
            project_root / "app" / "main" / "checks" / "report_checks",
        )

@pytest.fixture
def reports_fixture_dir():
    return Path(__file__).parent / "fixtures" / "reports"
