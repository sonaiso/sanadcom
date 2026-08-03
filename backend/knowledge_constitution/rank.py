from .contracts import EvidenceBinding
from .enums import KnowledgeRank


def binding_rank_ceiling(binding: EvidenceBinding) -> KnowledgeRank:
    if not binding.provenance_ok or not binding.integrity_ok:
        return KnowledgeRank.CANDIDATE
    if not binding.scope_coverage_ok or not binding.temporal_coverage_ok or not binding.claim_relevance_ok:
        return KnowledgeRank.PLAUSIBLE
    return KnowledgeRank.SUPPORTED
