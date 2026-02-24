# برومبت إنتاج ملف التقديم الرسمي — SICO GRC Submission Dossier

> **ملف رسمي داخل المستودع** — يُستخدم مع Copilot / ChatGPT / أي مساعد كود لإنتاج
> ملف تقديم جاهز بصيغة Markdown (وقابل للتحويل إلى Word) وفق متطلبات السوق السعودي
> وبصياغة قانونية آمنة.

---

## Master Prompt

> استخدمه كما هو، وغيّر القيم بين الأقواس `{{...}}` فقط.

```text
أنت مستشار امتثال سيبراني سعودي + كاتب تقني قانوني + مهندس GRC تشغيلي.
مهمتك: إنشاء "ملف تقديم جاهز" (Submission Dossier) لمشروع SICO GRC بصيغة Markdown
احترافية قابلة للتحويل إلى Word، مخصص للعروض/العقود/التقييمات داخل السعودية.

## الهدف
إنتاج ملف تقديم عملي ومنظم يوضح:
- تموضع المنصة كـ "تشغيل امتثال سيبراني سعودي" وليس مجرد أداة GRC
- التوافق مع ECC / CCC (ومسار PDPL عند الحاجة)
- الدليل التشغيلي (Evidence-backed)
- الحوكمة التشغيلية (SLA / Runbooks / IR / Change / Upgrade)
- التقييم الحالي للفجوات وخطة المعالجة
- صياغة قانونية آمنة للاستخدام في العروض والعقود داخل السعودية

## سياق المشروع (ثابت)
اسم المشروع: {{SICO GRC Platform}}
الجهة/الفريق: {{SilverWolf + Zain Affiliate / BU2}}
نموذج الاستضافة: {{On-prem داخل السعودية / Sovereign / Private Cloud}}
النطاق التنظيمي الأساسي: {{ECC + CCC}}
النطاق الاختياري: {{PDPL إذا كان المشروع يشمل بيانات شخصية}}
لغة المخرجات: العربية الأساسية + مصطلحات إنجليزية عند الحاجة (ثنائي اللغة)
نمط الوثيقة: تنفيذي + تشغيلي + قابل للتدقيق

## قواعد حاكمة مهمة جدًا (التزم بها حرفيًا)
1) لا تستخدم أي صياغة توحي باعتماد رسمي غير مثبت.
   - ممنوع: "معتمد من NCA" أو "NCA Certified Platform" إلا إذا تم تزويدك بوثيقة رسمية صريحة.
   - استخدم بدلًا من ذلك:
     - "Aligned with NCA ECC/CCC"
     - "Mapped to NCA controls"
     - "Supports audit-ready evidence workflows"
     - "Designed for sovereign/on-prem deployment in Saudi Arabia"

2) لا تخترع معلومات.
   - أي معلومة غير موجودة في المدخلات تُكتب كـ:
     - [TODO]
     - [يتطلب تأكيد من الفريق]
     - [غير متوفر حاليًا]
   - لا تُنتج أسماء ضوابط أو أرقام مواد قانونية من عندك إن لم تُعطَ لك.

3) اجعل كل ادعاء قابلًا للإثبات:
   - اربط الادعاءات بـ Evidence Types أو Artefacts أو سياسات تشغيل
   - أظهر حالة التغطية: كامل / جزئي / خارج النطاق

4) الوثيقة يجب أن تكون قابلة للاستخدام مباشرة في:
   - العروض التنفيذية
   - ملفات المشتريات
   - ملاحق العقود
   - التقييمات الداخلية والخارجية

5) التزم بتصميم "تشغيل امتثال" (Managed Compliance Operations)، وليس فقط منصة تقنية.

## المدخلات المطلوبة (املأها من المشروع/المستودع)
استخدم المدخلات التالية إن كانت متوفرة:
- {{Client_Name}} = اسم العميل المستهدف أو "Template"
- {{Sector}} = بنك / صحة / تعليم / طاقة / حكومي / مزود سحابي / عام
- {{Deployment_Model}} = On-prem / Private Cloud / Hybrid
- {{Frameworks_In_Scope}} = ECC / CCC / PDPL
- {{Control_Library_Source}} = مسارات ملفات الضوابط (JSON/CSV/Docs)
- {{Cross_Mapping_Source}} = مسارات ملفات ECC↔CCC mapping
- {{Evidence_Catalog_Source}} = مسار Evidence Catalog
- {{Evidence_Policy_Source}} = مسار Evidence Policy
- {{Security_Reports}} = SAST/DAST/SBOM/SARIF/Pentest summaries (إن وجدت)
- {{Gap_Register_Source}} = ملف الفجوات الحالي
- {{Remediation_Plan_Source}} = خطة المعالجة
- {{SLA_Assumptions}} = ساعات الاستجابة / أوقات الخدمة / دعم الطوارئ
- {{Runbook_List}} = قائمة runbooks المتاحة
- {{Pricing_Model}} = Packs + add-ons + assumptions
- {{Legal_Constraints}} = صياغات قانونية/تجارية يجب الالتزام بها

إذا لم تتوفر بعض المدخلات:
- أنشئ أقسامًا كاملة لكن ضع placeholders واضحة جدًا [TODO]

## مخرجات مطلوبة (إلزامية)
أنشئ ملف Markdown واحد باسم:
docs/commercial/SICO_GRC_Submission_Dossier_{{Client_Name_or_Template}}.md

ويجب أن يحتوي بالترتيب على الأقسام التالية:

### 1) صفحة الغلاف
- عنوان الوثيقة
- اسم العميل/الجهة (أو Template)
- الإصدار (v1.0)
- التاريخ
- تصنيف الوثيقة (Confidential / Internal / Customer-facing)
- إعداد: {{Team_Name}}
- مراجعة واعتماد (Placeholders)

### 2) خطاب التوافق (Compliance Positioning Letter)
صياغة احترافية عربية (مع فقرة English short version) توضح:
- أن المنصة "تشغيل امتثال سيبراني سعودي"
- أنها تدعم ECC/CCC (وPDPL عند الانطباق)
- أنها توفر أدلة تشغيلية قابلة للتدقيق
- أنها تعمل بنشر سيادي/On-prem داخل السعودية
- أنها لا تدّعي اعتمادًا رسميًا غير موثق
- أنها قابلة للتقييم الداخلي/الخارجي

### 3) جدول ECC/CCC Mapping (جدول عملي)
أنشئ جدول Markdown منسقًا بالأعمدة التالية:
- Mapping_ID
- Framework
- Control_ID
- Control_Title_AR
- Control_Title_EN
- Covered_By_Module (module/feature/process)
- Coverage_Status (Complete / Partial / Out of Scope)
- Evidence_Type(s)
- Evidence_Frequency
- Owner_Role
- Notes / Gaps
- Reference_Artifact

ثم:
- أضف قسم "Baseline vs Delta" يوضح:
  - الضوابط الأساسية المشتركة
  - ضوابط CCC الإضافية (Cloud Delta)
  - أي تعارضات/فجوات تتطلب تخصيص

### 4) Evidence Policy (سياسة الأدلة)
اكتب سياسة تشغيلية عملية تشمل:
- الهدف والنطاق
- المبادئ (Completeness, Authenticity, Timeliness, Traceability, Bilingual readiness)
- أنواع الأدلة المقبولة
- معايير قبول/رفض الأدلة
- دورة حياة الدليل (Draft → Submitted → Validated → Expired/Archived)
- التواتر (شهري/ربع سنوي/سنوي/حسب الحدث)
- الحفظ والأرشفة (Retention)
- الأدوار والمسؤوليات (RACI مبسط)
- آلية التحقق والمراجعة
- التعامل مع الأدلة الحساسة
- إدارة التغييرات على الأدلة
- استثناءات السياسة وآلية اعتمادها

ثم أضف "Evidence Catalog Snapshot" كجدول مختصر:
- Evidence_Type
- Description
- Applicable_Frameworks
- Typical_Controls
- Retention
- Owner
- Validator

### 5) Security Attestation (إفادة أمنية للمنصة)
أنشئ قسمًا منظمًا يصف أمن المنصة نفسها (وليس فقط امتثال العميل):
- Architecture Summary (On-prem / Sovereign)
- IAM / RBAC
- Data Protection (at rest / in transit)
- Audit Logging
- Backup & Recovery
- Hardening Baseline
- Vulnerability Management
- Secure SDLC / CI Pipeline
- SBOM / SARIF / SAST / Secret Scanning
- Patch & Upgrade Policy
- Tenant/Data Isolation (إن وجد)
- Incident Handling for the Platform

ثم أضف "Evidence of Security Controls" كقائمة مراجع:
- Artifact name
- Type (Report / Screenshot / Config / Policy)
- Date
- Owner
- Verification status

### 6) Gap & Remediation (الفجوات وخطة المعالجة)
أنشئ سجل فجوات احترافي بالأعمدة:
- Gap_ID
- Category (Governance / Technical / Operational / Legal / Documentation)
- Severity (P0/P1/P2/P3)
- Description
- Impact
- Affected Framework(s)
- Recommended Action
- Owner
- ETA
- Status
- Dependency
- Verification Method

ثم أضف خطة معالجة مرحلية:
- Phase 1 (0-30 يوم)
- Phase 2 (31-60 يوم)
- Phase 3 (61-90 يوم)
مع مخرجات واضحة وقابلة للقياس (KPIs)

### 7) الصياغة القانونية الآمنة (للعروض والعقود)
أنشئ قسمًا جاهزًا للنسخ في العروض/العقود بعنوان:
"Legal-safe Commercial Wording (Saudi Market)"
ويشمل:
- عبارات مسموحة (Approved wording)
- عبارات ممنوعة (Avoid wording)
- صياغة نطاق الخدمة (Scope wording)
- صياغة حدود المسؤولية (Assumptions / Dependencies)
- صياغة التحديثات التنظيمية (Regulatory updates)
- صياغة الملكية الفكرية للخرائط/القوالب/المحتوى
- صياغة الخصوصية والسرية
- صياغة عدم تمثيل اعتماد حكومي غير موثق

### 8) ملاحق (Annexes)
أضف ملاحق جاهزة بعناوين فقط (حتى لو placeholders):
- Annex A: Detailed Control Coverage Matrix
- Annex B: Evidence Catalog (Full)
- Annex C: Runbooks List
- Annex D: SLA Matrix
- Annex E: Security Scan Summary
- Annex F: Deployment Topology
- Annex G: Change Management Workflow
- Annex H: Incident Response Workflow (Platform)

## تنسيق ومظهر الوثيقة
- استخدم عناوين واضحة H1/H2/H3
- استخدم جداول منظمة قدر الإمكان
- اجعل اللغة عربية احترافية مع المصطلحات التقنية بالإنجليزية بين قوسين عند الحاجة
- لا تستخدم جمل دعائية مبالغ فيها
- اكتب بأسلوب تنفيذي/تعاقدي/تشغيلي
- أضف "حالة البيانات" لكل قسم:
  - Confirmed
  - Draft
  - TODO

## معايير الجودة (Self-check قبل الإخراج)
قبل تسليم المخرجات، تحقق من الآتي:
- [ ] لا يوجد ادعاء "معتمد من NCA" بدون دليل
- [ ] كل قسم رئيسي موجود
- [ ] ECC/CCC Mapping موجود وفيه Coverage Status
- [ ] Evidence Policy عملية وليست نظرية فقط
- [ ] Security Attestation يغطي المنصة نفسها
- [ ] Gap Register يحتوي أولويات P0/P1/P2
- [ ] الصياغة القانونية آمنة
- [ ] توجد placeholders واضحة للنواقص
- [ ] الوثيقة قابلة للتحويل إلى Word مباشرة

## أسلوب الإخراج المطلوب
أخرج فقط:
1) محتوى ملف Markdown النهائي كاملًا
2) ثم قائمة قصيرة "Required Inputs to Finalize" توضح البيانات الناقصة [TODO]
3) ثم قائمة "Suggested Repo Paths" أين يُحفظ الملف وأي ملفات مرجعية يجب ربطها

لا تضف شروحات عامة خارج المطلوب.
```

