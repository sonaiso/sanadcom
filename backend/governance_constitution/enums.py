from enum import Enum, IntEnum


class DecisionStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    ALLOWED = "ALLOWED"


class EvidenceRank(IntEnum):
    ZERO = 0
    CANDIDATE = 1
    HYPOTHESIS = 2
    SUPPORTED = 3
    VERIFIED = 4


class FailedStage(str, Enum):
    ORIGIN = "ORIGIN"
    BRANCH_LICENSE = "BRANCH_LICENSE"
    EFFECTIVE_ATTRIBUTE = "EFFECTIVE_ATTRIBUTE"
    SABAB = "SABAB"
    CONDITIONS = "CONDITIONS"
    MANI = "MANI"
    QADIH_DIFFERENCE = "QADIH_DIFFERENCE"
    EVIDENCE_TRACE = "EVIDENCE_TRACE"
    RANK = "RANK"
    RESIDUALS = "RESIDUALS"
    HANDOFF = "HANDOFF"
    # Backward-compatible aliases used by existing guard paths.
    CONDITION = "CONDITIONS"
    QADIH = "QADIH_DIFFERENCE"
    EVIDENCE = "EVIDENCE_TRACE"
    ACTION = "HANDOFF"


class BranchApplicabilityState(str, Enum):
    NOT_APPLICABLE = "branch_not_applicable"
    CANDIDATE = "branch_candidate"
    BLOCKED = "branch_blocked"
    APPLICABLE = "branch_applicable"
