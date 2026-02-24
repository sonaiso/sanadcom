# ملف التقديم الرسمي — SICO GRC Platform
# SICO GRC Submission Dossier

---

## صفحة الغلاف | Cover Page

| الحقل / Field | القيمة / Value |
|--------------|----------------|
| **عنوان الوثيقة** | ملف التقديم الرسمي لمنصة SICO GRC |
| **Document Title** | SICO GRC Platform — Submission Dossier |
| **العميل / Client** | Template (نسخة عامة قابلة للتخصيص) |
| **القطاع / Sector** | [TODO — بنك / صحة / طاقة / حكومي / عام] |
| **الإصدار / Version** | v1.0 |
| **التاريخ / Date** | 2026-02-24 |
| **تصنيف الوثيقة** | Confidential — Internal Use / Customer-Facing |
| **نموذج النشر** | On-prem داخل المملكة العربية السعودية / Sovereign Cloud |
| **الإطار التنظيمي** | NCA ECC + NCA CCC (+ PDPL عند الانطباق) |
| **إعداد / Prepared by** | SilverWolf + Zain Affiliate / BU2 |
| **مراجعة / Reviewed by** | [TODO — يتطلب تعيين مراجع] |
| **اعتماد / Approved by** | [TODO — يتطلب اعتماد مسؤول مفوّض] |

> **ملاحظة قانونية:** هذه الوثيقة سرية ومخصصة للاستخدام الداخلي أو تقديمها للعملاء المفوّضين فقط.
> تحتوي على معلومات تشغيلية وفنية وقانونية خاصة بمنصة SICO GRC.

> **Legal Note:** This document is confidential and intended for internal use or submission to
> authorized clients only. It contains operational, technical, and legal information proprietary
> to the SICO GRC Platform.

**حالة البيانات / Data Status:** Draft

---

## القسم الأول: خطاب التوافق | Compliance Positioning Letter

**حالة البيانات / Data Status:** Confirmed

### النسخة العربية

تمتلك منصة **SICO GRC** تصميمًا معماريًا وتشغيليًا متكاملًا يضعها في موقع **"تشغيل امتثال سيبراني سعودي"**
(Saudi Managed Compliance Operations)، لا مجرد أداة GRC تقنية.

**التوافق التنظيمي:**
تم تصميم المنصة وبناؤها بما يتوافق مع متطلبات **الضوابط الأساسية للأمن السيبراني (ECC)** و**الضوابط
السيبرانية للحوسبة السحابية (CCC)** الصادرة عن الهيئة الوطنية للأمن السيبراني (NCA)، مع إمكانية
توسعة النطاق ليشمل **نظام حماية البيانات الشخصية (PDPL)** عند انطباقه.

**النشر السيادي:**
تعمل المنصة بنموذج نشر **On-prem** أو **Private Cloud** داخل المملكة العربية السعودية، مما يضمن
السيادة الكاملة على البيانات وعدم خروجها خارج الحدود الجغرافية للمملكة.

**الأدلة التشغيلية:**
توفر المنصة أدلة تشغيلية قابلة للتدقيق (Audit-ready Evidence) مرتبطة بضوابط ECC/CCC بشكل
مباشر، مع دعم ثنائي اللغة (عربي/إنجليزي) لجميع المخرجات.

**إخلاء المسؤولية التنظيمية:**
لا تدّعي هذه الوثيقة ولا المنصة الحصول على اعتماد رسمي من الهيئة الوطنية للأمن السيبراني (NCA)
أو أي جهة حكومية أخرى، ما لم يُقدَّم دليل رسمي صريح على ذلك. يُستخدم مصطلح "متوافق مع"
(Aligned with) و"مُصمَّم وفق" (Designed to meet) بدلًا من "معتمد من" (Certified by).

**قابلية التقييم:**
المنصة مفتوحة للتقييم الداخلي والخارجي، وتوفر جميع الأدلة والتوثيق اللازمين لعمليات التدقيق
والمراجعة الدورية.

---

### English Short Version

**SICO GRC Platform** is architected and operated as a **Saudi Cybersecurity Managed Compliance
Operations** solution — not merely a technical GRC tool.

**Regulatory Alignment:** The platform is designed and built to be aligned with NCA ECC
(Essential Cybersecurity Controls) and NCA CCC (Cloud Cybersecurity Controls), with optional
coverage extension to PDPL when applicable.

**Sovereign Deployment:** The platform operates on an On-prem or Private Cloud deployment model
within the Kingdom of Saudi Arabia, ensuring full data sovereignty and no cross-border data transfers.

**Audit-ready Evidence:** The platform provides audit-ready, bilingual (Arabic/English) evidence
workflows directly mapped to ECC/CCC controls.

**Regulatory Disclaimer:** This document and the platform do not claim official NCA certification
or government endorsement unless explicitly evidenced by official documentation. Terminology used
includes: *"Aligned with NCA ECC/CCC"*, *"Mapped to NCA controls"*, *"Supports audit-ready
evidence workflows"*, and *"Designed for sovereign/on-prem deployment in Saudi Arabia"*.

**Auditability:** The platform is open to internal and external assessment, and provides all
required evidence and documentation for periodic audit and review.

---

## القسم الثاني: جدول تغطية ECC/CCC | ECC/CCC Control Mapping

**حالة البيانات / Data Status:** Confirmed (مستخرج من `data/controls/` و `data/mappings/`)

### 2.1 جدول الضوابط الأساسية | Core Controls Coverage Matrix

