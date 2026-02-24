# SOP – إدارة تحديثات أمان التبعيات / Dependency Security Update Playbook

> **رقم الوثيقة / Doc ID:** SOP-SEC-DEP-001  
> **الإصدار / Version:** 1.0  
> **تاريخ السريان / Effective Date:** 2026-02-24  
> **المالك / Owner:** Security Engineer  
> **المراجع / Reviewer:** Tech Lead  
> **دورة المراجعة / Review Cycle:** كل 6 أشهر / Every 6 months  
> **المرجع الفعلي / Real-World Reference:** PR #48 – `cryptography` 42.0.0→46.0.5, `langchain-community` 0.0.16→0.3.27

---

## 1. الغرض والنطاق / Purpose & Scope

### الغرض
يُحدّد هذا الإجراء الخطوات الموحدة لاكتشاف الثغرات الأمنية في تبعيات Python، وتقييمها، وتحديثها، والتحقق من الإصلاح، وتوثيقه في منصة SICO GRC.

### النطاق
يسري على جميع ملفات `requirements.txt` في المستودع:
- `src/backend/requirements.txt`
- `ai/requirements.txt`

### الاستثناءات
- تبعيات JavaScript/Node.js تتبع SOP منفصل (SOP-SEC-NPM-001)
- تبعيات Infrastructure-as-Code تتبع SOP-SEC-IAC-001

---

## 2. التعريفات / Definitions

| المصطلح | التعريف |
|---|---|
| **CVE** | Common Vulnerabilities and Exposures – معرّف الثغرة الأمنية المعياري |
| **CVSS** | Common Vulnerability Scoring System – نظام تقييم الخطورة (0.0–10.0) |
| **Dependency** | حزمة خارجية مُدرجة في `requirements.txt` |
| **Requirements file** | ملف يحدد إصدارات الحزم المطلوبة في بيئة Python |
| **pip-audit** | أداة مسح أمان تبعيات Python تستعلم قاعدة PyPA Advisory Database |
| **safety** | أداة بديلة تستعلم قاعدة Safety DB |
| **Dependabot** | خدمة GitHub تراقب التبعيات تلقائياً وترفع PRs للتحديث |
| **Remediation** | إجراء إصلاح الثغرة بتحديث الحزمة لإصدار آمن |
| **Rollback** | إعادة البيئة لإصدار سابق عند فشل التحديث |

---

## 3. المتطلبات الأولية / Prerequisites

### الأدوات المطلوبة

```bash
# تثبيت أدوات المسح
pip install pip-audit safety

# التحقق من التثبيت
pip-audit --version   # >= 2.7.0
safety --version      # >= 3.0.0
```

### الوصول المطلوب
- [ ] Write access على مستودع GitHub
- [ ] صلاحية فتح Issues وإنشاء PRs
- [ ] الوصول لقراءة نتائج GitHub Advanced Security (إن وُجد)
- [ ] الوصول لبيئة Staging للاختبار

### الأدوات والخدمات
| الأداة | الغرض | الرابط |
|---|---|---|
| pip-audit | مسح محلي للتبعيات | https://pypi.org/project/pip-audit/ |
| safety | مسح بديل للتبعيات | https://pypi.org/project/safety/ |
| Dependabot | مراقبة تلقائية | GitHub Settings → Security |
| NVD | قاعدة بيانات CVE | https://nvd.nist.gov/ |
| OSV | قاعدة بيانات مفتوحة المصدر | https://osv.dev/ |

---

## 4. خطوات العملية التشغيلية / Operational Steps

### الخطوة 1 – اكتشاف الثغرة (Discovery)

#### 1A. المسح التلقائي (Automated Scanning)
```bash
# مسح backend
pip-audit -r src/backend/requirements.txt --output json > /tmp/audit-backend.json

# مسح AI
pip-audit -r ai/requirements.txt --output json > /tmp/audit-ai.json

# مسح إضافي بـ safety
safety check -r src/backend/requirements.txt --full-report
```

#### 1B. مصادر الاكتشاف الأخرى
- **Dependabot Alert** في GitHub Security tab
- **NVD / OSV** عبر الاشتراك في الإشعارات
- **مجتمع المطورين** (Security advisories من PyPI)

#### 1C. توثيق الاكتشاف
- سجّل اسم الحزمة، الإصدار الحالي، معرّف CVE، وتاريخ الاكتشاف
- احتفظ بمخرجات أدوات المسح كـ Artifact

---

### الخطوة 2 – تقييم الخطورة (Severity Assessment)

#### معايير CVSS v3.1
| النطاق | التصنيف | الإجراء |
|---|---|---|
| 9.0 – 10.0 | 🔴 Critical | إصلاح فوري < 4 ساعات |
| 7.0 – 8.9 | 🟠 High | إصلاح < 24 ساعة |
| 4.0 – 6.9 | 🟡 Medium | إصلاح < 72 ساعة |
| 0.1 – 3.9 | 🟢 Low | يُجدوَل في Sprint التالي |

