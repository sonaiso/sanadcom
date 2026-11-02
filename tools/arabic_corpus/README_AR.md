# المدوّنة العربيّة المختومة وخطّ أساس NABT (الشريحتان S1 وS2)

```sh
# S1: ختم نصوص الهيئة الرسميّة (PDF أو نصّ) ببصماتها — المجلّد خاصّ حتى إذن النشر
python tools/arabic_corpus/seal_corpus.py corpora/nca            # يكتب manifest.json والنصوص المستخرجة
python tools/arabic_corpus/seal_corpus.py corpora/nca --check    # يعيد الحساب ويرفض أيّ انحراف

# S2: ماذا يقرأ NABT من المدوّنة كما هي (بلا تشكيل)؟
python tools/arabic_corpus/nabt_baseline.py corpora/nca --nabt-src /path/to/NABT/src --out docs/arabic-corpus/baseline.json
python tools/arabic_corpus/nabt_baseline.py corpora/nca --nabt-src /path/to/NABT/src --check docs/arabic-corpus/baseline.json
```

- NABT لا يخمّن الحركات؛ النصّ الرسميّ غير المشكول يُؤجَّل كلمةً كلمة باسم الرفض. التقرير هو قائمة عمل الشريحة S3 (تشكيل موقَّع)، لا درجة.
- الاختبارات في `tests/` تستعمل نصًّا قصيرًا كتبه الوكيل (لا نصّ الهيئة) وقارئًا مزيّفًا للتجميع، واختبارًا تكامليًّا مع NABT يُتخطّى إن لم يُوجد.
