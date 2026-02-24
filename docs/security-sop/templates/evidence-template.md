# نموذج توثيق الأدلة / Evidence & Artifact Template
## إصلاح ثغرة أمنية في التبعيات / Dependency Security Vulnerability Fix

> **رقم النموذج / Form ID:** EVD-SEC-DEP-`[YYYY-MM-DD]`-`[SEQ]`  
> **النسخة / Version:** 1.0

---

## القسم أ: معلومات الثغرة / Vulnerability Information

### التفاصيل الأساسية

| الحقل | القيمة |
|---|---|
| **معرّف CVE / CVE ID** | `CVE-XXXX-XXXXX` |
| **نقاط CVSS / CVSS Score** | `0.0 / Critical / High / Medium / Low` |
| **ناقل الهجوم / Attack Vector** | `Network / Adjacent / Local / Physical` |
| **الحزمة المتأثرة / Affected Package** | `package-name` |
| **الإصدار المتأثر / Vulnerable Version** | `X.X.X` |
| **الإصدار الآمن / Fixed Version** | `Y.Y.Y` |
| **نوع الثغرة / Vulnerability Type** | `RCE / SSRF / SQLi / XSS / DoS / ...` |
| **ملف requirements المتأثر** | `src/backend/requirements.txt` / `ai/requirements.txt` |

### وصف الثغرة / Vulnerability Description

```
[اكتب وصفاً مختصراً لطبيعة الثغرة وطريقة الاستغلال]
[Brief description of the vulnerability nature and exploitation method]
```

### مثال من PR #48 (نسخ وتعديل)

```
الثغرة: CVE-2024-2965 – SSRF في langchain-community RequestsToolkit
الإصدار المتأثر: 0.0.16
الإصدار الآمن: 0.3.27
الوصف: يسمح للمهاجم بإجراء طلبات HTTP داخلية عبر أداة RequestsToolkit
       مما يُمكّن من الوصول للخدمات الداخلية (SSRF).
```

---

## القسم ب: التواريخ / Dates & Timeline

| الحدث | التاريخ | الوقت | المسؤول |
|---|---|---|---|
| **تاريخ الاكتشاف / Discovery Date** | `YYYY-MM-DD` | `HH:MM` | `Security Engineer` |
| **تاريخ إنشاء Issue / Issue Created** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ بدء الإصلاح / Fix Started** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ فتح PR / PR Opened** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ الاعتماد / Approved** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ الدمج / Merged** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ النشر (Staging) / Staging Deploy** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ النشر (Production) / Prod Deploy** | `YYYY-MM-DD` | `HH:MM` | |
| **تاريخ الإغلاق / Closed** | `YYYY-MM-DD` | `HH:MM` | |

**إجمالي وقت المعالجة / Total Remediation Time:** `___ ساعة / hours`

---

## القسم ج: الملفات المعدّلة / Modified Files

| الملف | التعديل | قبل / Before | بعد / After |
|---|---|---|---|
| `src/backend/requirements.txt` | تحديث إصدار | `package==X.X.X` | `package==Y.Y.Y` |
| `ai/requirements.txt` | تحديث إصدار | `package==X.X.X` | `package==Y.Y.Y` |

> **القاعدة:** لا يُسمح بتعديل أي ملف آخر خارج ملفات requirements في عملية إصلاح أمني للتبعيات.

---

## القسم د: الروابط / Links & References

| العنصر | الرابط |
|---|---|
| **GitHub Issue** | `https://github.com/sonaiso/sanadcom/issues/XX` |
| **Pull Request** | `https://github.com/sonaiso/sanadcom/pull/XX` |
| **CVE Reference (NVD)** | `https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXXX` |
| **Security Advisory** | `https://github.com/advisories/GHSA-XXXX-XXXX-XXXX` |
| **pip-audit Output** | `[مرفق / Attached]` |
| **CI/CD Run** | `https://github.com/sonaiso/sanadcom/actions/runs/XXXXXXXX` |

---

## القسم هـ: نتائج الاختبار / Test Results

### اختبارات ما قبل النشر

| الاختبار | النتيجة | ملاحظات |
|---|---|---|
| `pip-audit` (pre-fix) | ✅ / ❌ | |
| `pip-audit` (post-fix) | ✅ / ❌ | |
| `pytest` unit tests | ✅ / ❌ | `X/Y passed` |
| `safety check` | ✅ / ❌ | |
| تثبيت التبعيات / pip install | ✅ / ❌ | |
| تشغيل التطبيق / App startup | ✅ / ❌ | |

### اختبارات Staging

| الاختبار | النتيجة | ملاحظات |
|---|---|---|
| Smoke Test | ✅ / ❌ | |
| اختبارات التراجع / Regression Tests | ✅ / ❌ | |
| فحص أمني / Security Scan | ✅ / ❌ | |

### اختبارات Production (Post-deploy Monitoring)

| المقياس | القيمة | حالة |
|---|---|---|
| معدل الأخطاء / Error Rate | `X%` | ✅ / ❌ |
| زمن الاستجابة / Response Time | `XX ms` | ✅ / ❌ |
| pip-audit نظيف / Clean | نعم / لا | ✅ / ❌ |

---

## القسم و: تقييم الأثر / Impact Assessment

### أثر التحديث على الأداء / Performance Impact

- [ ] لا أثر مقيس / No measurable impact
- [ ] أثر طفيف مقبول < 5% / Negligible impact < 5%
- [ ] أثر مقبول 5-15% / Acceptable impact 5-15%
- [ ] أثر يتطلب تحقيقاً / Impact requires investigation

### التوافق / Compatibility

- [ ] لا breaking changes في API العام
- [ ] لا تغيير في سلوك الحزمة المُستخدَم فعلياً
- [ ] تم التحقق من التوافق مع Python `3.10` / `3.11` / `3.12`

---

## القسم ز: الاعتماد والتوقيع / Approval & Sign-off

| الدور | الاسم | التوقيع | التاريخ |
|---|---|---|---|
| **مُعِد النموذج / Prepared by** | | | |
| **Security Engineer** | | | |
| **Tech Lead (معتمِد / Approver)** | | | |

---

## القسم ح: ملاحظات إضافية / Additional Notes

```
[أضف أي ملاحظات أو معلومات إضافية هنا]
[Add any additional notes or information here]
```

---

## مثال مكتمل: PR #48

<details>
<summary>انقر لرؤية المثال الكامل / Click to see completed example</summary>

| الحقل | القيمة |
|---|---|
| CVE ID | CVE-2024-2965 (SSRF) + CVE-2024-21513 (XXE) |
| CVSS Score | 9.0 (SSRF) / 8.1 (XXE) |
| Package | langchain-community |
| Vulnerable Version | 0.0.16 (backend), 0.0.13 (ai) |
| Fixed Version | 0.3.27 |
| Discovery Date | 2026-02-20 |
| Fix Date | 2026-02-24 |
| PR | https://github.com/sonaiso/sanadcom/pull/48 |
| Total Time | ~96 hours (Medium urgency) |

</details>
