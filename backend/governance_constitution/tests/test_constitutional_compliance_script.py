from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "check_constitutional_compliance.py"
SPEC = importlib.util.spec_from_file_location("constitutional_checker", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _required_agents_content() -> str:
    return """
Origin
BranchLicense
Effective Attribute
Sabab
Conditions
Mani
Qadih
Evidence Trace
Rank
Residuals
Handoff
forbidden
no shortcut
no bypass
"""


def _create_minimal_repo(tmp_path: Path) -> Path:
    _write(tmp_path / "AGENTS.md", _required_agents_content())
    _write(tmp_path / "CLAUDE.md", "Read AGENTS.md first and follow AGENTS.md always.")
    _write(
        tmp_path / ".github" / "copilot-instructions.md",
        "Read AGENTS.md and follow AGENTS.md before making changes.",
    )
    _write(tmp_path / "docs" / "SANADCOM_CONSTITUTION.md", "Constitution")
    _write(tmp_path / "docs" / "NCA_CONSTITUTIONAL_MODEL.md", "Aligned, not certified.")
    _write(tmp_path / "backend" / "governance_constitution" / "contracts.py", "class Decision: ...")
    _write(
        tmp_path / "backend" / "governance_constitution" / "guard.py",
        "from governance_constitution.contracts import TransitionDecision\n"
        "def evaluate_transition():\n"
        "    return TransitionDecision\n",
    )
    _write(tmp_path / "backend" / "grc" / "service.py", "def ok():\n    return True\n")
    return tmp_path


def _messages(violations) -> list[str]:
    return [f"{item.file}:{item.line}:{item.law}:{item.message}" for item in violations]


def test_required_files_check_passes(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    violations = CHECKER.run_checks(root)
    assert violations == []


def test_missing_agents_md_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    (root / "AGENTS.md").unlink()
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Required governance file missing: AGENTS.md" in message for message in messages)


@pytest.mark.parametrize("token", ["force_allow", "skip_constitution", "trust_llm_output"])
def test_forbidden_bypass_token_fails_in_runtime_code(tmp_path: Path, token: str) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "grc" / "runtime.py", f"{token} = True\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any(f"Forbidden bypass token '{token}'" in message for message in messages)


def test_forbidden_token_allowed_in_negative_test_context(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "tests" / "test_negative_examples.py", "force_allow = True\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("Forbidden bypass token 'force_allow'" in message for message in messages)


@pytest.mark.parametrize(
    "line",
    [
        "action_allowed = True\n",
        "is_compliant = True\n",
        "status = 'compliant'\n",
        "rank = 'verified'\n",
        "compliant = True\n",
    ],
)
def test_direct_action_allowed_true_fails_without_guard_reference(tmp_path: Path, line: str) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "ai" / "decision.py", line)
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Direct compliance/action shortcut" in message for message in messages)


def test_direct_decision_allowed_fails_without_guard_reference(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "metrics" / "decision.py", "decision = Decision.ALLOWED\nrank = Rank.VERIFIED\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Direct compliance/action shortcut" in message for message in messages)


def test_guarded_usage_passes_when_evaluate_transition_present(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(
        root / "backend" / "evidence" / "flow.py",
        "from governance_constitution.guard import evaluate_transition\n"
        "decision = Decision.ALLOWED\n"
        "evaluate_transition()\n",
    )
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("Direct compliance/action shortcut" in message for message in messages)


@pytest.mark.parametrize(
    "claim",
    [
        "Officially certified by NCA",
        "NCA approved baseline",
        "NCA certification completed",
        "approved by NCA authority",
    ],
)
def test_nca_certification_claim_is_detected(tmp_path: Path, claim: str) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "reporting" / "nca_claim.py", f'CLAIM = "{claim}"\n')
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("NCA wording must be aligned/mapped/evidence-ready" in message for message in messages)
