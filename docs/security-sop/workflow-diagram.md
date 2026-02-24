# مخططات سير العمل / Workflow Diagrams

> **الإصدار / Version:** 1.0 | **المرجع / Reference:** PR #48

---

## 1. Flowchart – دورة حياة معالجة الثغرة الأمنية

```mermaid
flowchart TD
    A([🔍 بدء: اكتشاف الثغرة\nVulnerability Discovered]) --> B{مصدر الاكتشاف\nDiscovery Source}
    B --> |pip-audit / safety| C[مسح محلي\nLocal Scan]
    B --> |Dependabot Alert| D[تنبيه GitHub\nGitHub Alert]
    B --> |NVD / OSV Feed| E[تغذية CVE\nCVE Feed]
    C & D & E --> F[توثيق الثغرة\nDocument Vulnerability]
    F --> G{تقييم CVSS\nCVSS Assessment}
    G --> |CVSS ≥ 9.0\nCritical| H[🔴 إجراء طارئ\nEmergency Response\n< 4 hours]
    G --> |CVSS 7.0–8.9\nHigh| I[🟠 أولوية عالية\nHigh Priority\n< 24 hours]
    G --> |CVSS 4.0–6.9\nMedium| J[🟡 أولوية متوسطة\nMedium Priority\n< 72 hours]
    G --> |CVSS < 4.0\nLow| K[🟢 Sprint التالي\nNext Sprint]
    H & I & J --> L[إنشاء GitHub Issue\nCreate GitHub Issue]
    K --> L
    L --> M[إنشاء branch من main\nCreate branch from main]
    M --> N[تحديث requirements.txt\nUpdate requirements.txt]
    N --> O[اختبار محلي\nLocal Testing]
    O --> P{الاختبار نجح؟\nTests Pass?}
    P --> |لا / No| Q[🔧 تحقيق ومعالجة\nInvestigate & Fix]
    Q --> O
    P --> |نعم / Yes| R[رفع Pull Request\nOpen Pull Request]
    R --> S[مراجعة الكود\nCode Review]
    S --> T{اعتماد الـ PR؟\nPR Approved?}
    T --> |تعليقات\nComments| U[تعديل الكود\nAddress Feedback]
    U --> S
    T --> |مرفوض\nRejected| V{سبب الرفض}
    V --> |مشكلة تقنية| N
    V --> |تصعيد| W[🆘 تصعيد لـ Tech Lead\nEscalate to Tech Lead]
    W --> X[قرار إداري\nManagement Decision]
    X --> N
    T --> |معتمد\nApproved| Y[دمج إلى main\nMerge to main]
    Y --> Z[نشر على Staging\nDeploy to Staging]
    Z --> AA[اختبار Staging\nStaging Testing]
    AA --> AB{Staging نجح؟\nStaging Pass?}
    AB --> |لا / No| AC[🔄 Rollback Staging\nRollback Staging]
    AC --> N
    AB --> |نعم / Yes| AD[نشر على Production\nDeploy to Production]
    AD --> AE[مراقبة Production\nMonitor Production]
    AE --> AF{مستقر؟\nStable?}
    AF --> |لا / No| AG[🔄 Rollback Production\nEmergency Rollback]
    AG --> W
    AF --> |نعم / Yes| AH[مسح نهائي\nFinal pip-audit Scan]
    AH --> AI[إغلاق Issue\nClose Issue]
    AI --> AJ[توثيق الدروس\nDocument Lessons Learned]
    AJ --> AK([✅ اكتمال\nComplete])

    style A fill:#4A90D9,color:#fff
    style AK fill:#27AE60,color:#fff
    style H fill:#E74C3C,color:#fff
    style I fill:#E67E22,color:#fff
    style J fill:#F1C40F
    style K fill:#2ECC71,color:#fff
    style AG fill:#E74C3C,color:#fff
    style AC fill:#E67E22,color:#fff
```

---

## 2. Sequence Diagram – تفاعل الأدوار

