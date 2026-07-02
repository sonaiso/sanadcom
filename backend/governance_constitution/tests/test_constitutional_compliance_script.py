from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


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


def _manifest_content() -> str:
    return """
required_reference: AGENTS.md
known_instruction_surfaces:
  - AGENTS.md
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/pull_request_template.md
  - docs/CONSTITUTIONAL_AGENT_ENFORCEMENT.md
  - docs/CONSTITUTIONAL_AGENT_CONTRACT.md
discovery_patterns:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
  - "**/*copilot*instructions*.md"
  - "**/*agent*.md"
  - "**/*agent*.yml"
  - "**/*agent*.yaml"
  - "**/*prompt*.md"
  - "**/*governance*.md"
forbidden_override_patterns:
  - "skip\\s+agents\\.md"
  - "constitution\\s+optional"
  - "skip\\s+constitution"
required_constitutional_terms:
  - origin
  - BranchLicense
  - effective_attribute
  - sabab
  - conditions
  - mani
  - qadih
  - evidence trace
  - rank
  - residuals
  - handoff
  - final delivery decision
governance_sensitive_paths:
  - "backend/**/*.py"
allowed_negative_example_paths:
  - "docs/**/*.md"
  - "tests/**/*.py"
  - "backend/**/tests/**/*.py"
  - "scripts/check_constitutional_compliance.py"
forbidden_nca_claims:
  - "certified by NCA"
  - "approved by NCA"
  - "NCA certified"
  - "NCA approved"
shortcut_decision_patterns:
  - "\\baction_allowed\\s*=\\s*True\\b"
  - "\\bDecision\\.ALLOWED\\b"
  - "\\bstatus\\s*=\\s*[\"']compliant[\"']"
  - "\\bcompliance_status\\s*=\\s*[\"']compliant[\"']"
  - "\\bis_compliant\\s*=\\s*True\\b"
  - "\\bapproved\\s*=\\s*True\\b"
  - "\\bcertified\\s*=\\s*True\\b"
  - "\\breturn\\s+Allowed\\s*\\("
  - "\\breturn\\s+Compliant\\s*\\("
  - "\\brank\\s*=\\s*[\"']verified[\"']"
  - "\\brank\\s*=\\s*[\"']certified[\"']"
  - "score\\s*>=\\s*threshold\\s*[-=]*>\\s*compliant"
required_decision_terms:
  - GovernedAssessmentDecision
  - ConstitutionalDecision
  - BranchLicense
  - EvidenceTrace
  - RankPolicy
  - Residual
  - HandoffRule
  - blocked_by_mani
  - qadih_difference
  - failed_stage
  - residuals
  - rank_ceiling
  - evaluate_transition
"""


def _agents_content() -> str:
    return """
origin
BranchLicense
effective_attribute
sabab
conditions
mani
qadih
evidence trace
rank
residuals
handoff
final delivery decision
"""


def _create_minimal_repo(tmp_path: Path) -> Path:
    _write(tmp_path / ".github" / "agent-constitution-manifest.yml", _manifest_content())
    _write(tmp_path / "AGENTS.md", _agents_content())
    _write(tmp_path / "CLAUDE.md", "Read AGENTS.md first and follow AGENTS.md.")
    _write(tmp_path / ".github" / "copilot-instructions.md", "Read AGENTS.md first and follow AGENTS.md.")
    _write(tmp_path / ".github" / "pull_request_template.md", "I read AGENTS.md.")
    _write(tmp_path / "docs" / "CONSTITUTIONAL_AGENT_ENFORCEMENT.md", "Read AGENTS.md.")
    _write(tmp_path / "docs" / "CONSTITUTIONAL_AGENT_CONTRACT.md", "Read AGENTS.md.")
    _write(
        tmp_path / "backend" / "governance" / "decision.py",
        "from governance_constitution.guard import evaluate_transition\n"
        "class ConstitutionalDecision: ...\n",
    )
    return tmp_path


def _messages(violations) -> list[str]:
    return [f"{item.file}:{item.line}:{item.law}:{item.message}" for item in violations]


def test_agent_file_without_agents_reference_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "CLAUDE.md", "Follow local guidance.")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Instruction surface must reference AGENTS.md" in message for message in messages)


def test_agent_file_skip_agents_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "CLAUDE.md", "Read AGENTS.md first. skip AGENTS.md for speed.")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("weakens or bypasses AGENTS.md" in message for message in messages)


def test_agent_file_constitution_optional_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / ".github" / "copilot-instructions.md", "Read AGENTS.md; constitution optional for demos.")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("weakens or bypasses AGENTS.md" in message for message in messages)


def test_future_agent_file_discovered_by_glob_fails_when_noncompliant(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "automation" / "future-agent.md", "Use emergency bypass path.")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("future-agent.md" in message and "must reference AGENTS.md" in message for message in messages)


def test_runtime_action_allowed_true_fails_without_guard(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "governance" / "shortcut.py", "action_allowed = True\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Direct decision shortcut" in message for message in messages)


def test_runtime_action_allowed_from_governed_decision_passes(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(
        root / "backend" / "governance" / "guarded.py",
        "class GovernedAssessmentDecision: ...\n"
        "decision = GovernedAssessmentDecision()\n"
        "action_allowed = decision.action_allowed\n",
    )
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("action_allowed" in message for message in messages)


def test_runtime_status_compliant_fails_unless_guarded_serialization(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "governance" / "status_shortcut.py", 'status = "compliant"\n')
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Direct decision shortcut" in message for message in messages)


def test_runtime_status_compliant_in_governed_serialization_passes(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(
        root / "backend" / "governance" / "serialization.py",
        "class ConstitutionalDecision: ...\n"
        "payload = {'status': 'compliant'}\n"
        "residuals = []\n",
    )
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("serialization.py" in message for message in messages)


def test_metric_shortcut_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "governance" / "metric_shortcut.py", "score >= threshold -> compliant\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Direct decision shortcut" in message for message in messages)


def test_nca_forbidden_wording_fails(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "governance" / "nca_claim.py", 'claim = "certified by NCA"\n')
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Forbidden NCA approval/certification wording" in message for message in messages)


def test_nca_safe_wording_passes(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "backend" / "governance" / "nca_safe.py", 'claim = "NCA-aligned and evidence-ready"\n')
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("nca_safe.py" in message for message in messages)


def test_missing_manifest_fails_closed(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    (root / ".github" / "agent-constitution-manifest.yml").unlink()
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Manifest load failure" in message for message in messages)


def test_negative_examples_in_docs_pass_only_when_marked(tmp_path: Path) -> None:
    root = _create_minimal_repo(tmp_path)
    _write(root / "docs" / "bad-example.md", "action_allowed = True\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert any("Negative example path used shortcut wording" in message for message in messages)

    _write(root / "docs" / "bad-example.md", "Bad: blocked example\naction_allowed = True\n")
    violations = CHECKER.run_checks(root)
    messages = _messages(violations)
    assert not any("Negative example path used shortcut wording" in message for message in messages)
