# نموذج طلب الاعتماد / Merge Approval Request Template
## تحديث أمان التبعيات / Dependency Security Update

> **رقم الطلب / Request ID:** APR-SEC-`[YYYY-MM-DD]`-`[SEQ]`  
> **للتقديم لـ / Submit to:** Tech Lead  
> **أقصى وقت للاستجابة / Response Deadline:** `[حسب CVSS / Per CVSS severity]`

---

## معلومات الطلب / Request Information

| الحقل | القيمة |
|---|---|
| **مُقدّم الطلب / Requestor** | `[اسم المطور / Developer Name]` |
| **تاريخ الطلب / Request Date** | `YYYY-MM-DD HH:MM` |
| **رقم Pull Request / PR Number** | `#XX` |
| **رابط PR / PR Link** | `https://github.com/sonaiso/sanadcom/pull/XX` |
| **Branch المصدر / Source Branch** | `fix/security-bump-<package>-<date>` |
| **Branch الهدف / Target Branch** | `main` |
| **Issue المرتبط / Linked Issue** | `#XX` |
| **أولوية الاعتماد / Approval Priority** | `🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low` |

---

## ملخص التغييرات / Changes Summary

```
[اكتب ملخصاً موجزاً لا يتجاوز 5 أسطر يصف:
 - الحزم المحدَّثة
 - السبب الأمني
 - نطاق التغيير (الملفات المعدّلة فقط)]
```

**مثال (PR #48):**
```
تحديث أمني لحزمتين رئيسيتين:
1. cryptography: 42.0.0 → 46.0.5 لمعالجة 3 CVEs (Max CVSS 7.5)
2. langchain-community: 0.0.16 → 0.3.27 لمعالجة 3 CVEs (Max CVSS 9.0)

التغييرات محصورة في:
- src/backend/requirements.txt (سطران)
- ai/requirements.txt (سطر واحد)
```

---

## الثغرات المعالجة / Vulnerabilities Addressed

| # | الحزمة / Package | CVE ID | CVSS | الخطورة / Severity | نوع الثغرة / Type |
|---|---|---|---|---|---|
| 1 | `package-name` | `CVE-XXXX-XXXXX` | `X.X` | Critical/High/Medium | RCE/SSRF/DoS/... |
| 2 | | | | | |
| 3 | | | | | |

**إجمالي CVEs المعالجة:** `X`  
**أعلى CVSS Score:** `X.X`  
**أعلى خطورة:** `Critical / High / Medium`

---

## نتائج الاختبار / Test Results Summary

### ✅ الاختبارات التي اجتازها / Passed Tests

- [ ] `pip-audit` لا يُبلّغ عن ثغرات (بعد التحديث)
- [ ] `pytest` اجتاز `X/Y` اختبار (`X%` نجاح)
- [ ] `safety check` نظيف
- [ ] تثبيت التبعيات يعمل بدون أخطاء
- [ ] التطبيق يبدأ بشكل طبيعي

### ❌ اختبارات فاشلة (إن وجدت) / Failed Tests

```
[اذكر أي اختبارات فاشلة وسبب قبولها / Mention any failed tests and reason for acceptance]
[أو اكتب: لا يوجد / None]
```

### سجل CI/CD / CI/CD Run

| المرحلة | الحالة | الرابط |
|---|---|---|
| Unit Tests | ✅ / ❌ | |
| Security Scan | ✅ / ❌ | |
| Build | ✅ / ❌ | |

---

## تقييم الأثر / Impact Assessment

### أثر على الأداء / Performance Impact

- [ ] **لا أثر** – حزم الأمان فقط، لا تغيير في Business Logic
- [ ] **أثر طفيف** – تم قياسه: `___`
- [ ] **يحتاج مراقبة** – السبب: `___`

### أثر على التوافق / Compatibility Impact

| الجانب | التقييم | ملاحظات |
|---|---|---|
| Public API | لا تغيير / No change | |
| Database Schema | لا تغيير / No change | |
| Configuration Files | لا تغيير / No change | |
| Behavior Change | لا تغيير / No change | |

### التبعيات المتأثرة / Affected Dependents

```
[هل تؤثر هذه التحديثات على حزم أخرى؟ اذكرها]
[مثال: langchain-community → يؤثر على ai/ module فقط]
```

---

## خطة التراجع / Rollback Plan

### متطلبات التراجع
- **وقت التراجع المقدر / Estimated Rollback Time:** `< 15 دقيقة / minutes`
- **من يُنفّذ التراجع / Rollback Executor:** DevOps Engineer

### خطوات التراجع / Rollback Steps

```bash
# 1. تحديد commit الأخير السليم
git log --oneline src/backend/requirements.txt

# 2. التراجع عن التغييرات في requirements.txt
git revert <merge-commit-sha>

# 3. فتح PR طارئ للتراجع (Hotfix PR)
git checkout -b hotfix/revert-security-bump-<date>
git push origin hotfix/revert-security-bump-<date>

# 4. اعتماد الدمج الطارئ من Tech Lead
# 5. إعادة النشر عبر CI/CD
```

### سيناريوهات التراجع / Rollback Triggers

- [ ] معدل أخطاء Production يرتفع > 1% بعد النشر
- [ ] اختبارات Staging الحرجة تفشل
- [ ] فشل غير متوقع في startup التطبيق
- [ ] طلب Tech Lead

---

## قائمة التحقق للمعتمِد / Approver's Checklist

> يجب على Tech Lead التحقق من البنود التالية قبل الاعتماد:

- [ ] CVEs موثّقة في قاعدة بيانات معتمدة (NVD/OSV)
- [ ] الإصدار الآمن المُقترح يُصلح الثغرات المذكورة فعلاً
- [ ] التغييرات محصورة في ملفات requirements فقط
- [ ] CI/CD pipeline يمر بنجاح (جميع checks خضراء)
- [ ] لا توجد تعليقات معلقة في PR
- [ ] Security Engineer وقّع على المراجعة

---

## توقيعات الاعتماد / Approval Signatures

### توقيع المطور / Developer Sign-off

| الحقل | القيمة |
|---|---|
| **الاسم / Name** | |
| **الدور / Role** | Backend Developer / Security Engineer |
| **التوقيع / Signature** | |
| **التاريخ / Date** | |
| **تأكيد / Confirmation** | ☐ أؤكد أن جميع بنود القائمة أعلاه مكتملة |

---

### توقيع مراجع الأمان / Security Review Sign-off

| الحقل | القيمة |
|---|---|
| **الاسم / Name** | |
| **الدور / Role** | Security Engineer |
| **التوقيع / Signature** | |
| **التاريخ / Date** | |
| **الرأي / Opinion** | ☐ موافق على الدمج / Approved ☐ يحتاج تعديل / Needs Changes |
| **ملاحظات / Notes** | |

---

### توقيع المعتمِد / Final Approver Sign-off

| الحقل | القيمة |
|---|---|
| **الاسم / Name** | |
| **الدور / Role** | Tech Lead / Engineering Manager |
| **التوقيع / Signature** | |
| **تاريخ الاعتماد / Approval Date** | |
| **القرار / Decision** | ☐ معتمد للدمج / Approved to Merge ☐ مرفوض / Rejected |
| **شروط الاعتماد / Conditions (if any)** | |
| **ملاحظات / Notes** | |

---

> 📎 **أرفق مع هذا النموذج / Attach with this form:**
> - مخرجات pip-audit قبل وبعد التحديث
> - سجل اختبارات pytest
> - رابط CI/CD Run
