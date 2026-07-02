## Constitutional Governance Checklist

- [ ] I read AGENTS.md before making changes.
- [ ] This PR does not create a shortcut from requirement/metric/evidence/RAG/LLM output to compliance decision.
- [ ] Every new decision path uses or preserves the constitutional transition chain.
- [ ] Every allowed action has an explicit decision, rank, residual policy, and handoff rule where applicable.
- [ ] Missing evidence results in DEFERRED or lower rank, not ALLOWED.
- [ ] Active blockers/mani result in BLOCKED.
- [ ] Qadih differences downgrade rank or require human review.
- [ ] NCA wording is “aligned/mapped/evidence-ready”, not “certified/approved by NCA”.
- [ ] Tests were added or updated for governance-sensitive changes.
