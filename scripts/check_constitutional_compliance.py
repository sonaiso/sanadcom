#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "docs/SANADCOM_CONSTITUTION.md",
    "docs/NCA_CONSTITUTIONAL_MODEL.md",
    "backend/governance_constitution/contracts.py",
    "backend/governance_constitution/guard.py",
)

AGENTS_MANDATORY_TERMS = (
    "origin",
    "branchlicense",
    "effective attribute",
    "sabab",
    "conditions",
    "mani",
    "qadih",
    "evidence trace",
    "rank",
    "residuals",
    "handoff",
    "forbidden",
    "no shortcut",
    "no bypass",
)

BYPASS_TOKENS = (
    "skip_constitution",
    "bypass_constitution",
    "ignore_constitution",
    "force_allow",
    "force_allowed",
    "force_verified",
    "disable_constitution",
    "constitution_exempt",
    "no_governance_needed",
    "trust_llm_output",
    "trust_rag_output",
)

SHORTCUT_PATTERNS = (
    r"\baction_allowed\s*=\s*True\b",
    r'"action_allowed"\s*:\s*True',
    r'\bdecision\s*=\s*["\']allowed["\']',
    r"\bDecision\.ALLOWED\b",
    r'\brank\s*=\s*["\']verified["\']',
    r"\bRank\.VERIFIED\b",
    r"\bis_compliant\s*=\s*True\b",
    r"\bcompliant\s*=\s*True\b",
    r'\bstatus\s*=\s*["\']compliant["\']',
)

GUARD_REFERENCES = (
    "evaluate_transition",
    "transitiondecision",
    "branchlicense",
    "evidencetrace",
    "constitutional",
    "governance_constitution",
)

NCA_CERTIFICATION_PATTERNS = (
    r"\bnca\b.{0,40}\b(certified|certification|approved|approval)\b",
    r"\b(certified|certification|approved|approval)\b.{0,40}\bnca\b",
)
NEGATION_HINTS = ("not", "without", "does not", "doesn't", "never", "no ")

RUNTIME_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx"}
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}
NEGATIVE_CONTEXT_DIRS = {"tests", "test", "docs", "documentation"}
NEGATIVE_CONTEXT_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "scripts/check_constitutional_compliance.py",
}
GOVERNANCE_PATH_HINTS = (
    "grc",
    "governance",
    "nca",
    "evidence",
    "metric",
    "metrics",
    "ai",
    "risk",
    "assessment",
    "compliance",
)


@dataclass(frozen=True)
class Violation:
    file: str
    line: int
    law: str
    message: str

    def format(self) -> str:
        line = self.line if self.line > 0 else 1
        return f"{self.file}:{line}: [{self.law}] {self.message}"


def _repo_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    while current != current.parent:
        if (current / ".git").exists() or (current / "AGENTS.md").exists():
            return current
        current = current.parent
    raise RuntimeError("Repository root not found.")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _line_number(content: str, index: int) -> int:
    return content.count("\n", 0, index) + 1


def _is_negative_context(relative_path: str) -> bool:
    if relative_path in NEGATIVE_CONTEXT_FILES:
        return True
    parts = set(relative_path.split("/"))
    return bool(parts & NEGATIVE_CONTEXT_DIRS)


def _is_governance_path(relative_path: str) -> bool:
    normalized = relative_path.lower()
    return any(token in normalized for token in GOVERNANCE_PATH_HINTS)


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            path.relative_to(root)
        except ValueError:
            continue
        files.append(path)
    return files


