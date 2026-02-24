# 🔄 Workflow Diagrams — مخططات سير العمل
# SICO GRC Platform

**الإصدار:** 1.0  
**تاريخ:** 2026-02-24

---

## Workflow 1 — دورة حياة الضابط الكاملة (Control Lifecycle)

```mermaid
flowchart TD
    A([🏢 فتح Tenant]) --> B[🎯 تحديد النطاق\nECC / CCC / PDPL]
    B --> C[📋 تحميل Control Library\nمكتبة الضوابط]
    C --> D[👤 تعيين Control Owners\nأصحاب الضوابط]
    D --> E[📤 إرسال طلبات الأدلة\nتلقائياً]
    E --> F{هل رُفع الدليل؟}
    F -- نعم --> G[🔍 مراجعة الدليل\nبواسطة Reviewer]
    F -- لا --> H[⏰ تذكير تلقائي\nللمسؤول]
    H --> F
    G --> I{هل الدليل مقبول؟}
    I -- مقبول ✅ --> J[✅ إغلاق الضابط\nControl Closed]
    I -- مرفوض ❌ --> K[🔴 تسجيل فجوة\nGap Identified]
    K --> L[📝 فتح خطة معالجة\nRemediation Plan]
    L --> M[🔧 تنفيذ المعالجة\nControl Owner]
    M --> E
    J --> N[📊 تجميع نتائج التقييم\nAssessment Results]
    N --> O[📄 إنشاء مسودة التقرير\nDraft Report]
    O --> P[👔 اعتماد المدير / CISO\nApproval]
    P --> Q([🔒 تجميد التقرير\nFrozen — Audit-Ready])
```

---

## Workflow 2 — دورة الأدلة (Evidence Lifecycle)

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Requested : طلب دليل من النظام
    Requested --> Uploaded : رفع بواسطة Control Owner
    Uploaded --> Under_Review : إرسال للمراجعة
    Under_Review --> Approved : قبول الدليل ✅
    Under_Review --> Rejected : رفض الدليل ❌
    Rejected --> Requested : إعادة الطلب مع ملاحظات
    Approved --> Linked : ربط بالضابط في النظام
    Linked --> [*] : إغلاق الضابط

    note right of Approved
        يُسجَّل في Audit Trail
        مع timestamp وهوية المراجع
    end note
```

---

## Workflow 3 — دورة التقرير (Report Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> Draft : إنشاء تقرير تلقائي
    Draft --> Under_Review : إرسال للمراجعة
    Under_Review --> Draft : إعادة للتعديل\n(مع ملاحظات)
    Under_Review --> Approved : اعتماد Reviewer
    Approved --> Frozen : تجميد نهائي\n(CISO / Manager)
    Frozen --> [*] : جاهز للتدقيق / التصدير

    note right of Frozen
        🔒 للقراءة فقط
        Audit Trail كامل
        قابل للتصدير فقط
    end note
```

---

## Workflow 4 — مسار Onboarding (P1 Priority)

```mermaid
flowchart LR
    A([🚀 بداية]) --> B["إنشاء Tenant\n(Multi-tenant)"]
    B --> C["RBAC + SoD\nتعيين الأدوار وفصل المهام"]
    C --> D{اختر الإطار}
    D --> |ECC| E["تحميل ECC\nControl Library\n(147 ضابط)"]
    D --> |CCC| F["تحميل CCC\nControl Library\n(ضوابط السحابة)"]
    D --> |PDPL| G["تحميل PDPL\nControl Library\n(حماية البيانات)"]
    D --> |الكل| H["Unified Library\nمكتبة موحدة كاملة"]
    E & F & G & H --> I["Evidence Catalog\n+ Evidence Policy\nكتالوج الأدلة"]
    I --> J["Assessment & Gap\nWorkflow\nتقييم وكشف فجوات"]
    J --> K["Self-Assessment\nتقييم ذاتي"]
    K --> L["Approved Report\nتقرير معتمد"]
    L --> M(["✅ جاهز للتدقيق\nAudit-Ready"])
```

---

## Workflow 5 — مسار المعالجة (Remediation Flow)

```mermaid
flowchart TD
    A([🔴 فجوة مكتشفة]) --> B{تصنيف الفجوة}
    B --> |Critical| C["🚨 معالجة فورية\n7 أيام"]
    B --> |High| D["🔴 معالجة عاجلة\n30 يوماً"]
    B --> |Medium| E["🟡 معالجة مجدولة\n90 يوماً"]
    B --> |Low| F["🟢 تحسين مستقبلي\n180 يوماً"]
    C & D & E & F --> G["📝 فتح Remediation Plan\nخطة المعالجة"]
    G --> H["👤 تعيين مسؤول\n+ موعد نهائي"]
    H --> I["🔧 تنفيذ الإجراء التصحيحي"]
    I --> J["📎 رفع دليل المعالجة"]
    J --> K["🔍 إعادة تقييم الضابط"]
    K --> L{هل أُغلقت الفجوة؟}
    L -- نعم ✅ --> M["✅ إغلاق الفجوة\n+ تحديث التقرير"]
    L -- لا ❌ --> N["🔄 مراجعة الخطة\nوتمديد الموعد"]
    N --> I
    M --> O(["📊 تقرير محدَّث"])
```

---

## Workflow 6 — مسار AI (Evidence Gap Suggestions)

```mermaid
flowchart TD
    A([🤖 AI Engine]) --> B["تحليل الضوابط\nالمفتوحة"]
    B --> C["مقارنة مع\nEvidence Catalog"]
    C --> D{هل هناك\nفجوة واضحة؟}
    D -- نعم --> E["اقتراح دليل\nمناسب للضابط"]
    D -- لا --> F["تأكيد الامتثال\nواقتراح التحسينات"]
    E --> G["إرسال اقتراح\nلـ Control Owner"]
    G --> H["Control Owner\nيراجع الاقتراح"]
    H --> I{قَبِل الاقتراح؟}
    I -- نعم --> J["رفع الدليل\nالمقترح"]
    I -- لا --> K["تجاهل الاقتراح\nأو تعديله"]
    J --> L(["✅ الضابط قيد المراجعة"])
```
