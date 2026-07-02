## Constitutional Governance Checklist

- [ ] I read AGENTS.md before making changes.
- [ ] I did not introduce an agent instruction file that bypasses AGENTS.md.
- [ ] This PR does not weaken AGENTS.md or make it optional.
- [ ] I did not introduce direct requirement/metric/evidence/RAG/LLM-to-decision shortcuts.
- [ ] This PR does not create a shortcut from requirement/metric/evidence/RAG/LLM output to compliance decision.
- [ ] Every new decision path uses or preserves the constitutional transition chain.
- [ ] Every allowed action is produced by a governed decision object.
- [ ] Missing evidence produces DEFERRED or lower rank.
- [ ] Active blockers/mani produce BLOCKED.
- [ ] Qadih differences downgrade rank, create residuals, or require human review.
- [ ] Metrics are treated as evidence candidates, not compliance certificates.
- [ ] NCA wording is aligned/mapped/evidence-ready, not certified/approved.
- [ ] Tests were added or updated for governance-sensitive changes.