| Mapping_ID | Framework | Control_ID | Control_Title_AR | Control_Title_EN | Covered_By_Module | Coverage_Status | Evidence_Type(s) | Evidence_Frequency | Owner_Role | Notes / Gaps | Reference_Artifact |
|-----------|-----------|------------|-----------------|-----------------|-------------------|----------------|-----------------|-------------------|-----------|-------------|-------------------|
| MAP-001 | ECC | ECC-1-1-1 | استراتيجية الأمن السيبراني | Cybersecurity Strategy | Governance Module | Complete | governance_policy, audit_reports | Annual | Compliance Officer | تتطلب اعتماد من المسؤول المفوّض | data/controls/ecc_controls.json |
| MAP-002 | ECC | ECC-1-1-2 | خارطة طريق الاستراتيجية | Strategy Roadmap | Governance Module | Complete | governance_policy | Annual | Compliance Officer | — | data/controls/ecc_controls.json |
| MAP-003 | ECC | ECC-1-2-1 | هيكل تنظيمي للأمن السيبراني | Cybersecurity Organizational Structure | Governance Module | Complete | governance_policy, iam_policy | Annual | CISO | — | data/controls/ecc_controls.json |
| MAP-004 | ECC | ECC-1-3-1 | برنامج التوعية والتدريب | Awareness & Training Program | Compliance Module | Partial | training_records | Annual | Compliance Officer | برنامج التدريب يتطلب تخصيصًا إضافيًا | data/controls/ecc_controls.json |
| MAP-005 | ECC | ECC-1-5-1 | سجل مخاطر الأمن السيبراني | Cybersecurity Risk Register | Risk Module | Complete | risk_register | Quarterly | Risk Officer | — | data/controls/ecc_controls.json |
| MAP-006 | ECC | ECC-1-5-2 | معالجة مخاطر الأمن السيبراني | Cybersecurity Risk Treatment | Risk Module | Complete | risk_register | Quarterly | Risk Officer | — | data/controls/ecc_controls.json |
| MAP-007 | ECC | ECC-2-1-1 | سياسة الأمن السيبراني | Cybersecurity Policy | Policy Module | Complete | governance_policy | Annual | CISO | — | data/controls/ecc_controls.json |
| MAP-008 | ECC | ECC-2-3-1 | إدارة الهوية والوصول | Identity & Access Management | IAM Module | Complete | iam_policy, access_reviews | Quarterly | IT Security | — | data/controls/ecc_controls.json |
| MAP-009 | ECC | ECC-2-5-1 | أمن البنية التحتية | Infrastructure Security | Technical Module | Partial | vulnerability_scan, hardening_baseline | Monthly | IT Security | يتطلب مزيدًا من أدلة التصليب | data/controls/ecc_controls.json |
| MAP-010 | ECC | ECC-2-7-1 | أمن البيانات وحمايتها | Data Security & Protection | Data Protection Module | Complete | data_classification, encryption_config | Annual | Data Officer | — | data/controls/ecc_controls.json |
| MAP-011 | ECC | ECC-2-10-1 | إدارة مخاطر سلسلة التوريد | Supply Chain Risk Management | Third-Party Module | Partial | third_party_assessment | Annual | Procurement | [TODO] — تقييمات الطرف الثالث تحتاج مراجعة | data/controls/ecc_controls.json |
| MAP-012 | ECC | ECC-2-12-1 | مراقبة الأمن السيبراني | Cybersecurity Monitoring | SOC Module | Complete | security_logs, siem_reports | Continuous | SOC Analyst | — | data/controls/ecc_controls.json |
| MAP-013 | ECC | ECC-2-12-3 | سجلات الأحداث الأمنية | Security Event Logs | SOC Module | Complete | security_logs | Continuous | SOC Analyst | — | data/controls/ecc_controls.json |
| MAP-014 | ECC | ECC-3-1-1 | الاستجابة للحوادث السيبرانية | Cybersecurity Incident Response | IR Module | Complete | incident_response_plan, ir_test_records | Annual | IR Team | — | data/controls/ecc_controls.json |
| MAP-015 | ECC | ECC-3-3-1 | استمرارية الأعمال | Business Continuity | BCP Module | Partial | bcp_plan, dr_test_records | Annual | Business Continuity | [TODO] — اختبارات DR تحتاج توثيق | data/controls/ecc_controls.json |
| MAP-016 | CCC | CCC-1-1-P-1 | أدوار ومسؤوليات الأمن السيبراني السحابي (مزود) | Cloud Cybersecurity Roles — Provider | Governance Module | Complete | governance_policy, cloud_raci | Annual | Cloud Security Engineer | امتداد لـ ECC-1-4-1 | data/controls/ccc_controls.json |
| MAP-017 | CCC | CCC-1-1-T-1 | أدوار ومسؤوليات الأمن السيبراني السحابي (مستأجر) | Cloud Cybersecurity Roles — Tenant | Governance Module | Complete | governance_policy, cloud_raci | Annual | Tenant Admin | امتداد لـ ECC-1-4-1 | data/controls/ccc_controls.json |
| MAP-018 | CCC | CCC-1-2-P-1 | إدارة مخاطر سحابية (مزود) | Cloud Risk Management — Provider | Risk Module | Partial | risk_register, cloud_risk_assessment | Quarterly | Cloud Risk Officer | يتطلب تقييم مخاطر سحابي مخصص | data/controls/ccc_controls.json |
| MAP-019 | CCC | CCC-1-2-T-1 | إدارة مخاطر سحابية (مستأجر) | Cloud Risk Management — Tenant | Risk Module | Partial | risk_register, cloud_risk_assessment | Quarterly | Tenant Risk Owner | [TODO] — نموذج تقييم مخاطر المستأجر | data/controls/ccc_controls.json |
| MAP-020 | CCC | CCC-2-11-P-1 | سجلات أمن السحابة (مزود) | Cloud Security Logs — Provider | SOC Module | Complete | security_logs, cloud_audit_trail | Continuous | Cloud SOC | — | data/controls/ccc_controls.json |
| MAP-021 | CCC | CCC-2-11-T-1 | سجلات أمن السحابة (مستأجر) | Cloud Security Logs — Tenant | SOC Module | Complete | security_logs | Continuous | Tenant Admin | — | data/controls/ccc_controls.json |

> **ملاحظة:** الجدول أعلاه يمثل عينة من الضوابط الأكثر أهمية. الجدول الكامل متاح في الملحق A.
> المصادر: `data/controls/ecc_controls.json`، `data/controls/ccc_controls.json`،
> `data/mappings/ecc-ccc-baseline.yaml`، `data/mappings/ccc-delta.yaml`

---

### 2.2 ملخص التغطية | Coverage Summary

| الإطار / Framework | إجمالي الضوابط | مغطى كاملًا | مغطى جزئيًا | خارج النطاق |
|-------------------|---------------|------------|------------|------------|
| ECC | 45 | 32 | 10 | 3 |
| CCC | 24 | 14 | 8 | 2 |
| PDPL | [TODO] | [TODO] | [TODO] | [TODO] |

---

### 2.3 Baseline vs Delta

#### الضوابط الأساسية المشتركة (ECC Baseline ↔ CCC)

وفقًا لملف `data/mappings/ecc-ccc-baseline.yaml`، تتقاطع ECC وCCC في **40–60%** من المتطلبات،
مما يسمح بتطبيق واحد يخدم كلا الإطارين.

**أمثلة على التقاطع الكامل (Full Overlap):**
- استراتيجية الأمن السيبراني: `ECC-1-1` ↔ `CCC-1-1` (CCC يضيف متطلبات سحابية)
- الأدوار والمسؤوليات: `ECC-1-2` ↔ `CCC-1-2` (CCC يضيف أدوار سحابية محددة)
- معايير التشفير: `ECC-3-5` ↔ `CCC-9-1/9-2/9-3` (CCC أكثر تفصيلًا للبيانات السحابية)

#### ضوابط CCC الإضافية (Cloud Delta)

وفقًا لملف `data/mappings/ccc-delta.yaml`، تشمل الضوابط الحصرية لـ CCC:
- **35 ضابط** خاص بمزودي الخدمات السحابية (CSP Controls)
- **17 ضابط** خاص بمستهلكي الخدمات السحابية (CSC Controls)
- **15 ضابط** حوكمة سحابية إضافية (Cloud Governance Extensions)

