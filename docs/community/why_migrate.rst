Why should I migrate to Charset-Normalizer?
===========================================

There is so many reason to migrate your current project. Here are some of them:

- Remove ANY license ambiguity/restriction for projects bundling Chardet (even indirectly).
- Twice as fast than Chardet in p99 and p95 stats.
- Never return a encoding if not suited for the given decoder. Eg. Never get UnicodeDecodeError!
- Actively maintained, open to contributors. Always was.
- Have the backward compatible function ``detect`` that come from Chardet.
- Truly detect the language used in the text.
- It is, for the first time, really universal! As there is no specific probe per charset.
- The package size is X2~X4 lower than Chardet's (7.0)! (Depends on your arch)
- Propose much more options/public kwargs to tweak the detection as you sees fit!
- Using static typing to ease your development.

And much more..! What are you waiting for? Upgrade now and give us a feedback. (Even if negative)
