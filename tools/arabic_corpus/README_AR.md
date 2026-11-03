# المدوّنة العربيّة المختومة وخطّ أساس NABT والتشكيل الموقَّع والقراءة والادّعاء (الشرائح S1–S5)

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

## S3: التشكيل الموقَّع

```sh
python tools/arabic_corpus/tashkil.py new corpora/nca ecc-2-2024-ar.pdf --out corpora/nca/tashkil-ecc.tsv   # هيكل: صفّ لكلّ سطر غير فارغ
# المشكِّل البشريّ يملأ عمود vocalized ويكتب معرِّفه في vocalizer (المسجَّل في vocalizers.json)، ثمّ يُوقَّع الملفّ:
# owner-tashkil-ecc.json على نسق Alghanem (signed_by, signed_on, file, sha256, scope=TASHKIL_SIGNED, owner_words)
python tools/arabic_corpus/tashkil.py check corpora/nca corpora/nca/tashkil-ecc.tsv --signature corpora/nca/owner-tashkil-ecc.json
```

- البوّابة ترفض باسمه: توقيعًا ناقصًا أو منحرفًا عن بصمة الملفّ، صفًّا لا يطابق النصّ المختوم (المعرِّف والبصمة والنصّ)، تشكيلًا غيّر حرفًا (لا يُسمح إلّا بالعلامات وٱ)، مشكِّلًا غير مسجَّل، وصفَّ وكيلٍ داخل جدولٍ موقَّع.
- اصطلاح التشكيل هو اصطلاح جسر Alghanem (A116-CANONICAL-TXT-1.1): كلّ صامت بحركة أو سكون، الواو والياء المدّيّتان بسكون، ألف المدّ بعد الفتحة بلا علامة، «ٱَلْ» للتعريف في أوّل الكلمة بسكون اللام ولو قبل حرف شمسيّ، والشدّة والتنوين ومقاعد الهمزة والتاء المربوطة مسموحة. ما خالف الاصطلاح لا يُرفض هنا بل يسمّيه القارئ.
- جدول الوكيل (`scope=TASHKIL_AGENT_SAMPLE_UNSIGNED`) عيّنةُ اختبار لا مرجع؛ المرجع لا يكون إلّا بتوقيع بشريّ مسجَّل.

## S4: القراءة المحكومة (شهادات الكلمات والعوامل)

```sh
python tools/arabic_corpus/qiraa.py corpora/nca/tashkil-ecc.tsv --corpus-dir corpora/nca --signature corpora/nca/owner-tashkil-ecc.json --alghanem-src /path/to/Alghanem --nabt-src /path/to/NABT/src --mashru-src /path/to/Mashru --document-reader --out docs/arabic-corpus/qiraa-ecc.json
python tools/arabic_corpus/qiraa.py ... --check docs/arabic-corpus/qiraa-ecc.json
```

القارئ يشغّل بوّابة S3 على الجدول أوّلًا (التوقيع والختم والربط بالمصدر) ويرفض ما لم تقبله (`TASHKIL_NOT_ACCEPTED`)، ويحمل التقرير بصمة الجدول ونطاقه. لكلّ كلمة: جسر Alghanem (READY أو تعليق باسمه) ← خانات A116 وشهادة شكل NABT (`GENERATED_BY_LAW` أو `UNLICENSED_SHAPE`) ← بحث في جدول العوامل المئة المختوم في Mashru (`SLGE/AwamilTable.lean`، بصمته في التقرير) بالحروف وبعلامات المدخل نفسه (إنّ غير إنْ؛ «ما» بلا علامة يبقى مرشَّحين). هذا بحثٌ لا إعراب: لا معمولَ يُعيَّن ولا تركيبَ يُدَّعى (`authority: LOOKUP_NOT_PARSE`). قارئ النصّ في NABT يُشغَّل اختياريًّا ويُسجَّل جوابه كما هو (مجاله «الجزء المنصَّب لا كلّ العربيّة»).

**مفحوصٌ على عيّنة الوكيل** (لا «مقيس»: العيّنة ليست مرجعًا محجوبًا) (أربع جمل، 18 كلمة، في `tests/test_tashkil_qiraa.py`؛ ليست نصّ الهيئة): الجسر 18/18 READY؛ شهادات NABT 15 مولَّدة بالقانون و3 مرفوضة باسم `UNLICENSED_SHAPE` وكلّها «ٱَلْ» قبل حرف شمسيّ (الجسر يبقي سكون اللام بلا إدغام والقانون يرفض سكونين متتاليين: بقيّة مسمّاة `ARTICLE_LAM_BEFORE_SOLAR_NOT_ASSIMILATED`)؛ 6 مطابقات عوامل؛ قارئ النصّ يؤجّل الجمل الأربع (`UNSUPPORTED_CLAUSE`، `UNSUPPORTED_OPEN_QUESTION`، `CASE_ROLE_MISMATCH`). الفجوات المعلَنة في التقرير: واجهة الحدود بين الكلمات، السوابق المتّصلة (وَ، فَ، بِ)، تعيين المعمول، تعدّد المرشَّحين.