#### الفجوات / التعارضات التي تتطلب تخصيصًا

| الفجوة | الإطار | الأولوية | ملاحظة |
|-------|--------|---------|--------|
| نماذج تقييم مخاطر المستأجر السحابي | CCC | P1 | [TODO] — يتطلب بناء نموذج مخصص |
| توثيق اختبارات الاستمرارية (DR) | ECC + CCC | P1 | موجود جزئيًا، يحتاج اكتمال |
| تقييمات الطرف الثالث (Supply Chain) | ECC | P2 | قيد التطوير |

---

## القسم الثالث: سياسة الأدلة | Evidence Policy

**حالة البيانات / Data Status:** Confirmed (مستخرج من `data/evidence/evidence_policy.json`)

**المرجع:** `data/evidence/evidence_policy.json` — الإصدار 1.0، تاريخ السريان: 2026-02-23

### 3.1 الهدف والنطاق

**الهدف:** تحدد هذه السياسة متطلبات جمع الأدلة وتخزينها والاحتفاظ بها لإثبات الامتثال للوائح
NCA ECC وNCA CCC وPDPL، وضمان جاهزية المنصة للتدقيق في أي وقت.

**النطاق:** تنطبق هذه السياسة على جميع الأدلة المجمّعة عبر منصة SICO GRC، وتشمل جميع الفرق
والإدارات التي تستخدم المنصة.

### 3.2 المبادئ الأساسية

| الرمز | المبدأ | الوصف |
|-------|--------|-------|
| EP-01 | **الاكتمال** (Completeness) | يجب أن تكون الأدلة كاملة وكافية لإثبات الامتثال الكامل لكل ضابط |
| EP-02 | **الأصالة** (Authenticity) | يجب أن تكون الأدلة أصلية وغير معدلة وقابلة للتتبع إلى مصدرها الأصلي |
| EP-03 | **التوقيت** (Timeliness) | يجب جمع الأدلة بالتكرار المطلوب والاحتفاظ بها طوال فترة الاحتفاظ الكاملة |
| EP-04 | **التوثيق ثنائي اللغة** (Bilingual Documentation) | جميع الأدلة تتضمن تسميات وبيانات وصفية بالعربية والإنجليزية |
| EP-05 | **الاحتفاظ** (Retention) | الاحتفاظ بجميع أدلة الامتثال لمدة لا تقل عن 7 سنوات وفق NCA |
| EP-06 | **قابلية التتبع** (Traceability) | ربط كل دليل بضابط محدد ومالك وتاريخ جمع |

### 3.3 أنواع الأدلة المقبولة

| نوع الدليل | الأشكال المقبولة | ملاحظات |
|-----------|----------------|---------|
| وثائق السياسات | PDF, DOCX | يجب أن تحمل توقيعًا أو ختمًا رسميًا |
| سجلات الأحداث | LOG, CSV, JSON | يُقبل التصدير الآلي من الأنظمة |
| تقارير التدقيق | PDF, XLSX | يجب أن تشمل توصيات ومسار المعالجة |
| نتائج الفحص الأمني | PDF, JSON, SARIF, HTML | SAST/DAST/Pentest |
| لقطات الشاشة | PNG, JPG | مع ختم التاريخ والوقت |
| ملفات الإعداد | YAML, JSON, XML | مع توثيق نسخة النظام |
| سجلات التدريب | PDF, CSV | مع توقيع المتدربين |
| محاضر الاجتماعات | PDF, DOCX | مع قائمة الحضور |

### 3.4 معايير قبول ورفض الأدلة

#### ✅ معايير القبول
- الدليل مرتبط بضابط محدد في ECC/CCC/PDPL
- يحمل تاريخ إنشاء/جمع واضح ضمن الفترة المطلوبة
- صادر من مصدر موثوق وقابل للتحقق
- يشمل البيانات الوصفية الثنائية اللغة
- اكتمال البيانات ≥ 80%

#### ❌ معايير الرفض
- الدليل منتهي الصلاحية (خارج فترة التواتر المطلوبة)
- يفتقر إلى بيانات التعريف الأساسية (تاريخ، مصدر، مالك)
- يحتوي على بيانات متعارضة أو غير قابلة للتحقق
- لا يرتبط بأي ضابط امتثال محدد
- محتوى غير مكتمل أو مبتور

### 3.5 دورة حياة الدليل

```
Draft → Submitted → Under Review → Validated ✅
                                 → Rejected ❌ → Revised → Re-submitted
                    
Validated → Active → Expired → Archived
```

| المرحلة | الوصف | المسؤول | المدة |
|---------|-------|---------|-------|
| **Draft** | الدليل قيد الإعداد | مالك الدليل | مفتوح |
| **Submitted** | تم تقديم الدليل للمراجعة | مالك الدليل | — |
| **Under Review** | قيد المراجعة من مسؤول الامتثال | Compliance Officer | ≤ 5 أيام عمل |
| **Validated** | تم التحقق والاعتماد | Compliance Officer | — |
| **Rejected** | مرفوض مع ملاحظات | Compliance Officer | — |
| **Active** | الدليل ساري وفعّال | System | حتى انتهاء الصلاحية |
| **Expired** | انتهت صلاحيته، يحتاج تجديد | System | — |
| **Archived** | محفوظ للرجوع إليه | Compliance Officer | وفق جدول الاحتفاظ |

### 3.6 التواتر وجدول الاحتفاظ

| الإطار | نوع الدليل | تواتر الجمع | مدة الاحتفاظ |
|--------|-----------|------------|-------------|
| ECC | سجلات الأمن | مستمر (Continuous) | سنة واحدة |
| ECC | تقارير التدقيق | سنوي | 7 سنوات |
| ECC | السياسات والإجراءات | سنوي | 7 سنوات |
| ECC | تقييمات المخاطر | ربع سنوي | 5 سنوات |
| ECC | سجلات التدريب | سنوي | 5 سنوات |
| CCC | سجلات الإعداد السحابي | نصف سنوي | 5 سنوات |
| CCC | تقارير اختبار الاختراق | سنوي | 3 سنوات |
| CCC | سجلات إدارة المفاتيح | مستمر | 7 سنوات |
| PDPL | سجلات الموافقة | عند الإنشاء | 7 سنوات |
| PDPL | سجلات المعالجة | مستمر | 7 سنوات |
| PDPL | تقارير DPIA | عند التغيير | 7 سنوات |
| PDPL | إخطارات الاختراق | عند الحدث | 7 سنوات |

### 3.7 الأدوار والمسؤوليات (RACI)

| النشاط | Compliance Officer | IT Security | Risk Officer | Data Officer | Auditor |
|-------|-------------------|------------|-------------|-------------|---------|
| جمع الأدلة | C | R | C | C | I |
| مراجعة الأدلة | R | C | C | C | I |
| اعتماد الأدلة | A | I | I | I | I |
| حفظ وأرشفة | R | A | I | I | I |
| التدقيق الدوري | C | I | C | I | R |
| إدارة الاستثناءات | A | C | R | C | I |

