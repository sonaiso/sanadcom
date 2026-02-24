# دليل إجراءات أمان التبعيات / Dependency Security SOP Guide

> **النطاق / Scope:** منصة SICO GRC – إدارة تحديثات أمان التبعيات  
> **الإصدار / Version:** 1.0  
> **تاريخ الإنشاء / Created:** 2026-02-24  
> **المرجع / Reference:** PR #48 – bump `cryptography` & `langchain-community`

---

## بنية المجلد / Folder Structure

```
docs/security-sop/
├── README.md                         ← هذا الملف / This file
├── SOP-dependency-security.md        ← الإجراء التشغيلي الرئيسي / Main SOP playbook
├── RACI-matrix.md                    ← مصفوفة المسؤوليات / Responsibility matrix
├── workflow-diagram.md               ← مخططات سير العمل / Workflow & state diagrams
└── templates/
    ├── onboarding-checklist.md       ← قائمة تأهيل المطورين الجدد / Developer onboarding
    ├── evidence-template.md          ← نموذج توثيق الأدلة / Evidence artifact template
    ├── approval-request.md           ← نموذج طلب الاعتماد / Approval request template
    └── submission-report.md          ← نموذج تقرير التسليم / Final submission report
```

---

## الغرض / Purpose

يوفر هذا المجلد الإجراءات التشغيلية الموحدة (SOPs) لإدارة تحديثات أمان تبعيات Python في مشروع SICO GRC. يستند إلى تجربة PR #48 التي عالجت CVEs حرجة في حزم `cryptography` و `langchain-community`.

This folder provides standardised operating procedures for managing Python dependency security updates in the SICO GRC project. It is grounded in the real experience of PR #48, which addressed critical CVEs in `cryptography` and `langchain-community`.

---

## كيفية الاستخدام / How to Use

| الحالة / Situation | الملف الموصى به / Recommended File |
|---|---|
| اكتشاف ثغرة جديدة / New vulnerability discovered | `SOP-dependency-security.md` → الخطوة 1 |
| تعيين المسؤوليات / Assign responsibilities | `RACI-matrix.md` |
| فهم دورة حياة المعالجة / Understand remediation lifecycle | `workflow-diagram.md` |
| تأهيل مطور جديد / Onboard a new developer | `templates/onboarding-checklist.md` |
| توثيق إصلاح ثغرة / Document a fix | `templates/evidence-template.md` |
| طلب اعتماد الدمج / Request merge approval | `templates/approval-request.md` |
| إعداد تقرير ختامي / Prepare final report | `templates/submission-report.md` |

---

## المعايير المطبقة / Applied Standards

- **ISO/IEC 27001:2022** – A.8.8 Management of technical vulnerabilities  
- **NIST SP 800-40 Rev. 4** – Guide to Enterprise Patch Management  
- **NCA ECC-1:2018** – متطلبات الأمن السيبراني للجهات الحكومية  
- **DevSecOps** – Shift-left security, automated scanning, gated deployments  

---

## المراجعة الدورية / Periodic Review

تُراجع هذه الوثائق كل **6 أشهر** أو عند حدوث:
- إصدار ثغرة CVSS ≥ 7.0 في تبعية رئيسية
- تغيير جوهري في البنية التحتية أو سلسلة CI/CD
- نتائج تدقيق أمني

These documents are reviewed every **6 months** or upon:
- A CVSS ≥ 7.0 vulnerability in a key dependency
- A material change to infrastructure or CI/CD pipeline
- Security audit findings

---

> 📌 **للمساهمة أو الاقتراح:** افتح Issue بعنوان `[SOP] <موضوع التغيير>` وأرفق تفاصيل المقترح.
