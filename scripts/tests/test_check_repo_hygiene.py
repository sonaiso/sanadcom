import importlib.util
import pathlib
import subprocess

_SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "check_repo_hygiene.py"
_spec = importlib.util.spec_from_file_location("check_repo_hygiene", _SCRIPT)
hygiene = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(hygiene)


def _git_repo_with(tmp_path, files):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for rel, size in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    return tmp_path


def test_clean_repository_passes(tmp_path):
    root = _git_repo_with(tmp_path, {"README.md": 10, "backend/app.py": 20})
    assert hygiene.violations(root, hygiene.tracked_files(root)) == []


def test_database_dump_is_blocked(tmp_path):
    # blocked example: a committed PostgreSQL dump must fail the gate
    root = _git_repo_with(tmp_path, {"local_db_backup.dump": 10})
    found = hygiene.violations(root, hygiene.tracked_files(root))
    assert len(found) == 1 and found[0].startswith("local_db_backup.dump")


def test_sqlite_wal_backup_directory_is_blocked(tmp_path):
    root = _git_repo_with(tmp_path, {"db-backup-sqlite-20260312/ciso-assistant.sqlite3-wal": 10})
    assert hygiene.violations(root, hygiene.tracked_files(root))


def test_oversized_file_is_blocked(tmp_path):
    root = _git_repo_with(tmp_path, {"big.bin": hygiene.MAX_FILE_BYTES + 1})
    found = hygiene.violations(root, hygiene.tracked_files(root))
    assert found and "exceeds" in found[0]


def test_planted_fault_mutation_is_caught(tmp_path, monkeypatch):
    # blocked example: if someone empties the forbidden patterns, the dump test above must still fail loudly
    root = _git_repo_with(tmp_path, {"x.dump": 10})
    monkeypatch.setattr(hygiene, "FORBIDDEN_PATTERNS", ())
    assert hygiene.violations(root, hygiene.tracked_files(root)) == []  # the mutant lets it through ...
    monkeypatch.undo()
    assert hygiene.violations(root, hygiene.tracked_files(root)) != []  # ... and the real gate does not