*R: Responsible | A: Accountable | C: Consulted | I: Informed*

### 3.8 التعامل مع الأدلة الحساسة

- الأدلة التي تحتوي على بيانات شخصية تخضع لمتطلبات PDPL الإضافية
- يتم تشفير الأدلة الحساسة أثناء التخزين والنقل
- يقتصر الوصول على المصرح لهم بناءً على مبدأ الحد الأدنى من الصلاحيات (Least Privilege)
- يتم تسجيل جميع عمليات الوصول والتعديل في سجل التدقيق

### 3.9 إدارة الاستثناءات

- تقدم طلبات الاستثناء كتابيًا للـ Compliance Officer
- يجب توثيق المبرر التجاري وتقييم المخاطر
- مدة الاستثناء لا تتجاوز 90 يومًا
- يتطلب اعتماد CISO وتسجيل في سجل الاستثناءات

### 3.10 Evidence Catalog Snapshot

| Evidence_Type | الوصف | Applicable_Frameworks | Typical_Controls | Retention | Owner | Validator |
|--------------|-------|----------------------|-----------------|-----------|-------|---------|
| governance_policy | وثيقة سياسة الحوكمة المعتمدة | ECC, CCC | ECC-1-1-1, ECC-1-2-1 | 7 سنوات | Compliance Officer | CISO |
| security_logs | سجلات الأحداث الأمنية | ECC, CCC, PDPL | ECC-2-12-3, CCC-2-11-P-1 | 1 سنة | SOC Analyst | IT Security |
| risk_register | سجل مخاطر الأمن السيبراني | ECC, CCC | ECC-1-5-1, CCC-1-2-P-1 | 5 سنوات | Risk Officer | Compliance Officer |
| iam_policy | سياسة إدارة الهوية والوصول | ECC, CCC | ECC-2-3-1 | 7 سنوات | IT Security | CISO |
| vulnerability_scan | تقرير فحص الثغرات | ECC, CCC | ECC-2-5-1 | 3 سنوات | IT Security | Compliance Officer |
| incident_response_plan | خطة الاستجابة للحوادث | ECC, CCC | ECC-3-1-1 | 7 سنوات | IR Team | CISO |
| training_records | سجلات التدريب والتوعية | ECC | ECC-1-3-1 | 5 سنوات | HR / Compliance | Compliance Officer |
| audit_reports | تقارير التدقيق الداخلي/الخارجي | ECC, CCC, PDPL | متعدد | 7 سنوات | Internal Audit | External Auditor |
| bcp_plan | خطة استمرارية الأعمال | ECC, CCC | ECC-3-3-1 | 7 سنوات | Business Continuity | Compliance Officer |
| data_classification | سجل تصنيف البيانات | ECC, CCC, PDPL | ECC-2-7-1 | 5 سنوات | Data Officer | CISO |
| third_party_assessment | تقييم أمان الطرف الثالث | ECC | ECC-2-10-1 | 3 سنوات | Procurement | Compliance Officer |
| encryption_config | إعدادات التشفير وإدارة المفاتيح | ECC, CCC | ECC-3-5-1, CCC-9-1 | 7 سنوات | IT Security | Compliance Officer |
| access_reviews | مراجعات صلاحيات الوصول | ECC, CCC | ECC-2-3-1 | 5 سنوات | IT Security | IT Manager |
| cloud_audit_trail | سجلات التدقيق السحابي | CCC | CCC-2-11-P-1 | 5 سنوات | Cloud Admin | Cloud Security |

*المرجع الكامل:* `data/evidence/evidence_catalog.json`

---

## القسم الرابع: الإفادة الأمنية للمنصة | Security Attestation

**حالة البيانات / Data Status:** Confirmed (جزئي) + [TODO] للتفاصيل المحددة

> **تنبيه:** هذا القسم يصف أمن **منصة SICO GRC نفسها** (البنية التحتية والتطبيق)، وليس فقط
> امتثال العميل الذي تديره المنصة.

### 4.1 ملخص البنية المعمارية | Architecture Summary

| العنصر | التفاصيل |
|--------|---------|
| **نموذج النشر** | On-prem / Private Cloud / Sovereign Deployment |
| **موقع البيانات** | داخل المملكة العربية السعودية (KSA-only) |
| **المكوّنات الرئيسية** | FastAPI Backend + Next.js 14 Frontend + PostgreSQL + Redis |
| **عزل المستأجرين** | بيئة مخصصة لكل عميل (Dedicated Tenant Isolation) |
| **الشبكة** | تشغيل محلي بدون اتصال خارجي إلزامي |

### 4.2 إدارة الهوية والوصول | IAM / RBAC

| السمة | التنفيذ الحالي |
|------|--------------|
| **المصادقة** | JWT Tokens مع انتهاء صلاحية قصير المدى |
| **التفويض** | RBAC (Role-Based Access Control) متعدد المستويات |
| **الأدوار** | Admin, CISO, Compliance Officer, Auditor, Viewer |
| **MFA** | [TODO — يتطلب تأكيد التطبيق أو الخارطة الزمنية] |
| **إدارة الجلسات** | انتهاء تلقائي + سجل التدقيق لكل دخول |
| **إدارة الصلاحيات** | مبدأ الحد الأدنى (Least Privilege) |

### 4.3 حماية البيانات | Data Protection

| الجانب | التفاصيل |
|-------|---------|
| **التشفير في الراحة (At Rest)** | [TODO — AES-256 أو مكافئ، يتطلب تأكيد التطبيق] |
| **التشفير أثناء النقل (In Transit)** | TLS 1.2/1.3 لجميع الاتصالات |
| **إدارة المفاتيح (Key Management)** | [TODO — يتطلب توثيق آلية إدارة المفاتيح] |
| **تصنيف البيانات** | متاح من خلال Data Classification Module |
| **إخفاء البيانات (Masking)** | [TODO — يتطلب تأكيد لسجلات الامتثال الحساسة] |

### 4.4 سجلات التدقيق | Audit Logging

- تسجيل جميع عمليات المستخدمين (CRUD) مع الطابع الزمني وعنوان IP
- سجلات تدقيق غير قابلة للتعديل (Immutable Audit Trail)
- مدة الاحتفاظ بسجلات التدقيق: وفق جدول احتفاظ المنصة
- دعم تصدير السجلات بصيغ: JSON, CSV, SIEM-compatible

### 4.5 النسخ الاحتياطي والاسترداد | Backup & Recovery

| المعلمة | القيمة |
|--------|-------|
| **RPO (Recovery Point Objective)** | [TODO — يتطلب تحديد الهدف] |
| **RTO (Recovery Time Objective)** | [TODO — يتطلب تحديد الهدف] |
| **تكرار النسخ الاحتياطي** | [TODO — يومي/أسبوعي؟] |
| **مكان التخزين** | داخل المملكة العربية السعودية |
| **اختبارات الاسترداد** | [TODO — توثيق آخر اختبار] |

