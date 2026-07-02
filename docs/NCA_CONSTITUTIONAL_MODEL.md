# NCA Constitutional Model (Sanadcom)

This model is NCA-aligned and defines origin/branch applicability gates without claiming official certification.

## ECC
- role: general cybersecurity origin

## DCC
- origin: ECC
- effective_attribute: data asset lifecycle
- sabab: existence of organizational data assets and processing/storage/transfer
- conditions: data inventory, owner, classification, lifecycle scope
- blockers: no data scope, no data owner, missing classification
- qadih examples: IT asset is not necessarily data asset; policy alone does not prove runtime protection

## CCC
- origin: ECC
- effective_attribute: cloud service model and CSP/CST relation
- sabab: use of IaaS/PaaS/SaaS/cloud tenancy
- conditions: cloud asset inventory, shared responsibility matrix, CSP/CST contract, data location
- blockers: no cloud scope, missing shared responsibility
- qadih examples: CSP control cannot be claimed by CST without contract evidence

## CSCC
- origin: ECC
- effective_attribute: critical system status
- sabab: approved criticality designation
- conditions: criticality assessment, system boundary, BIA, owner
- blockers: no criticality approval, undefined system boundary
- qadih examples: business-important system is not automatically a critical system

## OTCC
- origin: ECC
- effective_attribute: OT/ICS operational or HSE impact
- sabab: existence of OT/ICS asset
- conditions: OT asset inventory, facility level, safety/HSE impact, OT boundary
- blockers: pure IT asset, missing OT boundary
- qadih examples: IT patch process cannot be copied to OT without safety review

## TCC
- origin: ECC
- effective_attribute: remote work / remote access
- sabab: remote access to organizational assets
- conditions: remote access policy, MFA, endpoint posture, logging
- blockers: no remote access scope, unmanaged device access
- qadih examples: VPN alone does not prove secure remote work
