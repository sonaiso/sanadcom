# مودَعات مولَّدة من Lean

| الملفّ | كيف وُلِّد | ما يفحصه |
|---|---|---|
| `mashru-mujam2.tsv` | في Mashru عند `e4c801ffe9171dadedcc3aae23051ea0953ae361`: `lake build Jisr.AqsamAwamil` ثمّ `lake env lean tools/arabic_corpus/lean/DumpMujam.lean` (يطبع `Jisr.AqsamAwamil.mujam2`: العامل، الصنف، أقسامه) | `mashru_governors.py --check` ومعه `tests/test_mashru_governors.py`: مرآة بايثون تطابق جدول Lean في الصفوف المئة |

ليست نصّ هيئة ولا مرجعًا لغويًّا جديدًا: جدول المالك في Mashru كما يحسبه Lean من مودَعاته. عند تغيّر Mashru يُعاد التوليد وتُسجَّل البصمة.