### 4.6 صلابة البنية (Hardening Baseline)

- تطبيق CIS Benchmarks أو مكافئ للأنظمة الرئيسية [TODO — يتطلب تأكيد التطبيق]
- إزالة الخدمات والمنافذ غير الضرورية
- تحديثات أمنية دورية مع سياسة Patch Management موثقة
- مراجعة إعدادات الأمان ضمن دورة SDLC

### 4.7 إدارة الثغرات | Vulnerability Management

| النشاط | التكرار | الأداة |
|-------|--------|-------|
| فحص الثغرات (Vulnerability Scanning) | شهري | [TODO — أداة محددة] |
| اختبار الاختراق (Penetration Testing) | سنوي | [TODO — فريق داخلي/خارجي] |
| SAST (Static Application Security Testing) | مع كل CI/CD | GitHub Actions / [TODO] |
| DAST (Dynamic Application Security Testing) | ربع سنوي | [TODO] |
| Secret Scanning | مستمر | GitHub Secret Scanning |
| SBOM (Software Bill of Materials) | مع كل إصدار | [TODO] |

### 4.8 سلسلة CI/CD الآمنة | Secure SDLC / CI Pipeline

- مستودع الكود يستخدم GitHub مع Branch Protection Rules
- مراجعة الكود إلزامية (Code Review) قبل الدمج
- فحص الأسرار (Secret Scanning) تلقائي في كل Commit
- SAST مدمج في Pipeline
- SARIF Reports مدعوم للتقارير الأمنية

### 4.9 سياسة التصحيح والترقية | Patch & Upgrade Policy

- تصنيف التصحيحات: Critical (24 ساعة), High (7 أيام), Medium (30 يوم), Low (90 يوم)
- اختبار التصحيحات في بيئة Staging قبل الإنتاج
- توثيق كل ترقية في Change Log
- [TODO — نموذج Change Management الرسمي]

### 4.10 الاستجابة للحوادث (للمنصة) | Incident Handling for the Platform

| المرحلة | الوصف | المسؤول |
|--------|-------|---------|
| الكشف | مراقبة مستمرة عبر SOC Module | SOC Analyst |
| الاحتواء | عزل تلقائي + تنبيهات فورية | IT Security |
| التحقيق | تحليل سجلات التدقيق والأحداث | IR Team |
| الاسترداد | استعادة الخدمة وفق RTO | IT Operations |
| التوثيق | تقرير حادثة شامل ثنائي اللغة | Compliance Officer |
| المراجعة | تحليل ما بعد الحادثة (Post-Incident Review) | CISO |

### 4.11 أدلة ضوابط الأمان | Evidence of Security Controls

| اسم القطعة (Artifact) | النوع | التاريخ | المالك | حالة التحقق |
|----------------------|-------|--------|-------|------------|
| CI/CD Pipeline Configuration | Config | 2026-02-24 | DevOps Lead | Confirmed |
| GitHub Secret Scanning Logs | Report | 2026-02-24 | Security Lead | Confirmed |
| RBAC Role Definitions | Config | 2026-02-24 | IT Security | Confirmed |
| TLS Certificate Configuration | Config | [TODO] | IT Security | [TODO] |
| Vulnerability Scan Report | Report | [TODO] | IT Security | [TODO] |
| Penetration Test Report | Report | [TODO] | External Auditor | [TODO] |
| SBOM Export | Report | [TODO] | DevOps Lead | [TODO] |
| SARIF Security Report | Report | [TODO] | Security Lead | [TODO] |
| Backup & Recovery Test Records | Report | [TODO] | IT Operations | [TODO] |
| Hardening Baseline Checklist | Config | [TODO] | IT Security | [TODO] |

---

## القسم الخامس: سجل الفجوات وخطة المعالجة | Gap & Remediation

**حالة البيانات / Data Status:** Draft (يتطلب مراجعة الفريق وتحديث الحالة)

### 5.1 سجل الفجوات | Gap Register

| Gap_ID | Category | Severity | الوصف | التأثير | Affected Framework(s) | Recommended Action | Owner | ETA | Status | Dependency | Verification Method |
|--------|----------|---------|------|--------|----------------------|-------------------|-------|-----|--------|-----------|-------------------|
| GAP-001 | Documentation | P0 | غياب وثيقة اختبار DR (Disaster Recovery) رسمية | عدم القدرة على إثبات استمرارية الأعمال | ECC, CCC | إجراء اختبار DR موثق وتحديث BCP | Business Continuity | 30 يوم | Open | IT Operations | نتائج اختبار DR موقّعة |
| GAP-002 | Technical | P0 | عدم اكتمال توثيق التشفير في الراحة (At Rest) | مخاطر على سرية البيانات | ECC, CCC | توثيق آلية تشفير قاعدة البيانات وملفات النظام | IT Security | 14 يوم | Open | — | فحص إعدادات التشفير |
| GAP-003 | Technical | P1 | غياب تقرير اختبار الاختراق الأخير (Pentest) | لا يمكن إثبات مقاومة المنصة للهجمات | ECC, CCC | تكليف فريق Pentest خارجي أو داخلي | CISO | 60 يوم | Open | ميزانية معتمدة | تقرير Pentest رسمي |
| GAP-004 | Technical | P1 | غياب MFA (Multi-Factor Authentication) للمستخدمين المميزين | خطر الوصول غير المصرح به لحسابات مميزة | ECC, CCC | تطبيق MFA لجميع الحسابات المميزة (Admin, CISO) | IT Security | 30 يوم | Open | — | سياسة MFA موثقة + اختبار |
| GAP-005 | Operational | P1 | عدم اكتمال تقييمات مخاطر المستأجر السحابي | ثغرات في إدارة المخاطر السحابية | CCC | بناء نموذج تقييم مخاطر سحابي مخصص | Cloud Risk Officer | 45 يوم | Open | CCC Mapping | تقييم مخاطر سحابي موثق |
| GAP-006 | Operational | P1 | نقص في تقييمات الطرف الثالث (Supply Chain) | مخاطر من موردي البرمجيات وأطراف ثالثة | ECC | بناء برنامج تقييم أمان الطرف الثالث | Procurement | 60 يوم | Open | قائمة الموردين | تقارير تقييم موردين |
| GAP-007 | Documentation | P1 | غياب SBOM (Software Bill of Materials) رسمي | عدم القدرة على تتبع مكونات البرمجيات والثغرات | ECC, CCC | إنتاج SBOM آلي مع كل إصدار في CI/CD | DevOps Lead | 21 يوم | Open | CI/CD Pipeline | SBOM Export في المستودع |
| GAP-008 | Governance | P2 | عدم اكتمال نموذج Change Management الرسمي | مخاطر التغييرات غير المدارة في الإنتاج | ECC, CCC | توثيق وتطبيق Change Management Workflow | IT Operations | 45 يوم | Open | — | موافقات التغيير الموثقة |
| GAP-009 | Technical | P2 | عدم توثيق RPO/RTO رسميًا | لا يمكن قياس أو ضمان مستويات الاسترداد | ECC, CCC | تحديد وتوثيق RPO/RTO ضمن BCP | Business Continuity | 30 يوم | Open | GAP-001 | BCP موثق ومعتمد |
| GAP-010 | Legal | P2 | [TODO] — مراجعة قانونية لبنود الخصوصية في عقود العملاء | مخاطر قانونية تحت PDPL | PDPL | مراجعة العقود مع مستشار قانوني | Legal / Compliance | 60 يوم | Open | مستشار قانوني | عقود معتمدة قانونيًا |
| GAP-011 | Documentation | P2 | غياب Runbooks موثقة لعمليات الطوارئ | صعوبة الاستجابة السريعة للحوادث | ECC, CCC | إعداد وتوثيق Runbooks للعمليات الحرجة | IT Operations | 45 يوم | Open | — | مكتبة Runbooks معتمدة |
| GAP-012 | Technical | P3 | عدم اكتمال فحص DAST (Dynamic Testing) | ثغرات محتملة غير مكتشفة في وقت التشغيل | ECC, CCC | دمج DAST في دورة CI/CD الدورية | DevOps Lead | 90 يوم | Open | GAP-003 | تقارير DAST دورية |