def check_required_files(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            violations.append(
                Violation(
                    file=relative_path,
                    line=1,
                    law="Law 1/2/3",
                    message=f"Required governance file missing: {relative_path}",
                )
            )
    return violations


def check_agents_terms(root: Path) -> list[Violation]:
    content = _read(root / "AGENTS.md").lower() if (root / "AGENTS.md").exists() else ""
    return [
        Violation(
            file="AGENTS.md",
            line=1,
            law="Law 12",
            message=f"AGENTS.md missing mandatory constitutional term: {term}",
        )
        for term in AGENTS_MANDATORY_TERMS
        if term not in content
    ]


def check_instruction_files(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    required = ("read", "follow", "agents.md")
    for relative_path in ("CLAUDE.md", ".github/copilot-instructions.md"):
        path = root / relative_path
        if not path.exists():
            continue
        content = _read(path).lower()
        if any(token not in content for token in required):
            violations.append(
                Violation(
                    file=relative_path,
                    line=1,
                    law="Law 12",
                    message="Instruction file must explicitly require reading and following AGENTS.md.",
                )
            )
    return violations


def check_bypass_tokens(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    token_patterns = [re.compile(rf"\b{re.escape(token)}\b", flags=re.IGNORECASE) for token in BYPASS_TOKENS]
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if _is_negative_context(relative):
            continue
        if path.suffix.lower() not in RUNTIME_SUFFIXES:
            continue
        content = _read(path)
        for token, pattern in zip(BYPASS_TOKENS, token_patterns, strict=True):
            for match in pattern.finditer(content):
                violations.append(
                    Violation(
                        file=relative,
                        line=_line_number(content, match.start()),
                        law="Law 15",
                        message=f"Forbidden bypass token '{token}' in runtime code.",
                    )
                )
    return violations


def check_direct_shortcuts(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    patterns = [re.compile(pattern, flags=re.IGNORECASE) for pattern in SHORTCUT_PATTERNS]
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if _is_negative_context(relative):
            continue
        if path.suffix.lower() not in RUNTIME_SUFFIXES:
            continue
        if not _is_governance_path(relative):
            continue
        content = _read(path)
        lowered = content.lower()
        if any(reference in lowered for reference in GUARD_REFERENCES):
            continue
        for pattern in patterns:
            for match in pattern.finditer(content):
                violations.append(
                    Violation(
                        file=relative,
                        line=_line_number(content, match.start()),
                        law="Law 1/2/4/6/7/8/9/10/12/15",
                        message=(
                            "Direct compliance/action shortcut without constitutional guard reference. "
                            "Use evaluate_transition / TransitionDecision flow."
                        ),
                    )
                )
    return violations


def check_nca_marketing_claims(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    patterns = [re.compile(pattern, flags=re.IGNORECASE) for pattern in NCA_CERTIFICATION_PATTERNS]
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if _is_negative_context(relative):
            continue
        if path.suffix.lower() not in RUNTIME_SUFFIXES and path.suffix.lower() not in {".md", ".txt"}:
            continue
        content = _read(path)
        for pattern in patterns:
            for match in pattern.finditer(content):
                line_no = _line_number(content, match.start())
                line = content.splitlines()[line_no - 1].lower() if content.splitlines() else ""
                if any(hint in line for hint in NEGATION_HINTS):
                    continue
                violations.append(
                    Violation(
                        file=relative,
                        line=line_no,
                        law="Law 14",
                        message=(
                            "NCA wording must be aligned/mapped/evidence-ready and must not claim official "
                            "certification or approval."
                        ),
                    )
                )
    return violations


def run_checks(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    violations.extend(check_required_files(root))
    violations.extend(check_agents_terms(root))
    violations.extend(check_instruction_files(root))
    violations.extend(check_bypass_tokens(root))
    violations.extend(check_direct_shortcuts(root))
    violations.extend(check_nca_marketing_claims(root))
    unique: dict[tuple[str, int, str, str], Violation] = {}
    for violation in violations:
        unique[(violation.file, violation.line, violation.law, violation.message)] = violation
    return sorted(unique.values(), key=lambda item: (item.file, item.line, item.law, item.message))


def main() -> int:
    root = _repo_root(Path(__file__))
    violations = run_checks(root)
    if not violations:
        print("Constitutional compliance checks passed.")
        return 0
    print("Constitutional compliance violations detected:")
    for violation in violations:
        print(f"- {violation.format()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
