# 🎯 RACI Matrix — مصفوفة المسؤوليات
# SICO GRC Platform — Roles & Responsibilities

**الإصدار:** 1.0  
**تاريخ:** 2026-02-24

---

## تعريف الأدوار

### أدوار الفريق الداخلي (SICO)
| الدور | الوصف |
|---|---|
| **SICO Admin** | مدير المنصة — يملك صلاحية إنشاء وإدارة جميع Tenants |
| **AI Engine** | محرك الذكاء الاصطناعي — يقترح الأدلة ويحدد الفجوات |

### أدوار العميل
| الدور | الوصف |
|---|---|
| **Control Owner** | صاحب الضابط — مسؤول رفع الأدلة الداعمة |
| **Reviewer** | المراجع — يتحقق من الأدلة ويقييم الامتثال |
| **Manager/CISO** | مدير الامتثال أو CISO — يعتمد التقارير النهائية |

### مصطلحات RACI
- **R** = Responsible — المنفذ الفعلي للمهمة
- **A** = Accountable — المسؤول النهائي عن النتيجة
- **C** = Consulted — يُستشار رأيه
- **I** = Informed — يُبلَّغ بالنتيجة

---

## المصفوفة الكاملة

| العملية / النشاط | SICO Admin | Control Owner | Reviewer | Manager / CISO | AI Engine |
|---|:---:|:---:|:---:|:---:|:---:|
| **Onboarding & Setup** | | | | | |
| إنشاء Tenant جديد | R / A | I | I | I | — |
| تحديد نطاق الامتثال (ECC/CCC/PDPL) | R | C | C | A | I |
| إعداد RBAC + SoD | R / A | I | I | C | — |
| تحميل Control Library | R | I | C | A | I |
| تعيين Control Owners | R | — | — | A | — |
| **Evidence Management** | | | | | |
| فتح طلبات الأدلة | R | I | C | I | — |
| رفع الأدلة | I | R / A | I | I | C |
| مراجعة الأدلة والتحقق منها | I | C | R / A | I | C |
| قبول أو رفض الأدلة | I | I | R / A | C | — |
| **Assessment & Gap Analysis** | | | | | |
| إجراء تقييم الضوابط | C | R | R / A | I | R |
| تحديد وتصنيف الفجوات | C | C | R / A | I | R |
| إنشاء تقرير Gap Analysis | R | I | C | I | R |
| **Remediation** | | | | | |
| فتح خطة المعالجة | C | R | C | A | I |
| تنفيذ إجراءات المعالجة | I | R / A | C | I | I |
| التحقق من إغلاق الفجوة | I | C | R / A | I | C |
| **Reporting & Approval** | | | | | |
| إنشاء مسودة التقرير | R | I | C | I | R |
| مراجعة التقرير | I | I | R / A | C | — |
| اعتماد التقرير النهائي | I | I | C | R / A | — |
| تجميد التقرير (Freeze) | R | I | I | A | — |
| **Audit & Export** | | | | | |
| تسجيل Audit Trail الكامل | R / A | — | — | I | — |
| توليد التقرير التنفيذي (عربي/إنجليزي) | R | I | I | A | R |
| تصدير حزمة التقييم الذاتي (NCA) | R / A | I | C | A | R |
| تصدير Evidence Appendix | R | I | C | A | — |

---

## ملاحظات تشغيلية

### فصل المهام الحرج (Critical SoD Rules)
1. **لا يمكن لـ Control Owner مراجعة أدلته بنفسه** — يجب أن يكون Reviewer شخصاً مختلفاً
2. **لا يمكن لـ Reviewer اعتماد التقرير النهائي** — الاعتماد حصراً لـ Manager/CISO
3. **لا يمكن لـ SICO Admin رفع أدلة العميل** — الأدلة ترفعها جهة العميل فقط
4. **تجميد التقرير لا رجعة فيه** — يتطلب موافقة Manager/CISO بتوقيع رقمي

### تصعيد المشكلات (Escalation Path)
```
Control Owner → Reviewer → Manager/CISO → SICO Admin
```