---

### 5.2 خطة المعالجة المرحلية | Phased Remediation Plan

#### المرحلة الأولى (0–30 يوم) — الأولويات الحرجة

| المهمة | المسؤول | KPI |
|-------|---------|-----|
| توثيق التشفير في الراحة (At Rest) — GAP-002 | IT Security | وثيقة تشفير معتمدة من CISO |
| تطبيق MFA للحسابات المميزة — GAP-004 | IT Security | 100% من حسابات Admin/CISO مع MFA |
| إجراء اختبار DR موثق — GAP-001 | Business Continuity | تقرير اختبار DR + خطة BCP محدثة |
| إنتاج SBOM آلي — GAP-007 | DevOps Lead | SBOM Export في كل Pipeline Build |
| تحديد RPO/RTO — GAP-009 | Business Continuity | قيم RPO/RTO موثقة ومعتمدة |

**المخرجات القابلة للقياس:**
- 5 فجوات P0/P1 مغلقة أو في مرحلة متقدمة
- رفع نسبة تغطية ECC من 71% إلى ≥ 80%

---

#### المرحلة الثانية (31–60 يوم) — التحسينات التشغيلية

| المهمة | المسؤول | KPI |
|-------|---------|-----|
| تكليف وإجراء Pentest — GAP-003 | CISO | تقرير Pentest رسمي |
| بناء نموذج مخاطر المستأجر السحابي — GAP-005 | Cloud Risk Officer | نموذج مخاطر سحابي معتمد |
| برنامج تقييم الطرف الثالث — GAP-006 | Procurement | تقييم أول 5 موردين رئيسيين |
| توثيق Change Management Workflow — GAP-008 | IT Operations | Workflow معتمد ومطبق |
| المراجعة القانونية لعقود PDPL — GAP-010 | Legal | عقود نموذجية معدّلة |

**المخرجات القابلة للقياس:**
- إغلاق 4 فجوات P1 إضافية
- الحصول على تقرير Pentest لا توجد فيه ثغرات High/Critical غير معالجة

---

#### المرحلة الثالثة (61–90 يوم) — الاكتمال والنضج

| المهمة | المسؤول | KPI |
|-------|---------|-----|
| إعداد مكتبة Runbooks — GAP-011 | IT Operations | ≥ 10 Runbooks موثقة ومعتمدة |
| دمج DAST في CI/CD — GAP-012 | DevOps Lead | تقرير DAST أول في Pipeline |
| مراجعة شاملة لجميع الفجوات المفتوحة | Compliance Officer | Gap Register محدث بالكامل |
| تقرير حالة امتثال شامل | Compliance Officer | Compliance Dashboard ≥ 90% تغطية |

**المخرجات القابلة للقياس:**
- إغلاق جميع فجوات P1 وأغلب P2
- تغطية ECC ≥ 90%، تغطية CCC ≥ 85%
- المنصة جاهزة للتدقيق الخارجي

---

## القسم السادس: الصياغة القانونية الآمنة | Legal-safe Commercial Wording

**حالة البيانات / Data Status:** Confirmed

> هذا القسم جاهز للنسخ في العروض والعقود داخل السوق السعودي.

### 6.1 العبارات المسموحة | Approved Wording

يُوصى باستخدام العبارات التالية حصرًا عند وصف المنصة في العروض والعقود:

**بالعربية:**
- "منصة متوافقة مع متطلبات الهيئة الوطنية للأمن السيبراني (NCA)"
- "مصممة وفق ضوابط الأمن السيبراني الأساسية (ECC) والضوابط السيبرانية للحوسبة السحابية (CCC)"
- "توفر بيئة عمل جاهزة للتدقيق (Audit-ready)"
- "تدعم متطلبات الامتثال للأطر التنظيمية السعودية"
- "تعمل بنموذج نشر سيادي داخل المملكة العربية السعودية"
- "قابلة للتقييم الداخلي والخارجي"
- "توفر أدلة تشغيلية قابلة للتتبع والتحقق"

**بالإنجليزية:**
- "Aligned with NCA ECC and CCC requirements"
- "Mapped to NCA cybersecurity controls"
- "Supports audit-ready evidence workflows"
- "Designed for sovereign/on-prem deployment in Saudi Arabia"
- "Supports compliance management for ECC/CCC frameworks"
- "Evidence-backed compliance operations platform"

---

### 6.2 العبارات الممنوعة | Avoid Wording

❌ **لا تستخدم هذه العبارات** في غياب وثائق اعتماد رسمية:

| العبارة الممنوعة | البديل الآمن |
|----------------|-------------|
| "معتمد من NCA" | "متوافق مع متطلبات NCA" |
| "NCA Certified Platform" | "Aligned with NCA ECC/CCC" |
| "نظام امتثال رسمي معتمد" | "منظومة تشغيل امتثال سيبراني" |
| "ضامن الامتثال التنظيمي" | "يدعم تحقيق الامتثال التنظيمي" |
| "100% امتثال ECC/CCC" | "تغطية واسعة لضوابط ECC/CCC (تفاصيل في الملحق A)" |
| "معتمد حكوميًا" | "مصمم وفق المتطلبات الحكومية السعودية" |

---

### 6.3 صياغة نطاق الخدمة | Scope Wording

```
نطاق الخدمة:
تشمل الخدمة المقدمة إدارة وتشغيل منصة SICO GRC لدعم متطلبات الامتثال السيبراني وفق:
(أ) ضوابط الأمن السيبراني الأساسية (ECC)، إصدار 3:2018
(ب) الضوابط السيبرانية للحوسبة السحابية (CCC)، إصدار 2:2024
(ج) نظام حماية البيانات الشخصية (PDPL) — عند انطباقه وبناءً على اتفاق خاص

تشمل الخدمة: [قائمة الميزات/الوحدات المتفق عليها]
لا تشمل الخدمة: الاستشارات القانونية، التدقيق الخارجي، الاعتراض على قرارات الجهات التنظيمية
```

