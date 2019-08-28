
Using program `bench.py`.<br>

Required (Available via pip) :

- tqdm
- chardet
- charset_normalizer
- prettytable

Bellow results are using **nanoseconds** as unit.

| File       | [Chardet](https://github.com/chardet/chardet)       | [cChardet](https://github.com/PyYoshi/cChardet) | Charset Normalizer |
| ------------- | :-------------: | :------------------: | :------------------: |
| `sample.1.ar.srt` |  705 119 790  | 24 348 958 |     34 470 625     |
| `sample.1.fr.srt` |   94 098 176  | 1 073 397  |    122 536 469     |
| `sample.1.gr.srt` |  128 603 257  | 8 217 624  |     36 972 182     |
| `sample.1.he.srt` |  300 661 169  | 11 792 028 |     73 381 774     |
| `sample.1.hi.srt`  |    572 238    |  192 271   |     5 527 538      |
| `sample.1.ru.srt` |   47 116 035  | 8 397 738  |     30 111 175     |
| `sample.1.tu.srt` |   6 352 253   |  110 794   |     12 371 315     |
| `sample.2.ar.srt` |  692 033 157  | 24 020 717 |     32 666 399     |
| `sample.3.ar.srt` |     9 424     |    997     |     13 309 962     |
| `sample.4.ar.srt` |  356 634 446  | 13 249 616 |     18 681 878     |
| `sample.5.ar.srt` | 1 001 263 340 |  408 416   |     25 874 928     |
| `sample-chinese.txt` |   11 161 636  |  409 296   |     6 391 593      |
| `sample-greek-2.txt` |   7 768 267   |  261 484   |     2 198 826      |
| `sample-greek.txt` |   7 720 740   |  257 420   |     1 532 783      |
| `sample-hebrew-2.txt` |   4 863 929   |  159 423   |     3 622 851      |
| `sample-hebrew.txt` |   11 799 499  |   12 690   |     3 129 855      |
| `sample-korean.txt` |   8 491 067   |  233 762   |     3 334 189      |
| `sample-russian-2.txt` |   23 425 606  |   14 338   |     2 513 368      |
| `sample-russian.txt` |   15 952 528  |  508 425   |     3 846 456      |
| `sample-turkish.txt` |   13 261 380  |  379 785   |     6 939 200      |

Ranking by performance :
- 1st cChardet
- 2nd Charset Normalizer
- 3th Chardet
