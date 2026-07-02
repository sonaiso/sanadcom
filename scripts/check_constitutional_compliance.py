#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import fnmatch
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - import fallback; fail-closed enforcement happens in _load_manifest.
    yaml = None


MANIFEST_PATH = ".github/agent-constitution-manifest.yml"
RUNTIME_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx"}
TEXT_SUFFIXES = RUNTIME_SUFFIXES | {".md", ".txt", ".yml", ".yaml", ".json"}
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
NEGATION_HINTS = (
    "not",
    "without",
    "does not",
    "doesn't",
    "never",
    "must not",
    "prohibited",
    "forbidden",
)
NEGATIVE_MARKERS = (
    "blocked example",
    "prohibited",
    "forbidden",
    "bad:",
    "blocked:",
    "must not",
    "do not",
    "shortcut",
)
HARD_LITERAL_TOKENS = (
    "action_allowed = true",
    "is_compliant = true",
    "approved = true",
    "certified = true",
    "rank = \"verified\"",
    "rank = 'verified'",
    "rank = \"certified\"",
    "rank = 'certified'",
    "return allowed(",
    "return compliant(",
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


@dataclass(frozen=True)
class ConstitutionManifest:
    required_reference: str
    known_instruction_surfaces: tuple[str, ...]
    discovery_patterns: tuple[str, ...]
    forbidden_override_patterns: tuple[str, ...]
    required_constitutional_terms: tuple[str, ...]
    governance_sensitive_paths: tuple[str, ...]
    allowed_negative_example_paths: tuple[str, ...]
    forbidden_nca_claims: tuple[str, ...]
    shortcut_decision_patterns: tuple[str, ...]
    required_decision_terms: tuple[str, ...]


class ManifestLoadError(RuntimeError):
    pass


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


def _line_content(content: str, line_no: int) -> str:
    lines = content.splitlines()
    if line_no < 1 or line_no > len(lines):
        return ""
    return lines[line_no - 1]


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def _load_manifest(root: Path) -> ConstitutionManifest:
    path = root / MANIFEST_PATH
    if not path.exists():
        raise ManifestLoadError(f"Manifest missing: {MANIFEST_PATH}")
    if yaml is None:
        raise ManifestLoadError("Manifest parsing requires PyYAML; install pyyaml to enforce fail-closed compliance checks.")
    try:
        data = yaml.safe_load(_read(path))
    except Exception as exc:  # pragma: no cover - type-specific errors vary by parser implementation.
        raise ManifestLoadError(f"Manifest parse error in {MANIFEST_PATH}: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestLoadError(f"Manifest {MANIFEST_PATH} must be a mapping.")

    required_keys = (
        "required_reference",
        "known_instruction_surfaces",
        "discovery_patterns",
        "forbidden_override_patterns",
        "required_constitutional_terms",
        "governance_sensitive_paths",
        "allowed_negative_example_paths",
        "forbidden_nca_claims",
        "shortcut_decision_patterns",
        "required_decision_terms",
    )
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ManifestLoadError(f"Manifest missing required keys: {', '.join(missing)}")

    def _tuple_of_strings(key: str) -> tuple[str, ...]:
        value = data.get(key)
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
            raise ManifestLoadError(f"Manifest key '{key}' must be a non-empty list of strings.")
        return tuple(item.strip() for item in value)

    required_reference = data.get("required_reference")
    if not isinstance(required_reference, str) or not required_reference.strip():
        raise ManifestLoadError("Manifest key 'required_reference' must be a non-empty string.")

    return ConstitutionManifest(
        required_reference=required_reference.strip(),
        known_instruction_surfaces=_tuple_of_strings("known_instruction_surfaces"),
        discovery_patterns=_tuple_of_strings("discovery_patterns"),
        forbidden_override_patterns=_tuple_of_strings("forbidden_override_patterns"),
        required_constitutional_terms=_tuple_of_strings("required_constitutional_terms"),
        governance_sensitive_paths=_tuple_of_strings("governance_sensitive_paths"),
        allowed_negative_example_paths=_tuple_of_strings("allowed_negative_example_paths"),
        forbidden_nca_claims=_tuple_of_strings("forbidden_nca_claims"),
        shortcut_decision_patterns=_tuple_of_strings("shortcut_decision_patterns"),
        required_decision_terms=_tuple_of_strings("required_decision_terms"),
    )


def _is_marked_negative_example(content: str, line_no: int) -> bool:
    lines = content.splitlines()
    if not lines:
        return False
    start = max(0, line_no - 5)
    end = min(len(lines), line_no + 2)
    window = "\n".join(lines[start:end]).lower()
    return any(marker in window for marker in NEGATIVE_MARKERS)


def _matches_any_glob(relative_path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in patterns)


def _compile_patterns(values: tuple[str, ...]) -> list[re.Pattern[str]]:
    return [re.compile(value, flags=re.IGNORECASE) for value in values]


def _discover_instruction_files(root: Path, manifest: ConstitutionManifest) -> tuple[list[Path], list[Violation]]:
    violations: list[Violation] = []
    discovered: set[Path] = set()

    for relative in manifest.known_instruction_surfaces:
        path = root / relative
        if not path.exists():
            violations.append(
                Violation(
                    file=relative,
                    line=1,
                    law="Law 12",
                    message="Known instruction surface listed in manifest is missing.",
                )
            )
            continue
        discovered.add(path)

    for pattern in manifest.discovery_patterns:
        matches = list(root.glob(pattern))
        for path in matches:
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            discovered.add(path)

    return sorted(discovered), violations


def check_instruction_surfaces(root: Path, manifest: ConstitutionManifest) -> list[Violation]:
    files, violations = _discover_instruction_files(root, manifest)
    forbidden_patterns = _compile_patterns(manifest.forbidden_override_patterns)

    required_reference = manifest.required_reference.lower()
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            content = _read(path)
        except Exception as exc:
            violations.append(
                Violation(
                    file=relative,
                    line=1,
                    law="Law 12",
                    message=f"Instruction surface could not be parsed/read (fail-closed): {exc}",
                )
            )
            continue

        if path.suffix.lower() in {".yml", ".yaml"}:
            try:
                if yaml is None:
                    raise ManifestLoadError("PyYAML missing")
                yaml.safe_load(content)
            except Exception as exc:  # pragma: no cover - type-specific errors vary by parser implementation.
                violations.append(
                    Violation(
                        file=relative,
                        line=1,
                        law="Law 12",
                        message=f"Instruction YAML cannot be parsed (fail-closed): {exc}",
                    )
                )
                continue

        lowered = content.lower()
        if required_reference not in lowered:
            if relative != manifest.required_reference:
                violations.append(
                    Violation(
                        file=relative,
                        line=1,
                        law="Law 12",
                        message=f"Instruction surface must reference {manifest.required_reference}.",
                    )
                )

        if relative != manifest.required_reference:
            for pattern in forbidden_patterns:
                for match in pattern.finditer(content):
                    line_no = _line_number(content, match.start())
                    line = _line_content(content, line_no).lower()
                    prev_line = _line_content(content, line_no - 1).lower()
                    context = f"{prev_line}\n{line}"
                    if any(hint in context for hint in NEGATION_HINTS):
                        continue
                    violations.append(
                        Violation(
                            file=relative,
                            line=line_no,
                            law="Law 12/15",
                            message="Instruction surface weakens or bypasses AGENTS.md constitutional governance.",
                        )
                    )

    return violations


def check_agents_terms(root: Path, manifest: ConstitutionManifest) -> list[Violation]:
    path = root / manifest.required_reference
    if not path.exists():
        return [
            Violation(
                file=manifest.required_reference,
                line=1,
                law="Law 12",
                message="Required AGENTS root constitution file is missing.",
            )
        ]

    content = _read(path).lower()
    return [
        Violation(
            file=manifest.required_reference,
            line=1,
            law="Law 12",
            message=f"AGENTS constitutional root missing mandatory term: {term}",
        )
        for term in manifest.required_constitutional_terms
        if term.lower() not in content
    ]


def _governance_runtime_files(root: Path, manifest: ConstitutionManifest) -> list[Path]:
    files: set[Path] = set()
    for pattern in manifest.governance_sensitive_paths:
        for path in root.glob(pattern):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in RUNTIME_SUFFIXES:
                continue
            files.add(path)
    return sorted(files)


def _has_guard_reference(content: str, manifest: ConstitutionManifest) -> bool:
    lowered = content.lower()
    return any(term.lower() in lowered for term in manifest.required_decision_terms)


def check_runtime_shortcuts(root: Path, manifest: ConstitutionManifest) -> list[Violation]:
    violations: list[Violation] = []
    patterns = _compile_patterns(manifest.shortcut_decision_patterns)

    for path in _governance_runtime_files(root, manifest):
        relative = path.relative_to(root).as_posix()
        try:
            content = _read(path)
        except Exception as exc:
            violations.append(
                Violation(
                    file=relative,
                    line=1,
                    law="Law 12",
                    message=f"Governance runtime file unreadable (fail-closed): {exc}",
                )
            )
            continue

        has_guard = _has_guard_reference(content, manifest)
        for pattern in patterns:
            for match in pattern.finditer(content):
                line_no = _line_number(content, match.start())
                line = _line_content(content, line_no)
                line_lower = line.lower()

                if _matches_any_glob(relative, manifest.allowed_negative_example_paths):
                    if has_guard and not any(token in line_lower for token in HARD_LITERAL_TOKENS):
                        continue
                    if _is_marked_negative_example(content, line_no):
                        continue
                    violations.append(
                        Violation(
                            file=relative,
                            line=line_no,
                            law="Law 10/15",
                            message=(
                                "Negative example path used shortcut wording without explicit blocked/prohibited marker. "
                                "Mark the snippet as a prohibited example."
                            ),
                        )
                    )
                    continue

                if not has_guard:
                    violations.append(
                        Violation(
                            file=relative,
                            line=line_no,
                            law="Law 1/2/4/6/7/8/9/10/12/15",
                            message=(
                                "Direct decision shortcut in governance-sensitive runtime code without constitutional guard reference. "
                                "Use governed decision flow (BranchLicense/EvidenceTrace/RankPolicy/Residual/Handoff)."
                            ),
                        )
                    )
                    continue

                if any(token in line_lower for token in HARD_LITERAL_TOKENS):
                    violations.append(
                        Violation(
                            file=relative,
                            line=line_no,
                            law="Law 9/10/12/15",
                            message=(
                                "Ambiguous hardcoded decision shortcut in governed file. "
                                "Derive outcome from a governed decision object instead of literal allow/compliant values."
                            ),
                        )
                    )

    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in RUNTIME_SUFFIXES:
            continue
        if not _matches_any_glob(relative, manifest.allowed_negative_example_paths):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        content = _read(path)
        for pattern in patterns:
            for match in pattern.finditer(content):
                line_no = _line_number(content, match.start())
                if _is_marked_negative_example(content, line_no):
                    continue
                violations.append(
                    Violation(
                        file=relative,
                        line=line_no,
                        law="Law 10/15",
                        message=(
                            "Negative example path used shortcut wording without explicit blocked/prohibited marker. "
                            "Mark the snippet as a prohibited example."
                        ),
                    )
                )

    return violations


def check_nca_wording(root: Path, manifest: ConstitutionManifest) -> list[Violation]:
    violations: list[Violation] = []
    escaped_phrases = [re.escape(item) for item in manifest.forbidden_nca_claims]
    patterns = [re.compile(pattern, flags=re.IGNORECASE) for pattern in escaped_phrases]

    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        content = _read(path)
        for pattern in patterns:
            for match in pattern.finditer(content):
                line_no = _line_number(content, match.start())
                line = _line_content(content, line_no).lower()

                if _matches_any_glob(relative, manifest.allowed_negative_example_paths) and _is_marked_negative_example(content, line_no):
                    continue
                if any(hint in line for hint in NEGATION_HINTS):
                    continue

                violations.append(
                    Violation(
                        file=relative,
                        line=line_no,
                        law="Law 14",
                        message=(
                            "Forbidden NCA approval/certification wording detected. "
                            "Use NCA-aligned/mapped/evidence-ready wording unless official certification artifact exists."
                        ),
                    )
                )

    return violations


def run_checks(root: Path) -> list[Violation]:
    violations: list[Violation] = []

    try:
        manifest = _load_manifest(root)
    except ManifestLoadError as exc:
        return [
            Violation(
                file=MANIFEST_PATH,
                line=1,
                law="Law 12",
                message=f"Manifest load failure (fail-closed): {exc}",
            )
        ]

    violations.extend(check_agents_terms(root, manifest))
    violations.extend(check_instruction_surfaces(root, manifest))
    violations.extend(check_runtime_shortcuts(root, manifest))
    violations.extend(check_nca_wording(root, manifest))

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
