---
name: Wrong charset / Detection issue
about: Create a report to help us improve the detection mechanism
title: "[DETECTION]"
labels: help wanted
assignees: ''

---

**Provide the file**
A accessible way of retriving the file concerned. Host it somewhere with untouched encoding.

**Verbose output**
Using the CLI, run `normalizer -v ./my-file.txt` and past the result in here.

```
(venv) >normalizer -v ./data/sample.1.ar.srt
2021-05-21 08:38:44,050 | DEBUG | ascii does not fit given bytes sequence at ALL. 'ascii' codec can't decode byte 0xca in position 54: ordinal not in range(128)
2021-05-21 08:38:44,051 | DEBUG | big5 does not fit given bytes sequence at ALL. 'big5' codec can't decode byte 0xc9 in position 60: illegal multibyte sequence
2021-05-21 08:38:44,051 | DEBUG | big5hkscs does not fit given bytes sequence at ALL. 'big5hkscs' codec can't decode byte 0xc9 in position 60: illegal multibyte sequence
....
```

**Expected encoding**
A clear and concise description of what you expected to get.

**Desktop (please complete the following information):**
 - OS: [e.g. Linux, Windows or Mac]
 - Python version [e.g. 3.5]

**Additional context**
Add any other context about the problem here.
