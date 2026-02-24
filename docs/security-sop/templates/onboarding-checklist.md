# قائمة تأهيل المطورين الجدد / Developer Onboarding Checklist
## عملية أمان التبعيات / Dependency Security Process

> **للمطور الجديد / For New Developer:** `_________________`  
> **تاريخ البدء / Start Date:** `_________________`  
> **المرشد / Mentor:** `_________________`  
> **المراجع / Reference:** `SOP-dependency-security.md`, PR #48

---

## القسم الأول: الإعداد البيئي / Environment Setup

### 1.1 متطلبات النظام / System Requirements

- [ ] Python 3.10+ مثبّت ومُختبر (`python --version`)
- [ ] pip مُحدَّث (`pip install --upgrade pip`)
- [ ] Git مُهيَّأ (`git config --global user.name` + `user.email`)
- [ ] GitHub account مع MFA مُفعَّل
- [ ] SSH key مُضافة لـ GitHub account

### 1.2 استنساخ المستودع / Repository Clone

```bash
git clone git@github.com:sonaiso/sanadcom.git
cd sanadcom
```

- [ ] استنساخ ناجح
- [ ] تشغيل `git log --oneline -5` للتحقق من السجل

### 1.3 الأدوات الأمنية / Security Tools

```bash
pip install pip-audit safety bandit
```

- [ ] `pip-audit --version` تُظهر إصداراً ≥ 2.7.0
- [ ] `safety --version` تُظهر إصداراً ≥ 3.0.0
- [ ] `bandit --version` تُظهر إصداراً ≥ 1.7.0

---

## القسم الثاني: الأدوات المطلوب تثبيتها / Required Tools Installation

### 2.1 أدوات التطوير / Development Tools

- [ ] **VS Code** أو IDE آخر مع Python extension
- [ ] **pre-commit** لتشغيل فحوصات قبل كل commit:
  ```bash
  pip install pre-commit
  pre-commit install
  ```
- [ ] **Docker Desktop** لتشغيل بيئة الاختبار المحلية
  ```bash
  docker --version   # تأكيد التثبيت
  ```

### 2.2 أدوات المسح الأمني / Security Scanning Tools

| الأداة | الغرض | تثبيت |
|---|---|---|
| `pip-audit` | فحص تبعيات Python | `pip install pip-audit` |
| `safety` | فحص بديل للتبعيات | `pip install safety` |
| `bandit` | SAST – تحليل كود Python | `pip install bandit` |
| `gitleaks` | كشف أسرار في الكود | [gitleaks.io](https://github.com/gitleaks/gitleaks) |

- [ ] جميع الأدوات مثبّتة ومختبرة

### 2.3 اختبار أدوات المسح / Scan Tools Verification

```bash
# تشغيل مسح على المستودع الحالي
pip-audit -r src/backend/requirements.txt
safety check -r src/backend/requirements.txt
bandit -r src/backend/ -ll
```

- [ ] pip-audit يُشغَّل بنجاح
- [ ] safety يُشغَّل بنجاح
- [ ] bandit يُشغَّل بنجاح

---

## القسم الثالث: الوصول المطلوب / Required Access

### 3.1 GitHub Access

- [ ] صلاحية **Read** على المستودع `sonaiso/sanadcom`
- [ ] صلاحية **Write** (لإنشاء branches وPRs)
- [ ] الوصول لتبويب **Security** في GitHub (إن كان متاحاً)
- [ ] الوصول لـ **Dependabot Alerts**

للطلب: تواصل مع Tech Lead وأرسل GitHub username.

### 3.2 بيئات النشر / Deployment Environments

- [ ] **Staging**: بيانات الوصول من DevOps Engineer
- [ ] **Production**: يحتاج موافقة مسبقة من Tech Lead (للمراقبة فقط في البداية)

### 3.3 أدوات المشروع / Project Tools

- [ ] الوصول لـ Jira/GitHub Projects (إن وُجد)
- [ ] الوصول لأدوات CI/CD (GitHub Actions)
- [ ] القناة الأمنية في Slack/Teams: `#security-alerts`

---

## القسم الرابع: التدريب المطلوب / Required Training

### 4.1 قراءة الوثائق / Documentation Reading

- [ ] قراءة `SECURITY.md` (السياسة الأمنية الرئيسية)
- [ ] قراءة `docs/security-sop/SOP-dependency-security.md` (هذا SOP)
- [ ] قراءة `docs/security-sop/RACI-matrix.md` (مصفوفة المسؤوليات)
- [ ] مراجعة PR #48 كمثال عملي حقيقي

### 4.2 فهم السياق / Understand Context

- [ ] فهم بنية المشروع (Backend + AI layers)
- [ ] فهم ملفات `src/backend/requirements.txt` و `ai/requirements.txt`
- [ ] فهم CI/CD pipeline (`.github/workflows/`)
- [ ] معرفة كيفية قراءة نتائج pip-audit

### 4.3 تدريبات موصى بها / Recommended Training

| الموضوع | المصدر | مدة التدريب |
|---|---|---|
| CVSS v3.1 Scoring | [FIRST.org](https://www.first.org/cvss/) | 2 ساعات |
| OWASP Top 10 | [owasp.org](https://owasp.org/www-project-top-ten/) | 3 ساعات |
| Python Security | [Bandit Docs](https://bandit.readthedocs.io/) | 1 ساعة |
| GitHub Security Features | [GitHub Docs](https://docs.github.com/en/code-security) | 2 ساعات |

- [ ] CVSS Scoring مفهوم (تدرّب على حالات PR #48)
- [ ] OWASP Dependency Check مفهوم
- [ ] Python security best practices مفهومة

---

## القسم الخامس: أول مهام الأمان / First Security Tasks

### 5.1 مهام التدريب / Training Tasks

- [ ] **المهمة 1:** شغّل `pip-audit` على المستودع وراجع النتائج مع المرشد
- [ ] **المهمة 2:** راجع PR #48 على GitHub وافهم كل تعديل
- [ ] **المهمة 3:** أنشئ branch تجريبي وجرّب تحديث تبعية غير أمنية في بيئة تطوير (لا ترفع PR)
- [ ] **المهمة 4:** اقرأ CVE-2024-2965 (SSRF في langchain-community) وفهم طريقة الاستغلال

### 5.2 اختبار الاستعداد / Readiness Test

أجب على الأسئلة التالية مع المرشد:
- [ ] ما هو CVSS Score الذي يستدعي إجراءً فورياً (< 4 ساعات)؟
- [ ] ما هي الخطوات الخمس الأولى في SOP-dependency-security.md؟
- [ ] من هو المسؤول (A) في خطوة "اعتماد الدمج" في RACI Matrix؟
- [ ] كيف تُنشئ branch صحيح لإصلاح أمني؟

### 5.3 المهمة الأولى الفعلية / First Real Task

- [ ] الانضمام لـ On-Call rotation (بعد 30 يوم من البدء)
- [ ] المشاركة في مراجعة أمنية واحدة كـ Observer
- [ ] تعبئة نموذج `evidence-template.md` لأول ثغرة (بمساعدة المرشد)

---

## التوقيعات / Sign-off

| الدور | الاسم | التوقيع | التاريخ |
|---|---|---|---|
| المطور الجديد / New Developer | | | |
| المرشد / Mentor | | | |
| Security Engineer | | | |
| Tech Lead | | | |

---

> ✅ عند إكمال جميع البنود، أرسل هذا الملف المكتمل لـ Security Engineer لحفظه كـ Evidence.