## S5 (الخطوة الأولى): من القراءة إلى النواة، غلاف قرار لكلّ مقطع

```sh
python tools/arabic_corpus/claims.py corpora/nca/tashkil-ecc.tsv --corpus-dir corpora/nca --signature corpora/nca/owner-tashkil-ecc.json --reading docs/arabic-corpus/qiraa-ecc.json --out docs/arabic-corpus/claims-ecc.json
python tools/arabic_corpus/claims.py ... --check docs/arabic-corpus/claims-ecc.json
```

الواقع = المقطع المختوم؛ الأثر = قراءته المشهود لها (كلّ كلمة READY في الجسر ومولَّدة بالقانون في NABT)، فالمقطع غير المقروء كلّه **لا أثرَ له** فتوقفه النواة عند TRACE_CANDIDATE ولا يتولّد منه ادّعاء؛ المحلّ = الوثيقة؛ عقد المجال `nca-text-v1` بعلاقة واحدة «states»؛ الادّعاء = «المصدر يقول: <المقطع بنصّه>» لا إعادة صياغة؛ الربط: الأصل سليم إذا كان الجدول موقَّعًا (`TASHKIL_SIGNED`) وإلّا سُقف الرتبة عند CANDIDATE. الرتبة والبقايا والحكم وترخيص الفعل (`register_normative_statement`، العتبة VERIFIED فلا يُمنح من هذه الشريحة وحدها) والتسليم كلّها من النواة (`backend/knowledge_constitution`) لا من الأداة. التقرير مربوط ببصمة جدول التشكيل وبتقرير S4 للجدول نفسه.

ما ليس في هذه الخطوة: لا استخراج متطلَّب ولا تحليل إلزام ولا انطباق على جهة (`applicability_result = NOT_EVALUATED`) ولا حكم امتثال ولا بيانات تدريب.

**مفحوصٌ على عيّنة الوكيل**: 4 مقاطع ← 3 BLOCKED عند TRACE_CANDIDATE (كلمة «ٱَلْ» قبل شمسيّ غير مشهود لها) إلى المراجعة البشريّة، و1 SUPPORTED برتبة CANDIDATE (نطاق الوكيل) إلى طابور التأجيل، والترخيص غير ممنوح في الأربعة.

## بطاقات العوامل المئة (التفسير من مودَعات Mashru لا من اليد)

```sh
python tools/arabic_corpus/mashru_governors.py --mashru-src /path/to/Mashru --out docs/arabic-corpus/governor-cards.json --explain "إنّ" "على"
python tools/arabic_corpus/mashru_governors.py --mashru-src /path/to/Mashru --check governor-cards-lean.tsv   # مطابقة المرآة بجدول ولّده Lean
```

لكلّ عامل في جدول المالك: صنفه ومعادلاته (`Jisr/Awamil.lean`: الأدوار والحالات بترميز المالك)، وقسمُه اسمًا أو فعلًا أو حرفًا كما يشتقّه `Jisr/AqsamAwamil.lean`: من عائلات المالك في `SLGE/Wad.lean` بسطر قطر الندى، وإلّا من النقل بسطره في مودَع مختوم (المغني، الجنى الداني، الألفية، الكتاب) مع الاقتباس كما أُودع وعلامة الاستدلال. القارئ (`qiraa.py`) يلحق البطاقة وجملتها بكلّ مطابقة عامل، فتحمل القراءة «لماذا» بمصدره: «إنّ»: حرف (قطر الندى، عائلة innaF، السطر 187)؛ من إنّ وأخواتها: تنصب الاسم وترفع الخبر.

مرآةٌ لتعاريف Lean لا جديدَ فيها؛ أرقامها مطابِقة لما يبرهنه Mashru على مودَعه (`mujam_98`: 98/100 لها قسم، 45 من العائلات، 50 حرفًا و27 فعلًا و18 اسمًا، 3 بقسمين، واثنان بلا حكم: شرع وبدأ). مطابقة Jurjani (91 سماعيًّا/7 قياسيّة/2 معنويّة) خارج نطاق Mashru بقرار المالك لأنّ كتابه غير مودَع، فلا تُدّعى هنا.
