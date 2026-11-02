import importlib.util
import pathlib

_SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "check_enterprise_isolation.py"
_spec = importlib.util.spec_from_file_location("check_enterprise_isolation", _SCRIPT)
iso = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(iso)


def _tree(tmp_path, files):
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def test_clean_tree_passes(tmp_path):
    root = _tree(tmp_path, {"backend/core/views.py": "import os\nfrom core import models\n",
                            "enterprise/backend/x.py": "from enterprise_core import models\n"})
    assert iso.scan(root) == []


def test_community_import_of_enterprise_is_blocked(tmp_path):
    # blocked example: AGPL module importing the commercially licensed package
    root = _tree(tmp_path, {"backend/core/views.py": "from enterprise_core.models import ClientSettings\n"})
    hits = iso.scan(root)
    assert len(hits) == 1 and hits[0].startswith("backend/core/views.py:1")


def test_registered_exception_is_skipped_and_nothing_else(tmp_path, monkeypatch):
    root = _tree(tmp_path, {"backend/core/management/commands/dump_permissions.py": "import enterprise_core\n",
                            "backend/other.py": "import enterprise_core\n"})
    hits = iso.scan(root)
    assert [h.split(":")[0] for h in hits] == ["backend/other.py"]


def test_real_repository_has_only_the_registered_exception():
    root = pathlib.Path(__file__).resolve().parents[2]
    assert iso.scan(root) == []