---

### 6.4 صياغة حدود المسؤولية | Assumptions & Dependencies

```
الافتراضات والتبعيات:
1. يتحمل العميل المسؤولية الكاملة عن دقة البيانات المدخلة في المنصة.
2. مسؤولية الامتثال التنظيمي النهائي تقع على عاتق العميل.
3. تقتصر مسؤولية المزود على ضمان عمل المنصة وفق المواصفات التقنية المتفق عليها.
4. أي تغييرات في اللوائح التنظيمية قد تتطلب تحديثات إضافية تُتفاوض بشكل منفصل.
5. يُشترط لتفعيل الضمانات التشغيلية أن تكون البيئة مُثبَّتة وفق متطلبات النشر الرسمية.
```

---

### 6.5 صياغة التحديثات التنظيمية | Regulatory Updates

```
إدارة التحديثات التنظيمية:
يلتزم المزود بمراقبة التحديثات الصادرة عن الهيئة الوطنية للأمن السيبراني (NCA) وتقييم
أثرها على المنصة. عند صدور تحديثات جوهرية، يُبلَّغ العميل خلال [30] يوم عمل، وتُقدَّم
خطة تحديث بما يتضمن الجدول الزمني والتكاليف المرتبطة إن وجدت.
```

---

### 6.6 صياغة الملكية الفكرية | Intellectual Property

```
الملكية الفكرية:
- خرائط الضوابط (Control Mappings) وقوالب الامتثال ومحتوى المنصة: ملكية حصرية للمزود.
- البيانات التشغيلية والأدلة المجمّعة من قِبَل العميل عبر المنصة: ملكية العميل الحصرية.
- لا يحق للعميل إعادة توزيع خرائط الضوابط أو قوالب المنصة لأطراف ثالثة دون موافقة خطية.
- يحتفظ المزود بحق تطوير المنصة وتحديث المحتوى التنظيمي دون إشعار مسبق، شريطة
  عدم الإخلال بالالتزامات التعاقدية.
```

---

### 6.7 صياغة الخصوصية والسرية | Privacy & Confidentiality

```
الخصوصية والسرية:
1. جميع البيانات المُعالَجة عبر المنصة تخضع لأحكام سرية صارمة.
2. لا تُنقل البيانات خارج حدود المملكة العربية السعودية.
3. يلتزم المزود بأحكام نظام حماية البيانات الشخصية (PDPL) فيما يخص البيانات الشخصية.
4. يُحظر على موظفي المزود الوصول إلى بيانات العميل إلا لأغراض الدعم التقني المصرح به.
5. يوقّع جميع موظفي المزود المتعاملين مع بيانات العميل على اتفاقية عدم إفصاح (NDA).
```

---

### 6.8 إخلاء مسؤولية الاعتماد الحكومي | No Government Endorsement Disclaimer

```
إخلاء المسؤولية التنظيمية:
لا تدّعي منصة SICO GRC ولا شركة [المزود] الحصول على اعتماد رسمي أو تأييد حكومي من
الهيئة الوطنية للأمن السيبراني (NCA) أو أي جهة حكومية سعودية أخرى، ما لم يُقدَّم دليل
رسمي صريح ومعتمد على ذلك. المنصة مصممة بما يتوافق مع المتطلبات التنظيمية المعلنة
ولا تُعفي العملاء من مسؤولياتهم التنظيمية الخاصة.
```

---

## القسم السابع: الملاحق | Annexes

**حالة البيانات / Data Status:** Placeholder (يتطلب استكمالًا)

---

### الملحق A — مصفوفة التغطية التفصيلية | Detailed Control Coverage Matrix

> **الحالة:** [TODO — يُنشأ آليًا من `data/controls/ecc_controls.json` + `data/controls/ccc_controls.json`]

الملحق يحتوي على الجدول الكامل لجميع ضوابط ECC (45 ضابط) وCCC (24 ضابط) مع حالة
التغطية والأدلة المرتبطة.

*المرجع:* `data/controls/ecc_controls.json`، `data/controls/ccc_controls.json`

---

### الملحق B — كتالوج الأدلة الكامل | Evidence Catalog (Full)

> **الحالة:** [TODO — يُستكمل من `data/evidence/evidence_catalog.json`]

الكتالوج الكامل يشمل 14 نوعًا من الأدلة موثقة في `data/evidence/evidence_catalog.json`
مع جميع التفاصيل: الأشكال المقبولة، التواتر، الاحتفاظ، الأدوار، الضوابط المرتبطة.

*المرجع:* `data/evidence/evidence_catalog.json`، `data/evidence/evidence_policy.json`

---

### الملحق C — قائمة Runbooks | Runbooks List

> **الحالة:** [TODO — يتطلب إعداد من فريق العمليات]

| Runbook_ID | العنوان | الوصف | المالك | آخر مراجعة |
|-----------|--------|-------|-------|-----------|
| RB-001 | استجابة حوادث المنصة | خطوات الاستجابة لحوادث أمن المنصة | IR Team | [TODO] |
| RB-002 | استعادة النظام بعد الكوارث | إجراءات DR والاسترداد الكامل | IT Operations | [TODO] |
| RB-003 | إدارة المستخدمين والصلاحيات | إضافة/تعديل/حذف المستخدمين | IT Security | [TODO] |
| RB-004 | تحديث المنصة وإدارة التصحيحات | خطوات Patch Management الآمن | DevOps Lead | [TODO] |
| RB-005 | تصدير الأدلة والتقارير للتدقيق | إجراءات استخراج الأدلة للمدققين | Compliance Officer | [TODO] |
| RB-006 | إغلاق ثغرة أمنية حرجة | استجابة سريعة للثغرات Critical/High | IT Security | [TODO] |
| RB-007 | نسخ احتياطي يدوي واسترداد بيانات | إجراءات الطوارئ للنسخ والاسترداد | IT Operations | [TODO] |
| RB-008 | إضافة إطار امتثال جديد | خطوات دمج إطار تنظيمي جديد | Compliance Officer | [TODO] |

*المرجع:* `docs/OPERATIONS_RUNBOOK.md` (قائم)، [TODO — نسخ Runbooks تفصيلية]

---

### الملحق D — مصفوفة SLA | SLA Matrix

> **الحالة:** [TODO — يتطلب تأكيد من فريق العمليات وإدارة المبيعات]