#### أسئلة التقييم
1. هل الثغرة قابلة للاستغلال في بيئة الإنتاج الحالية؟
2. هل تؤثر على بيانات مستخدمين أو بيانات حساسة؟
3. هل يوجد Exploit عام متاح (Public PoC)؟
4. ما هو الإصدار الآمن المتاح؟

---

### الخطوة 3 – إنشاء Issue على GitHub

```markdown
**عنوان النموذج:**
[SECURITY] <Package> <old-version> → <new-version> | CVE-XXXX-XXXXX

**المحتوى المطلوب:**
- الحزمة المتأثرة وإصدارها الحالي
- قائمة CVEs مع CVSS Score لكل منها
- وصف مختصر لطبيعة الثغرة
- الإصدار الآمن المقترح
- الأولوية / Label: `security`, `priority:high`
```

**مثال من PR #48:**
```
[SECURITY] cryptography 42.0.0 → 46.0.5 + langchain-community 0.0.16 → 0.3.27
Labels: security, priority:high
```

---

### الخطوة 4 – إنشاء Branch جديد من `main`

```bash
# التأكد من أحدث إصدار لـ main
git checkout main
git pull origin main

# إنشاء branch بالتسمية المعيارية
git checkout -b fix/security-bump-<package>-<date>

# مثال
git checkout -b fix/security-bump-cryptography-20260224
```

> ⚠️ **تحذير:** لا تبنِ على branches أخرى غير `main` لتجنب تعارضات الدمج.

---

### الخطوة 5 – تحديث ملفات `requirements.txt`

#### قواعد التحديث
1. حدّث **جميع** مواضع ظهور الحزمة في الملف
2. لا تحدّث حزماً أخرى لم تُذكر في الثغرة
3. استخدم الإصدار المحدد (pinned version) وليس النطاق

```bash
# مثال تحديث في src/backend/requirements.txt
# قبل / Before
cryptography==42.0.0
langchain-community==0.0.16

# بعد / After
cryptography==46.0.5
langchain-community==0.3.27
```

#### التحقق من صحة الملف
```bash
pip install -r src/backend/requirements.txt --dry-run
pip install -r ai/requirements.txt --dry-run
```

---

### الخطوة 6 – الاختبار المحلي (Local Testing)

```bash
# 1. إنشاء بيئة افتراضية نظيفة
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate

# 2. تثبيت التبعيات المحدّثة
pip install -r src/backend/requirements.txt

# 3. تشغيل اختبارات الوحدة
cd src/backend && pytest tests/ -v --tb=short

# 4. التحقق من عدم وجود ثغرات جديدة
pip-audit -r src/backend/requirements.txt

# 5. اختبار التشغيل السريع
python -c "from cryptography.hazmat.primitives.asymmetric import rsa; print('cryptography OK')"
python -c "from langchain_community.llms import FakeListLLM; print('langchain-community OK')"
```

---

### الخطوة 7 – رفع Pull Request

```markdown
**عنوان PR:**
fix: bump <package> to patch CVE-XXXX-XXXXX

**وصف PR:**
## Version Bumps
- `<package>` X.X.X → Y.Y.Y

## CVEs Addressed
| Package | CVE | CVSS | Description |
|---|---|---|---|
| cryptography | CVE-2023-49083 | 7.5 | pkcs12 NULL-ptr deref |

## Testing
- [ ] Local pip install verified
- [ ] Unit tests pass
- [ ] pip-audit clean post-update

## Risk Assessment
- Breaking changes: None expected
- Rollback plan: git revert <commit>
```

#### Checklist قبل الرفع
- [ ] Branch مبني على أحدث `main`
- [ ] تحديثات محصورة في ملفات requirements فقط
- [ ] اختبارات محلية ناجحة
- [ ] لا يوجد dependency conflict
- [ ] ربط PR بالـ Issue الأصلي (`Closes #XX`)

---

### الخطوة 8 – المراجعة والاعتماد (Review & Approval)

**المراجع المطلوبون:**
- Security Engineer: يتحقق من صحة الإصدار الآمن
- Tech Lead: يعتمد الدمج

**معيار القبول:**
- [ ] CI/CD pipeline ناجح (جميع checks خضراء)
- [ ] لا توجد تعليقات معلقة
- [ ] توقيع Tech Lead على نموذج `approval-request.md`

---

### الخطوة 9 – الدمج والنشر (Merge & Deploy)

```bash
# استخدام Squash Merge للحفاظ على تاريخ نظيف
# يتم عبر GitHub UI → Squash and Merge

# بعد الدمج، تشغيل CI/CD Pipeline على main
# التحقق من نشر التغيير على Staging أولاً
```

