# مصفوفة RACI – تحديثات أمان التبعيات / RACI Matrix – Dependency Security Updates

> **الإصدار / Version:** 1.0 | **آخر تحديث / Last Updated:** 2026-02-24  
> **المرجع / Reference:** PR #48 – bump `cryptography` & `langchain-community`

---

## مفتاح المصفوفة / Matrix Key

| الرمز | المعنى (عربي) | Meaning (English) |
|:---:|---|---|
| **R** | مسؤول عن التنفيذ | **R**esponsible – does the work |
| **A** | مساءل / صاحب القرار | **A**ccountable – owns the outcome |
| **C** | يُستشار | **C**onsulted – provides input |
| **I** | يُبلَّغ | **I**nformed – kept in the loop |

---

## مصفوفة المسؤوليات / Responsibility Matrix

| النشاط / Activity | Security Engineer | Backend Developer | DevOps / Platform Engineer | Tech Lead / Eng. Manager | QA Engineer | Product Owner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. اكتشاف الثغرة** / Vulnerability Discovery | **R/A** | I | I | I | – | I |
| **2. تقييم الخطورة (CVSS Scoring)** / Severity Assessment | **R/A** | C | C | C | – | I |
| **3. إنشاء Issue على GitHub** / GitHub Issue Creation | **R** | C | – | **A** | – | I |
| **4. تطوير الإصلاح (تحديث requirements)** / Fix Development | C | **R** | C | **A** | – | – |
| **5. Code Review** | **R** | C | C | **A** | – | – |
| **6. اعتماد الدمج** / Merge Approval | C | – | – | **R/A** | – | I |
| **7. النشر على بيئة Staging** / Staging Deployment | I | I | **R/A** | C | I | – |
| **8. الاختبار بعد النشر (Staging)** / Post-deploy Testing (Staging) | C | C | I | C | **R/A** | – |
| **9. النشر على الإنتاج** / Production Deployment | I | I | **R/A** | **C** | I | I |
| **10. إغلاق Issue وتوثيق الدرس المستفاد** / Close Issue & Lessons Learned | **R** | C | C | **A** | C | I |

---

## وصف الأدوار / Role Descriptions

### 🔐 Security Engineer
مسؤول أولي عن مراقبة قواعد بيانات CVE (NVD, OSV), تشغيل أدوات المسح (`pip-audit`, `safety`), وتقييم الخطورة وفق CVSS v3.1. يوفر التوجيه التقني خلال مرحلة الإصلاح وما بعدها.

Primary owner of CVE database monitoring (NVD, OSV), running scanning tools (`pip-audit`, `safety`), and CVSS v3.1 severity scoring. Provides technical guidance during and after remediation.

---

### 💻 Backend Developer
يُنفّذ تحديثات الحزم في ملفات `requirements.txt`, يُجري الاختبارات المحلية, ويرفع Pull Request. المرجع الفعلي لأثر التغيير على الكود.

Implements package version bumps in `requirements.txt` files, runs local tests, and opens the Pull Request. Primary point of contact for code-level impact assessment.

---

### ⚙️ DevOps / Platform Engineer
يدير بيئات النشر وخطوط CI/CD. يُنسّق نشر الإصلاح على Staging ثم الإنتاج، ويضمن سلامة pipelines والـ rollback.

Manages deployment environments and CI/CD pipelines. Coordinates the fix rollout to Staging then Production, and ensures pipeline integrity and rollback readiness.

---

### 🎯 Tech Lead / Engineering Manager
صاحب القرار النهائي في اعتماد الدمج. يوازن بين الاستعجال الأمني ومتطلبات الاستقرار. يتلقى تقارير التصعيد للثغرات Severity ≥ High.

Final decision-maker for merge approval. Balances security urgency against stability requirements. Receives escalation reports for Severity ≥ High vulnerabilities.

---

### 🧪 QA Engineer
يُنفّذ اختبارات التراجع (regression) وسيناريوهات End-to-End على بيئة Staging بعد نشر الإصلاح، ويُوقّع على شهادة جودة الاختبار.

Executes regression tests and E2E scenarios on Staging after fix deployment, and signs off on the test quality certificate.

---

### 📋 Product Owner
يُبلَّغ بالثغرات والجداول الزمنية للإصلاح. لا يُشارك في التنفيذ التقني لكنه يملك قرار تأخير الإصلاح إذا كانت هناك اعتبارات عمل استثنائية (نادر).

Informed of vulnerabilities and remediation timelines. Not involved in technical execution but owns the decision to delay a fix in exceptional business circumstances (rare).

---

## سيناريوهات التصعيد / Escalation Scenarios

| الحالة / Condition | التصعيد إلى / Escalate to | الإطار الزمني / Timeframe |
|---|---|---|
| CVSS ≥ 9.0 (Critical) | Tech Lead + CISO فوراً / immediately | < 4 ساعات / hours |
| CVSS 7.0–8.9 (High) | Tech Lead | < 24 ساعة / hours |
| CVSS 4.0–6.9 (Medium) | Security Engineer يقود / leads | < 72 ساعة / hours |
| CVSS < 4.0 (Low) | يُجدوَل في Sprint القادم / next Sprint | < 2 أسابيع / weeks |
| PR مرفوض مرتين / PR rejected twice | Tech Lead + Security Engineer | نفس اليوم / same day |

---

## مثال تطبيقي: PR #48 / Applied Example: PR #48

| النشاط | المنفّذ الفعلي |
|---|---|
| اكتشاف الثغرة | Security Engineer (pip-audit scan) |
| تقييم الخطورة | Security Engineer → CVSS High/Critical |
| إنشاء Issue | Security Engineer (GitHub Issue) |
| تحديث requirements | Backend Developer (Copilot-assisted) |
| Code Review | Security Engineer + Tech Lead |
| اعتماد الدمج | Tech Lead |
| النشر | DevOps Engineer |
| إغلاق وتوثيق | Security Engineer |
