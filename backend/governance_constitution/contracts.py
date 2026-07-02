from dataclasses import dataclass, field
from enum import Enum, IntEnum

from .enums import DecisionStatus, EvidenceRank, FailedStage
from .validators import (
    derive_action_allowed,
    derive_decision_status,
    ensure_branch_license_fields,
    ensure_evidence_trace_fields,
    ensure_no_forbidden_nca_wording,
    enforce_constitutional_rank_ceiling,
)


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


class ResidualSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class OriginNode:
    origin_id: str
    title: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if not self.origin_id or not self.origin_id.strip():
            raise ValueError("origin_id is required")


@dataclass(frozen=True)
class EffectiveAttribute:
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("effective attribute is required")


@dataclass(frozen=True)
class Sabab:
    reason: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.reason or not self.reason.strip():
            raise ValueError("sabab is required")


@dataclass(frozen=True)
class Condition:
    condition_id: str
    description: str = ""
    satisfied: bool = False

    def __post_init__(self) -> None:
        if not self.condition_id or not self.condition_id.strip():
            raise ValueError("condition_id is required")


@dataclass(frozen=True)
class Mani:
    blocker_id: str
    description: str = ""
    active: bool = False

    def __post_init__(self) -> None:
        if not self.blocker_id or not self.blocker_id.strip():
            raise ValueError("blocker_id is required")


@dataclass(frozen=True)
class QadihDifference:
    difference_id: str
    description: str = ""
    rank_downgrade_steps: int = 1
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        if not self.difference_id or not self.difference_id.strip():
            raise ValueError("difference_id is required")
        if self.rank_downgrade_steps < 0:
            raise ValueError("rank_downgrade_steps cannot be negative")


@dataclass(frozen=True)
class EvidenceTrace:
    source: str
    scope: str
    owner: str
    freshness: str
    control_binding: str
    artifact_ref: str | None = None
    evidence_ref: str | None = None
    evidence_type: str = "artifact"
    metric_like: bool = False

    def __post_init__(self) -> None:
        ensure_evidence_trace_fields(self)

    @property
    def rank_ceiling(self) -> EvidenceRank:
        if self.metric_like:
            return EvidenceRank.CANDIDATE
        return EvidenceRank.SUPPORTED


@dataclass(frozen=True)
class RankPolicy:
    minimum_action_rank: EvidenceRank = EvidenceRank.VERIFIED
    policy_name: str = "default"


@dataclass(frozen=True)
class Residual:
    stage: FailedStage
    code: str
    message: str
    severity: ResidualSeverity = ResidualSeverity.MEDIUM
    exception_recorded: bool = False

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("residual code is required")
        if not self.message or not self.message.strip():
            raise ValueError("residual message is required")
        ensure_no_forbidden_nca_wording(self.message)


@dataclass(frozen=True)
class HandoffRule:
    required: bool = False
    owner: str | None = None
    rationale: str = ""


@dataclass(frozen=True)
class BranchLicense:
    origin: OriginNode | str
    branch_id: str | None = None
    effective_attribute: EffectiveAttribute | str | None = None
    sabab: Sabab | str | None = None
    conditions: tuple[Condition | str, ...] = field(default_factory=tuple)
    mani: tuple[Mani | str, ...] = field(default_factory=tuple)
    qadih_differences: tuple[QadihDifference | str, ...] = field(default_factory=tuple)
    evidence_requirements: tuple[str, ...] = field(default_factory=tuple)
    rank_policy: RankPolicy | dict[str, str] = field(default_factory=RankPolicy)
    residual_policy: str = "record_all_failures"
    branch: str | None = None
    blockers: tuple[Mani | str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if isinstance(self.origin, str):
            object.__setattr__(self, "origin", OriginNode(self.origin))
        if not self.branch_id and not self.branch:
            raise ValueError("branch_id is required")
        if not self.branch_id:
            object.__setattr__(self, "branch_id", self.branch)
        if not self.branch:
            object.__setattr__(self, "branch", self.branch_id)
        if self.branch_id and self.branch and self.branch_id != self.branch:
            raise ValueError("branch_id and branch alias must match")
        if isinstance(self.effective_attribute, str):
            object.__setattr__(self, "effective_attribute", EffectiveAttribute(self.effective_attribute))
        if isinstance(self.sabab, str):
            object.__setattr__(self, "sabab", Sabab(self.sabab))
        if self.blockers and not self.mani:
            object.__setattr__(self, "mani", self.blockers)
        if isinstance(self.rank_policy, dict):
            minimum = self.rank_policy.get("minimum_action_rank", EvidenceRank.VERIFIED)
            if isinstance(minimum, str):
                try:
                    minimum = EvidenceRank[minimum]
                except KeyError as error:
                    raise ValueError(
                        f"invalid minimum_action_rank '{minimum}' in BranchLicense.rank_policy"
                    ) from error
            object.__setattr__(
                self,
                "rank_policy",
                RankPolicy(minimum_action_rank=minimum, policy_name=self.rank_policy.get("policy_name", "default")),
            )
        ensure_branch_license_fields(self)


@dataclass(frozen=True)
class ConstitutionalDecision:
    origin: OriginNode | str
    branch: str
    branch_license: BranchLicense
    effective_attribute: EffectiveAttribute | str
    sabab: Sabab | str
    conditions_evaluated: tuple[Condition, ...] = field(default_factory=tuple)
    mani_evaluated: tuple[Mani, ...] = field(default_factory=tuple)
    qadih_differences: tuple[QadihDifference, ...] = field(default_factory=tuple)
    evidence_traces: tuple[EvidenceTrace, ...] = field(default_factory=tuple)
    rank: EvidenceRank = EvidenceRank.CANDIDATE
    failed_stage: FailedStage | None = None
    residuals: tuple[Residual, ...] = field(default_factory=tuple)
    handoff: HandoffRule = field(default_factory=HandoffRule)
    status: DecisionStatus = field(init=False)
    action_allowed: bool = field(init=False)

    def __post_init__(self) -> None:
        if isinstance(self.origin, str):
            object.__setattr__(self, "origin", OriginNode(self.origin))
        if isinstance(self.effective_attribute, str):
            object.__setattr__(self, "effective_attribute", EffectiveAttribute(self.effective_attribute))
        if isinstance(self.sabab, str):
            object.__setattr__(self, "sabab", Sabab(self.sabab))
        if self.branch_license.origin.origin_id != self.origin.origin_id:
            raise ValueError("branch_license origin must match decision origin")
        enforce_constitutional_rank_ceiling(
            rank=self.rank,
            evidence_traces=self.evidence_traces,
            conditions_evaluated=self.conditions_evaluated,
        )
        status, failed_stage, residuals, rank, handoff = derive_decision_status(self, Residual)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "failed_stage", failed_stage)
        object.__setattr__(self, "residuals", residuals)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "handoff", handoff)
        object.__setattr__(self, "action_allowed", derive_action_allowed(status))


@dataclass(frozen=True)
class GovernedAssessmentDecision:
    constitutional_decision: ConstitutionalDecision
    assessment_id: str | None = None

    @property
    def action_allowed(self) -> bool:
        return self.constitutional_decision.action_allowed

    @property
    def status(self) -> DecisionStatus:
        return self.constitutional_decision.status


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
