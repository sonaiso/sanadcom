from .contracts import (
    ClosureBundle,
    DomainContract,
    IdentityCertificate,
    ProtocolDecision,
    RelationCertificate,
    Residual,
    ScopeCertificate,
    ScopeProfile,
    TransitionCertificate,
    TransitionProposal,
    UnitCertificate,
)
from .enums import ConstitutionalRank, ProtocolStage, ResidualKind, TransitionStatus


def _scope_exceeded(certified: ScopeProfile, supported: ScopeProfile) -> bool:
    checks = (
        ("quantifier", certified.quantifier, supported.quantifier),
        ("temporal", certified.temporal, supported.temporal),
        ("spatial", certified.spatial, supported.spatial),
        ("conditional", certified.conditional, supported.conditional),
        ("referential", certified.referential, supported.referential),
        ("modal", certified.modal, supported.modal),
    )
    return any(certified_value and certified_value != supported_value for _, certified_value, supported_value in checks)


def evaluate_transition_proposal(
    *,
    proposal: TransitionProposal,
    certifier_authority: str,
    unit_certificate: UnitCertificate | None,
    identity_certificate: IdentityCertificate | None,
    domain_contract: DomainContract | None,
    relation_certificate: RelationCertificate | None,
    scope_certificate: ScopeCertificate | None,
    closure_bundle: ClosureBundle | None,
    constitution_version: str = "1.0.0",
    existing_residuals: tuple[Residual, ...] = (),
) -> ProtocolDecision:
    residuals: list[Residual] = list(existing_residuals)
    failed_stage: ProtocolStage | None = None

    if certifier_authority.strip().upper() == proposal.proposer_type.value:
        residuals.append(
            Residual(
                code="self_certification_attempt",
                kind=ResidualKind.SELF_CERTIFICATION,
                stage=ProtocolStage.CERTIFICATION,
                description="Proposal authority cannot certify its own proposal.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Independent certifier authority is assigned.",
            )
        )

    if unit_certificate is None:
        failed_stage = failed_stage or ProtocolStage.UNIT
        residuals.append(
            Residual(
                code="missing_unit_certificate",
                kind=ResidualKind.MISSING_UNIT_PROOF,
                stage=ProtocolStage.UNIT,
                description="Unit certificate is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide unit certificate with carrier and boundary rule.",
            )
        )
    if identity_certificate is None:
        failed_stage = failed_stage or ProtocolStage.IDENTITY
        residuals.append(
            Residual(
                code="missing_identity_certificate",
                kind=ResidualKind.IDENTITY_GAP,
                stage=ProtocolStage.IDENTITY,
                description="Identity certificate is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide identity certificate with preserved identity basis.",
            )
        )
    if domain_contract is None:
        failed_stage = failed_stage or ProtocolStage.DOMAIN
        residuals.append(
            Residual(
                code="missing_domain_contract",
                kind=ResidualKind.DOMAIN_MISMATCH,
                stage=ProtocolStage.DOMAIN,
                description="Domain contract is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide domain contract for proposal domain.",
            )
        )
    if relation_certificate is None:
        failed_stage = failed_stage or ProtocolStage.RELATION
        residuals.append(
            Residual(
                code="missing_relation_certificate",
                kind=ResidualKind.RELATION_UNLICENSED,
                stage=ProtocolStage.RELATION,
                description="Relation certificate is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide relation certificate matching proposed relation.",
            )
        )
    if scope_certificate is None:
        failed_stage = failed_stage or ProtocolStage.SCOPE
        residuals.append(
            Residual(
                code="missing_scope_certificate",
                kind=ResidualKind.SCOPE_EXCEEDED,
                stage=ProtocolStage.SCOPE,
                description="Scope certificate is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide scope certificate with supported and certified scope.",
            )
        )
    if closure_bundle is None:
        failed_stage = failed_stage or ProtocolStage.CLOSURE
        residuals.append(
            Residual(
                code="missing_closure_bundle",
                kind=ResidualKind.INFERENCE_GAP,
                stage=ProtocolStage.CLOSURE,
                description="Closure bundle is required before certification.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Provide closure bundle showing structural/referential/inferential/epistemic closure.",
            )
        )

    if domain_contract is not None:
        if proposal.domain_ref and proposal.domain_ref != domain_contract.domain_id:
            failed_stage = failed_stage or ProtocolStage.DOMAIN
            residuals.append(
                Residual(
                    code="domain_mismatch",
                    kind=ResidualKind.DOMAIN_MISMATCH,
                    stage=ProtocolStage.DOMAIN,
                    description="Proposed domain does not match provided domain contract.",
                    blocking=True,
                    rank_ceiling=ConstitutionalRank.CANDIDATE,
                    trace_ref=proposal.trace_id,
                    reopen_condition="Align proposal domain with domain contract.",
                )
            )
        if proposal.proposed_relation.relation_type not in domain_contract.allowed_relation_types:
            failed_stage = failed_stage or ProtocolStage.RELATION
            residuals.append(
                Residual(
                    code="relation_not_allowed_in_domain",
                    kind=ResidualKind.RELATION_UNLICENSED,
                    stage=ProtocolStage.RELATION,
                    description="Proposed relation type is not licensed by domain contract.",
                    blocking=True,
                    rank_ceiling=ConstitutionalRank.CANDIDATE,
                    trace_ref=proposal.trace_id,
                    reopen_condition="Use an allowed relation type or update domain contract.",
                )
            )

    if identity_certificate is not None and identity_certificate.preserved:
        if identity_certificate.basis.strip().lower() == "similarity":
            failed_stage = failed_stage or ProtocolStage.IDENTITY
            residuals.append(
                Residual(
                    code="identity_from_similarity_forbidden",
                    kind=ResidualKind.IDENTITY_GAP,
                    stage=ProtocolStage.IDENTITY,
                    description="Similarity cannot be upgraded to identity preservation.",
                    blocking=True,
                    rank_ceiling=ConstitutionalRank.PLAUSIBLE,
                    trace_ref=proposal.trace_id,
                    reopen_condition="Provide identity-preserving evidence instead of similarity.",
                )
            )

    if relation_certificate is not None:
        if relation_certificate.relation_type != proposal.proposed_relation.relation_type:
            failed_stage = failed_stage or ProtocolStage.RELATION
            residuals.append(
                Residual(
                    code="relation_type_upgrade_forbidden",
                    kind=ResidualKind.RELATION_UNLICENSED,
                    stage=ProtocolStage.RELATION,
                    description="Relation candidate type cannot be upgraded during certification.",
                    blocking=True,
                    rank_ceiling=ConstitutionalRank.CANDIDATE,
                    trace_ref=proposal.trace_id,
                    reopen_condition="Certify the same relation type as proposed or submit a new proposal.",
                )
            )

    if scope_certificate is not None:
        if _scope_exceeded(scope_certificate.certified_scope, scope_certificate.supported_scope) and not scope_certificate.generalization_license:
            failed_stage = failed_stage or ProtocolStage.SCOPE
            residuals.append(
                Residual(
                    code="scope_expansion_without_license",
                    kind=ResidualKind.SCOPE_EXCEEDED,
                    stage=ProtocolStage.SCOPE,
                    description="Certified scope exceeds supported scope without explicit license.",
                    blocking=True,
                    rank_ceiling=ConstitutionalRank.PLAUSIBLE,
                    trace_ref=proposal.trace_id,
                    reopen_condition="Add scope generalization license or narrow certified scope.",
                )
            )

    if closure_bundle is not None and not all(
        [
            closure_bundle.structural,
            closure_bundle.referential,
            closure_bundle.inferential,
            closure_bundle.epistemic,
        ]
    ):
        failed_stage = failed_stage or ProtocolStage.CLOSURE
        residuals.append(
            Residual(
                code="closure_bundle_incomplete",
                kind=ResidualKind.INFERENCE_GAP,
                stage=ProtocolStage.CLOSURE,
                description="Closure bundle must satisfy structural, referential, inferential, and epistemic closure.",
                blocking=True,
                rank_ceiling=ConstitutionalRank.CANDIDATE,
                trace_ref=proposal.trace_id,
                reopen_condition="Complete all closure dimensions before certification.",
            )
        )

    rank_ceiling = min((residual.rank_ceiling for residual in residuals), default=ConstitutionalRank.ASSURED)
    certified_rank = min(proposal.proposed_rank, rank_ceiling)
    blocking_residuals = [residual for residual in residuals if residual.blocking]

    if blocking_residuals:
        status = TransitionStatus.BLOCKED
    elif residuals:
        status = TransitionStatus.SUSPENDED
    else:
        status = TransitionStatus.CERTIFIED

    transition_certificate: TransitionCertificate | None = None
    if (
        status == TransitionStatus.CERTIFIED
        and unit_certificate is not None
        and identity_certificate is not None
        and domain_contract is not None
        and relation_certificate is not None
        and scope_certificate is not None
        and closure_bundle is not None
    ):
        transition_certificate = TransitionCertificate(
            proposal_id=proposal.proposal_id,
            unit_certificate_id=unit_certificate.certificate_id,
            identity_certificate_id=identity_certificate.certificate_id,
            domain_id=domain_contract.domain_id,
            relation_certificate_id=relation_certificate.certificate_id,
            scope_certificate_id=scope_certificate.certificate_id,
            closure_bundle=closure_bundle,
            residual_ids=tuple(residual.code for residual in residuals),
            certified_rank=certified_rank,
            decision=status,
            constitution_version=constitution_version,
            trace_id=proposal.trace_id,
            reopen_conditions=("Any new defeater, domain drift, or evidence expiry reopens this certificate.",),
        )

    final_stage = failed_stage or (blocking_residuals[0].stage if blocking_residuals else None)
    return ProtocolDecision(
        status=status,
        failed_stage=final_stage,
        certified_rank=certified_rank,
        rank_ceiling=rank_ceiling,
        residuals=tuple(residuals),
        transition_certificate=transition_certificate,
    )