```mermaid
sequenceDiagram
    autonumber
    actor Dev as 👨‍💻 Developer
    actor SecEng as 🔐 Security Engineer
    participant GitHub as 🐙 GitHub
    participant CI as ⚙️ CI/CD Pipeline
    participant Scanner as 🔍 Security Scanner
    actor TechLead as 🎯 Tech Lead

    Note over SecEng,Scanner: مرحلة الاكتشاف / Discovery Phase
    SecEng->>Scanner: تشغيل pip-audit / Run pip-audit
    Scanner-->>SecEng: نتائج الثغرات / Vulnerability Results
    SecEng->>GitHub: إنشاء Security Issue / Create Security Issue
    GitHub-->>Dev: إشعار بالمهمة / Task Notification
    GitHub-->>TechLead: إشعار بالثغرة / Vulnerability Alert

    Note over Dev,CI: مرحلة الإصلاح / Remediation Phase
    Dev->>GitHub: إنشاء branch fix/ / Create fix/ branch
    Dev->>Dev: تحديث requirements.txt / Update requirements.txt
    Dev->>Scanner: مسح محلي / Local scan
    Scanner-->>Dev: تأكيد الإصلاح / Fix Confirmed
    Dev->>GitHub: رفع Pull Request / Open Pull Request

    Note over GitHub,CI: مرحلة CI/CD / CI/CD Phase
    GitHub->>CI: تشغيل Pipeline / Trigger Pipeline
    CI->>Scanner: فحص أمني آلي / Automated security scan
    Scanner-->>CI: نتائج المسح / Scan Results
    CI->>CI: تشغيل pytest / Run pytest
    CI-->>GitHub: نتائج Pipeline / Pipeline Results
    GitHub-->>SecEng: طلب مراجعة / Review Request
    GitHub-->>TechLead: طلب اعتماد / Approval Request

    Note over SecEng,TechLead: مرحلة المراجعة / Review Phase
    SecEng->>GitHub: مراجعة الكود / Code Review
    SecEng-->>GitHub: Approve (Security ✅)
    TechLead->>GitHub: مراجعة نهائية / Final Review
    TechLead-->>GitHub: Approve + Merge (Tech Lead ✅)

    Note over GitHub,CI: مرحلة النشر / Deployment Phase
    GitHub->>CI: دمج → تشغيل Deploy Pipeline / Merge → Deploy Pipeline
    CI->>CI: نشر Staging / Deploy to Staging
    CI-->>SecEng: تقرير Staging / Staging Report
    SecEng->>Scanner: فحص Staging / Scan Staging
    Scanner-->>SecEng: Staging نظيف / Staging Clean
    SecEng-->>TechLead: جاهز للإنتاج / Ready for Production
    TechLead->>CI: اعتماد نشر Production / Approve Production Deploy
    CI->>CI: نشر Production / Deploy to Production
    CI-->>TechLead: تأكيد النشر / Deploy Confirmed

    Note over SecEng,GitHub: مرحلة الإغلاق / Closure Phase
    SecEng->>GitHub: إغلاق Issue / Close Issue
    SecEng->>GitHub: رفع Evidence Artifact / Upload Evidence Artifact
    SecEng-->>TechLead: تقرير التسليم / Submission Report
```

---

## 3. State Diagram – حالات الـ Pull Request

```mermaid
stateDiagram-v2
    [*] --> Draft : إنشاء PR\nCreate PR

    Draft --> InReview : طلب المراجعة\nRequest Review
    Draft --> Closed : إلغاء\nCancelled

    InReview --> ChangesRequested : تعليقات المراجع\nReviewer Comments
    InReview --> Approved : موافقة المراجع\nReviewer Approval
    InReview --> Closed : سحب الـ PR\nPR Withdrawn

    ChangesRequested --> InReview : تطبيق التعديلات\nChanges Applied
    ChangesRequested --> Closed : إلغاء\nCancelled

    Approved --> Merged : دمج في main\nMerged to main
    Approved --> ChangesRequested : ملاحظة أخيرة\nLast-minute Comment

    Merged --> DeployedStaging : نشر Staging آلي\nAuto-deploy Staging

    DeployedStaging --> StagingFailed : فشل الاختبار\nTest Failed
    DeployedStaging --> StagingVerified : اجتياز الاختبار\nTest Passed

    StagingFailed --> RolledBack : Rollback تلقائي\nAuto Rollback
    RolledBack --> [*] : إعادة التحقيق\nRe-investigate

    StagingVerified --> DeployedProduction : اعتماد الإنتاج\nProduction Approved

    DeployedProduction --> ProductionFailed : خطأ إنتاجي\nProduction Error
    DeployedProduction --> Complete : استقرار الإنتاج\nProduction Stable

    ProductionFailed --> EmergencyRollback : تراجع طارئ\nEmergency Rollback
    EmergencyRollback --> [*] : تحقيق الحادثة\nIncident Investigation

    Complete --> [*] : إغلاق Issue\nClose Issue ✅

    state InReview {
        [*] --> SecurityReview
        SecurityReview --> TechLeadReview
        TechLeadReview --> [*]
    }

    state DeployedProduction {
        [*] --> Monitoring
        Monitoring --> Verified
        Verified --> [*]
    }
```

---

## 4. Timeline Diagram – مثال PR #48

```mermaid
gantt
    title دورة حياة PR #48 | PR #48 Lifecycle
    dateFormat  YYYY-MM-DD
    axisFormat  %d-%b

    section الاكتشاف / Discovery
    مسح pip-audit               :done, scan,    2026-02-20, 1d
    تقييم CVEs                  :done, assess,  2026-02-20, 1d

    section الإصلاح / Remediation
    إنشاء Issue                  :done, issue,   2026-02-21, 1d
    تحديث requirements          :done, update,  2026-02-24, 1d
    اختبار محلي                 :done, test,    2026-02-24, 1d

    section المراجعة / Review
    فتح Pull Request            :active, pr,    2026-02-24, 2d
    Code Review                 :        cr,    2026-02-25, 1d
    اعتماد الدمج               :        appr,  2026-02-26, 1d

    section النشر / Deployment
    دمج في main                 :        merge, after appr, 1d
    نشر Staging                 :        stg,   after merge, 1d
    اختبار Staging              :        stgT,  after stg, 1d
    نشر Production              :        prod,  after stgT, 1d

    section الإغلاق / Closure
    توثيق وإغلاق               :        close, after prod, 1d
```
