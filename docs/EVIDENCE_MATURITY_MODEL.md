# Evidence Maturity Model

This layer is an operational stage after NCA applicability and applicability follow-up planning.

It classifies evidence readiness and trace completeness without issuing any compliance judgment.
It is not a compliance status, not an NCA approval, and not an NCA certification layer.

## States

- `evidence_missing`
- `evidence_draft`
- `evidence_submitted`
- `evidence_attested`
- `evidence_validated`
- `evidence_expired`
- `evidence_rejected`
- `evidence_conflicting`

## Boundaries

- `evidence_validated` means internal evidence validation under internal policy only.
- `evidence_validated` does not mean compliant.
- `evidence_validated` does not mean certified.
- `evidence_validated` does not mean approved.
- This layer does not produce action gates.
- This layer does not produce compliance decisions.

## Sequence intent

This operational flow remains lightweight:

1. Applicability
2. Follow-up and scoping
3. Evidence maturity
4. Implementation assessment (later stage)
5. Governed decision bridge (later stage)