**ترتيب النشر:**
1. ✅ Merge to `main`
2. ✅ Auto-deploy to **Staging** (CI/CD trigger)
3. ✅ QA Smoke Test على Staging
4. ✅ Manual approval للنشر على **Production**
5. ✅ Monitor Production logs لمدة 30 دقيقة

---

### الخطوة 10 – التحقق والإغلاق (Verification & Closure)

```bash
# تشغيل مسح نهائي على بيئة الإنتاج
pip-audit -r src/backend/requirements.txt

# التحقق من الإصدار المنشور
pip show cryptography | grep Version
```

**إجراءات الإغلاق:**
- [ ] تشغيل pip-audit على بيئة Production وتأكيد النظافة
- [ ] إغلاق الـ Issue الأصلي مع تعليق ختامي
- [ ] تعبئة نموذج `evidence-template.md`
- [ ] تعبئة نموذج `submission-report.md`
- [ ] إضافة الدرس المستفاد في قسم Lessons Learned

---

## 5. CVEs المعالجة في PR #48

### cryptography (42.0.0 → 46.0.5)

| CVE | CVSS | النوع | الوصف |
|---|---|---|---|
| CVE-2023-32681 | 6.1 | Timing Oracle | Bleichenbacher timing oracle attack على RSA |
| CVE-2023-49083 | 7.5 | NULL-ptr deref | pkcs12 parsing NULL pointer dereference |
| CVE-2024-26130 | 7.5 | Subgroup Attack | SECT curve subgroup attack على ECDH |

### langchain-community (0.0.16 → 0.3.27 | 0.0.13 → 0.3.27)

| CVE | CVSS | النوع | الوصف |
|---|---|---|---|
| CVE-2024-21513 | 8.1 | XXE | XML External Entity injection |
| CVE-2024-2965 | 9.0 | SSRF | Server-Side Request Forgery في `RequestsToolkit` |
| CVE-2024-46946 | 8.8 | Deserialization | Pickle deserialization من مصدر غير موثوق |

### fastapi (0.109.0 → 0.109.1) ✅ كانت محدّثة مسبقاً

| CVE | CVSS | النوع | الوصف |
|---|---|---|---|
| CVE-2024-24762 | 7.5 | ReDoS | Regular Expression DoS عبر Content-Type header |

### python-multipart (0.0.6 → 0.0.22) ✅ كانت محدّثة مسبقاً

| CVE | CVSS | النوع | الوصف |
|---|---|---|---|
| CVE-2024-24762 | 7.5 | ReDoS | Content-Type header ReDoS (مشترك مع fastapi) |
| CVE-2024-53498 | 7.5 | DoS | DoS عبر malformed multipart boundary |
| CVE-2025-23017 | 8.1 | File Write | Arbitrary file write عبر crafted upload |

---

## 6. معايير الجودة (Definition of Done)

عملية التحديث تُعتبر مكتملة عند استيفاء جميع البنود التالية:

- [x] pip-audit لا يُبلّغ عن ثغرات في الإصدارات المحدّثة
- [x] جميع اختبارات pytest تمر بنجاح
- [x] CI/CD pipeline خضراء على `main`
- [x] الإصدار المحدّث منشور على Staging ومختبر
- [x] الإصدار المحدّث منشور على Production
- [x] الـ Issue مغلق مع تعليق توثيقي
- [x] نماذج `evidence-template.md` و `submission-report.md` مكتملة
- [x] لا يوجد تراجع (regression) في اختبارات QA

---

## 7. قواعد التصعيد (Escalation Matrix)

```
CVSS < 4.0  →  Security Engineer → يُجدوَل في Sprint التالي
CVSS 4-7    →  Security Engineer → Tech Lead (24-72h)
CVSS 7-9    →  Security Engineer → Tech Lead → فوري (< 24h)
CVSS ≥ 9    →  Security Engineer → Tech Lead → CISO (< 4h) → Emergency Response
```

في حال عدم توفر الإصلاح (No patch available):
1. تقييم المخاطر واتخاذ قرار Compensating Control
2. توثيق قرار القبول بالمخاطرة (Risk Acceptance) مع توقيع CISO
3. المتابعة الأسبوعية حتى توفر الإصلاح

---

## 8. المراجع والروابط / References

- [NVD – National Vulnerability Database](https://nvd.nist.gov/)
- [OSV – Open Source Vulnerability Database](https://osv.dev/)
- [PyPA Advisory Database](https://github.com/pypa/advisory-database)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
- [ISO 27001:2022 Annex A.8.8](https://www.iso.org/standard/82875.html)
- [NIST SP 800-40 Rev. 4](https://csrc.nist.gov/publications/detail/sp/800-40/rev-4/final)
- [NCA ECC-1:2018](https://nca.gov.sa/en/)
- [PR #48 – sanadcom](https://github.com/sonaiso/sanadcom/pull/48)
