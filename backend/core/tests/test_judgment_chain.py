"""The judgment chain is built from stored objects and never issues a compliance decision.

Expectations are fixed by hand from the kernel's laws, not read back from the module:
- no evidence  -> no trace candidate at all -> BLOCKED at TRACE_CANDIDATE (missing_trace_candidates),
  handoff HUMAN_REVIEW. (First hand expectation said EVIDENCE_BINDING; the kernel's no-jump law refuses
  earlier, at the trace stage, and that is the correct reading: nothing was ever bound.)
- one sound documentary evidence -> SUPPORTED, rank SUPPORTED, action NOT granted (threshold VERIFIED),
  handoff DEFERRAL_QUEUE: a document supports, it does not verify
- evidence without owner -> never becomes a trace (EVIDENCE_HAS_NO_OWNER) -> BLOCKED as if absent
- rejected evidence -> provenance broken -> rank ceiling CANDIDATE
- the platform's own `result` is reported as a declaration and does not move the judgment
"""

import datetime as dt

import pytest

from core.judgment_chain import (
    ACTION_MIN_RANK,
    chain_for_assessment,
    chain_for_requirement,
)
from core.models import (
    Actor,
    ComplianceAssessment,
    Evidence,
    EvidenceRevision,
    Framework,
    RequirementAssessment,
    RequirementNode,
)
from iam.models import Folder, User

TODAY = dt.date(2026, 11, 2)


@pytest.fixture
def world(db):
    folder = Folder.objects.create(name="chain-folder")
    framework = Framework.objects.create(
        name="ECC test", folder=folder, min_score=0, max_score=100
    )
    node = RequirementNode.objects.create(
        name="Cybersecurity policy",
        folder=folder,
        framework=framework,
        assessable=True,
        urn="urn:test:ecc:1-1-1",
        ref_id="1-1-1",
    )
    RequirementNode.objects.create(
        name="Heading",
        folder=folder,
        framework=framework,
        assessable=False,
        urn="urn:test:ecc:1-1",
    )
    ca = ComplianceAssessment.objects.create(
        name="CA", folder=folder, framework=framework, min_score=0, max_score=100
    )
    ras = ca.create_requirement_assessments()
    ra = next(r for r in ras if r.requirement_id == node.id)
    owner = User.objects.create_user(
        email="owner@example.com", password="Strong-Pass-123!"
    )
    return {
        "folder": folder,
        "framework": framework,
        "node": node,
        "ca": ca,
        "ra": ra,
        "owner": owner,
    }


def _evidence(
    world,
    name,
    *,
    owner=True,
    link="https://example.com/policy.pdf",
    status="approved",
    expiry=None,
):
    ev = Evidence.objects.create(
        name=name, folder=world["folder"], status=status, expiry_date=expiry
    )
    if owner:
        # Evidence owners are Actors; the User's actor is created by ActorSyncMixin on save
        ev.owner.add(Actor.objects.get(user=world["owner"]))
    if link:
        EvidenceRevision.objects.create(
            evidence=ev, folder=world["folder"], version=1, link=link
        )
    world["ra"].evidences.add(ev)
    return ev


def test_no_evidence_is_blocked_at_trace_candidate_and_routed_to_human_review(world):
    row = chain_for_requirement(world["ca"], world["ra"], TODAY)
    assert row["judgment"]["status"] == "BLOCKED"
    assert row["judgment"]["failed_stage"] == "TRACE_CANDIDATE"
    assert any(r["code"] == "missing_trace_candidates" for r in row["residuals"])
    assert row["action"]["granted"] is False
    assert row["handoff"]["route"] == "HUMAN_REVIEW"
    states = {s["stage"]: s["state"] for s in row["stages"]}
    assert (
        states["TRACE_CANDIDATE"] == "blocked"
        and states["EVIDENCE_BINDING"] == "not_reached"
    )
    assert states["REALITY_CANDIDATE"] == "reached"


def test_one_sound_document_supports_but_never_verifies(world):
    _evidence(world, "Policy v3")
    row = chain_for_requirement(world["ca"], world["ra"], TODAY)
    assert row["judgment"] == {
        "status": "SUPPORTED",
        "rank": "SUPPORTED",
        "rank_ceiling": "SUPPORTED",
        "failed_stage": "ACTION_LICENSE",
    }
    assert (
        row["action"]["granted"] is False
        and row["action"]["minimum_rank"] == ACTION_MIN_RANK.name
    )
    assert row["handoff"]["route"] == "DEFERRAL_QUEUE"
    assert any(r["code"] == "rank_below_action_threshold" for r in row["residuals"])
    assert (
        row["evidence"][0]["became_trace"] is True
        and row["evidence"][0]["owner"] == "owner@example.com"
    )


def test_evidence_without_owner_is_not_a_trace(world):
    _evidence(world, "Orphan doc", owner=False)
    row = chain_for_requirement(world["ca"], world["ra"], TODAY)
    assert (
        row["evidence"][0]["became_trace"] is False
        and row["evidence"][0]["reason"] == "EVIDENCE_HAS_NO_OWNER"
    )
    # an evidence that never became a trace leaves the kernel with no trace at all: same block as absence
    assert (
        row["judgment"]["status"] == "BLOCKED"
        and row["judgment"]["failed_stage"] == "TRACE_CANDIDATE"
    )


def test_rejected_evidence_caps_rank_at_candidate(world):
    _evidence(world, "Rejected doc", status="rejected")
    row = chain_for_requirement(world["ca"], world["ra"], TODAY)
    assert (
        row["judgment"]["rank_ceiling"] == "CANDIDATE"
        and row["judgment"]["rank"] == "CANDIDATE"
    )


def test_expired_evidence_lowers_ceiling_to_plausible(world):
    _evidence(world, "Old doc", expiry=dt.date(2025, 1, 1))
    row = chain_for_requirement(world["ca"], world["ra"], TODAY)
    assert row["judgment"]["rank_ceiling"] == "PLAUSIBLE"


def test_declared_result_does_not_move_the_judgment(world):
    # blocked example: the platform's own result field says compliant, the chain still has no evidence
    ra = world["ra"]
    ra.result = RequirementAssessment.Result.COMPLIANT
    ra.save(update_fields=["result"])
    row = chain_for_requirement(world["ca"], ra, TODAY)
    assert row["declared_result"] == "compliant"
    assert row["judgment"]["status"] == "BLOCKED"


def test_assessment_level_counts_and_no_percentage(world):
    _evidence(world, "Policy v3")
    data = chain_for_assessment(world["ca"], TODAY)
    assert data["counts"]["requirements"] == 1  # the heading is not assessable
    assert data["counts"]["by_judgment_status"] == {"SUPPORTED": 1}
    assert data["counts"]["by_failed_stage"] == {"ACTION_LICENSE": 1}
    assert data["counts"]["by_handoff_route"] == {"DEFERRAL_QUEUE": 1}
    flat = str(data)
    assert "percent" not in flat and "score" not in data["counts"]
    assert data["requirements"][0]["envelope"]["normative_source_ids"] == ["ECC"]