---

## كيفية الاستخدام داخل المشروع

### 1) شغّل البرومبت في وضعين

| الوضع | الاستخدام |
|-------|-----------|
| **Template Mode** | بدون عميل محدد — لإنتاج نسخة عامة قابلة للتخصيص |
| **Client Mode** | مع `{{Client_Name}}`, `{{Sector}}`, `{{Deployment_Model}}` |

### 2) مسارات ملفات المشروع المرجعية

مرّر هذه المسارات للمساعد عند التشغيل:

| الغرض | المسار |
|-------|--------|
| مكتبة ضوابط ECC | `data/controls/ecc_controls.json` |
| مكتبة ضوابط CCC | `data/controls/ccc_controls.json` |
| مكتبة ضوابط PDPL | `data/controls/pdpl_controls.json` |
| خرائط ECC↔CCC | `data/mappings/ecc-ccc-baseline.yaml` |
| دلتا CCC | `data/mappings/ccc-delta.yaml` |
| كتالوج الأدلة | `data/evidence/evidence_catalog.json` |
| سياسة الأدلة | `data/evidence/evidence_policy.json` |
| وثائق الامتثال | `docs/compliance/` |
| التقارير الأمنية | `docs/security/` (SBOM/SARIF إن وجدت) |
| بيانات النشر | `deployment/` |

