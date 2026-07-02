# NCA Applicability Engine (Branch Opening Only)

This document defines the scope of the NCA applicability layer added in PR #90.

## What this layer does

- registers licensed NCA branches that may open from ECC origin:
  - DCC
  - CCC
  - CSCC
  - OTCC
  - TCC
- evaluates branch applicability using constitutional inputs:
  - scope signals
  - conditions
  - mani/blockers
  - qadih differences
- returns branch-opening states only:
  - `branch_applicable`
  - `branch_candidate`
  - `branch_blocked`
  - `branch_not_applicable`

## What this layer does not do

- does not issue compliance judgments
- does not issue certification or approval claims
- does not expose `action_allowed`
- does not perform evidence scoring
- does not add AI or RAG decision paths
- does not add UI, dashboards, or database migrations

## Constitutional position

This layer is the applicability gate before evidence-trace binding and ranked constitutional decisions.
It preserves governed flow by deciding whether a branch may open, and why, without claiming control verification.