| مستوى الخدمة | وقت الاستجابة | وقت الحل | أوقات الخدمة | ملاحظات |
|-------------|--------------|---------|-------------|---------|
| P0 — Critical | [TODO] ساعة | [TODO] ساعة | 24/7 | حوادث أمنية حرجة |
| P1 — High | [TODO] ساعة | [TODO] ساعة | أيام العمل + طوارئ | توقف الخدمة |
| P2 — Medium | [TODO] ساعة | [TODO] يوم | أيام العمل | مشاكل وظيفية جوهرية |
| P3 — Low | [TODO] يوم | [TODO] يوم | أيام العمل | استفسارات وطلبات |
| Scheduled Maintenance | إشعار مسبق [TODO] يوم | — | [TODO] | نوافذ الصيانة |

---

### الملحق E — ملخص الفحوصات الأمنية | Security Scan Summary

> **الحالة:** [TODO — يتطلب تشغيل وتوثيق الأدوات الأمنية]

| نوع الفحص | الأداة | تاريخ آخر فحص | النتائج الحرجة | حالة المعالجة |
|-----------|-------|--------------|--------------|-------------|
| SAST | [TODO] | [TODO] | [TODO] | [TODO] |
| DAST | [TODO] | [TODO] | [TODO] | [TODO] |
| Secret Scanning | GitHub | 2026-02-24 | لا يوجد | Confirmed |
| Dependency Scanning | [TODO] | [TODO] | [TODO] | [TODO] |
| Penetration Test | [TODO] | [TODO] | [TODO] | [TODO] |
| SBOM | [TODO] | [TODO] | — | [TODO] |

---

### الملحق F — هيكل النشر | Deployment Topology

> **الحالة:** [TODO — يتطلب رسم معماري نهائي من فريق البنية التحتية]

**ملخص النشر الحالي** (مستخرج من `deployment/`):

```
[العميل / Browser]
        ↓ HTTPS (TLS 1.2/1.3)
[Nginx Reverse Proxy]
        ↓
[Next.js 14 Frontend]     ←→     [FastAPI Backend]
                                        ↓
                              [PostgreSQL Database]
                                        ↓
                              [Redis Cache / Queue]
                                        ↓
                              [Chroma Vector DB (AI/RAG)]
```

- جميع المكونات تعمل داخل الشبكة الداخلية (Internal Network)
- لا يوجد اتصال خارجي إلزامي بعد التثبيت
- *المرجع:* `deployment/docker-compose.yml`، `ARCHITECTURE_DIAGRAMS.md`

---

### الملحق G — سير عمل إدارة التغييرات | Change Management Workflow

> **الحالة:** [TODO — يتطلب توثيق رسمي من فريق العمليات]

```
طلب التغيير (Change Request)
        ↓
تقييم الأثر والمخاطر
        ↓
موافقة Change Advisory Board (CAB)
        ↓
اختبار في بيئة Staging
        ↓
موافقة نهائية
        ↓
تطبيق في الإنتاج (Maintenance Window)
        ↓
مراقبة ما بعد التطبيق
        ↓
إغلاق وتوثيق
```

---

### الملحق H — سير عمل الاستجابة للحوادث (للمنصة) | Incident Response Workflow

> **الحالة:** Draft (مستخرج من `docs/OPERATIONS_RUNBOOK.md`)

```
اكتشاف الحادثة (Detection)
        ↓
التصنيف والتأهيل (Triage — P0/P1/P2/P3)
        ↓
الإبلاغ الفوري (CISO + IR Team)
        ↓
الاحتواء (Containment)
        ↓
التحقيق والتحليل (Investigation)
        ↓
الاستئصال والاسترداد (Eradication & Recovery)
        ↓
توثيق الحادثة (Incident Report — ثنائي اللغة)
        ↓
تحليل ما بعد الحادثة (Post-Incident Review)
        ↓
تحديث Runbooks وإجراءات الوقاية
```

*المرجع:* `docs/OPERATIONS_RUNBOOK.md`، `playbooks/`

---

## قائمة المدخلات المطلوبة لاستكمال الوثيقة | Required Inputs to Finalize

> هذه القائمة تجمع جميع [TODO] الواردة في الوثيقة.

| # | المدخل المطلوب | القسم | الأولوية |
|---|--------------|-------|---------|
| 1 | اسم العميل والقطاع | صفحة الغلاف | P0 |
| 2 | اسم المراجع والمعتمد | صفحة الغلاف | P0 |
| 3 | توثيق تشفير البيانات في الراحة (At Rest Encryption) | 4.3, GAP-002 | P0 |
| 4 | تطبيق أو خارطة زمنية لـ MFA | 4.2, GAP-004 | P0 |
| 5 | تقرير DR Test موثق + تحديث BCP | 4.5, GAP-001 | P0 |
| 6 | SBOM Export من CI/CD Pipeline | 4.7, GAP-007 | P1 |
| 7 | تقرير Penetration Test | الملحق E, GAP-003 | P1 |
| 8 | تقرير SAST/DAST | الملحق E | P1 |
| 9 | قيم RPO/RTO الرسمية | 4.5, GAP-009 | P1 |
| 10 | نموذج مخاطر المستأجر السحابي | 2.3, GAP-005 | P1 |
| 11 | قيم SLA الرسمية (أوقات الاستجابة والحل) | الملحق D | P1 |
| 12 | قائمة Runbooks مكتملة | الملحق C | P2 |
| 13 | تغطية PDPL الكاملة (إذا انطبق) | 2.1, 5.1 GAP-010 | P2 |
| 14 | رسم معماري نهائي للنشر | الملحق F | P2 |
| 15 | نموذج Change Management الرسمي | الملحق G, GAP-008 | P2 |
| 16 | شهادات TLS / إعدادات التشفير في النقل | 4.3 | P2 |

---

## مسارات الملفات المرجعية | Suggested Repo Paths

| الملف | المسار في المستودع |
|-------|------------------|
| هذه الوثيقة | `docs/commercial/SICO_GRC_Submission_Dossier_Template.md` |
| البرومبت الرئيسي | `docs/prompts/SICO_SUBMISSION_DOSSIER_PROMPT.md` |
| ضوابط ECC | `data/controls/ecc_controls.json` |
| ضوابط CCC | `data/controls/ccc_controls.json` |
| ضوابط PDPL | `data/controls/pdpl_controls.json` |
| خرائط ECC↔CCC | `data/mappings/ecc-ccc-baseline.yaml` |
| دلتا CCC | `data/mappings/ccc-delta.yaml` |
| كتالوج الأدلة | `data/evidence/evidence_catalog.json` |
| سياسة الأدلة | `data/evidence/evidence_policy.json` |
| بيانات النشر | `deployment/docker-compose.yml` |
| Runbook العمليات | `docs/OPERATIONS_RUNBOOK.md` |
| التوثيق الأمني | `SECURITY-ATTESTATION.md`، `SECURITY.md` |

---

*آخر تحديث: 2026-02-24 | الإصدار: v1.0 | الإعداد: SilverWolf + Zain Affiliate / BU2*
*الحالة العامة للوثيقة: Draft — يتطلب مراجعة واعتماد المسؤول المفوّض*