### 3) برومبت Copilot لـ VS Code (تنفيذ مباشر)

```text
Scan this repository and generate a Saudi-market GRC submission dossier in Markdown.

Target file:
docs/commercial/SICO_GRC_Submission_Dossier_Template.md

Use project files as sources of truth:
- data/controls/*
- data/mappings/*
- data/evidence/*
- docs/compliance/*
- docs/security/*
- deployment/*
- README.md

Requirements:
- Arabic-first professional document (with English technical terms when needed)
- Include sections: Cover Page, Compliance Positioning Letter, ECC/CCC Mapping,
  Evidence Policy, Security Attestation, Gap & Remediation, Legal-safe wording, Annexes
- Do NOT claim official NCA certification unless explicitly evidenced in repo
- Mark missing facts as [TODO]
- Produce audit-ready, procurement-ready, contract-safe wording
- Use structured tables and clear headings
- Keep all statements evidence-oriented and implementation-focused
```

---

## ملفات الإخراج المتوقعة

| الملف | الوصف |
|-------|-------|
| `docs/commercial/SICO_GRC_Submission_Dossier_Template.md` | النسخة العامة (Template) |
| `docs/commercial/SICO_GRC_Submission_Dossier_{{Client}}.md` | نسخة مخصصة للعميل |

---

*آخر تحديث: 2026-02-24 | الإصدار: v1.0 | الحالة: Confirmed*
