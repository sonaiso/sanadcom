from dataclasses import dataclass, field
from enum import Enum, IntEnum


class Rank(IntEnum):
    ZERO = 0
    CANDIDATE = 1
    HYPOTHESIS = 2
    LIKELY = 3
    VERIFIED = 4


class Decision(str, Enum):
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    ALLOWED = "ALLOWED"


class FailedStage(str, Enum):
    ORIGIN = "ORIGIN"
    BRANCH_LICENSE = "BRANCH_LICENSE"
    EFFECTIVE_ATTRIBUTE = "EFFECTIVE_ATTRIBUTE"
    SABAB = "SABAB"
    CONDITION = "CONDITION"
    MANI = "MANI"
    QADIH = "QADIH"
    EVIDENCE = "EVIDENCE"
    RANK = "RANK"
    ACTION = "ACTION"


class ResidualSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Residual:
    stage: FailedStage
    code: str
    message: str
    severity: ResidualSeverity = ResidualSeverity.MEDIUM


@dataclass(frozen=True)
class BranchLicense:
    origin: str
    branch: str
    effective_attribute: str
    sabab: str
    conditions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    qadih_differences: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    rank_policy: dict[str, str] = field(default_factory=dict)
    residual_policy: str = "record_all_failures"


@dataclass(frozen=True)
class TransitionRequest:
    origin: str | None
    branch: str | None
    effective_attribute: str | None
    sabab: str | None
    provided_conditions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    qadih_differences: list[str] = field(default_factory=list)
    evidence_trace: dict[str, str] | None = None
    requested_rank: Rank = Rank.CANDIDATE
    minimum_action_rank: Rank = Rank.VERIFIED
    action_requested: bool = False
    metric_claimed_compliance: bool = False


@dataclass(frozen=True)
class TransitionDecision:
    decision: Decision
    failed_stage: FailedStage | None
    rank: Rank
    action_allowed: bool
    residuals: list[Residual] = field(default_factory=list)
