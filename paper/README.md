## State of the art

pre-requisite
-------------

  - chardet
  - cchardet
  - charset-normalizer

Thoses tests are running on charset-normalizer (1.3.1), chardet (3.0.4) and cchardet (2.1.4).

  - files used in python chardet tests
  - files used in python charset-normalizer
  - script features.py

how it is computed
------------------

  - `from time import perf_counter_ns` for performance measure
  - reading file before measure
  - using folder name as encoding hint (considering it is the right one)
  - when guessed and not equal to target encoding try to verify if it matter

*if it matter* : Means if a package guessed cp1252 instead of cp1254, decode bytes using both and compare output string. 
If equal, then it does not matter.

## Global results

| Package       | Accuracy       | Mean per file (ns) | File per sec (est) |
| ------------- | :-------------: | :------------------: | :------------------: |
|      [chardet](https://github.com/chardet/chardet)       |     93.5 %     |     126 081 168 ns      |       7.931 file/sec        |
|      [cchardet](https://github.com/PyYoshi/cChardet)      |     97.0 %     |      1 668 145 ns       |      **599.468 file/sec**      |
| charset-normalizer |    **97.25 %**     |     209 503 253 ns      |       4.773 file/sec    |

### Per encoding

ascii
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |       201824       |      4954.812      |                            |
|      cchardet      |    100.0     |       53517        |     18685.651      |                            |
| charset-normalizer |     75.0     |      48069575      |       20.803       |                            |

big5
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |     100.0     |     187318613      |       5.338        |                            |
|      cchardet      |     100.0     |       420464       |      2378.325      |                            |
| charset-normalizer |     100.0     |      29030648      |       34.446       |                            |

cp932
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |     281405894      |       3.554        |                            |
|      cchardet      |    0.0      |       448856       |      2227.886      |         shift_jis          |
| charset-normalizer |    100.0     |     407520555      |       2.454        |                            |

cp949
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |     235318707      |        4.25        |                            |
|      cchardet      |    50.0     |       275061       |      3635.557      |           euc_kr           |
| charset-normalizer |    100.0     |     283099072      |       3.532        |                            |


euc_jp
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |     285472520      |       3.503        |                            |
|      cchardet      |    96.55     |       152344       |      6564.092      |           cp1252           |
| charset-normalizer |    96.55     |     223891487      |       4.466        |           cp1252           |

euc_kr
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |     206658004      |       4.839        |                            |
|      cchardet      |    100.0     |       379409       |      2635.678      |                            |
| charset-normalizer |    96.88     |     237868022      |       4.204        |           gb2312           |

gb2312
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |     204280068      |       4.895        |                            |
|      cchardet      |    75.0     |       406609       |      2459.365      |          gb18030           |
| charset-normalizer |    90.0     |     267700099      |       3.736        |  euc_jis_2004, big5hkscs   |


cp855
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      48681383      |       20.542       |                            |
|      cchardet      |    100.0     |      3109405       |      321.605       |                            |
| charset-normalizer |    100.0     |     131318072      |       7.615        |                            |

cp866
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      34948580      |       28.613       |                            |
|      cchardet      |    100.0     |      2120040       |      471.689       |                            |
| charset-normalizer |    100.0     |     134351478      |       7.443        |                            |

iso2022_jp
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  100.0     |       487661       |      2050.605      |                            |
|      cchardet      |  100.0     |       11730        |     85251.492      |                            |
| charset-normalizer |  100.0     |      53079390      |       18.84        |                            |


iso2022_kr
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  100.0     |       80494        |     12423.286      |                            |
|      cchardet      |  100.0     |        8798        |     113662.196     |                            |
| charset-normalizer |  100.0     |      28608808      |       34.954       |                            |


latin_1
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |   100.0     |      10655475      |       93.848       |                            |
|      cchardet      |   100.0     |       158693       |      6301.475      |                            |
| charset-normalizer |   100.0     |     219482041      |       4.556        |                            |


iso8859_2
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  9.09     |      59510154      |       16.804       |          latin_1           |
|      cchardet      |  100.0     |      1072225       |       932.64       |                            |
| charset-normalizer |  100.0     |     364305515      |       2.745        |                            |


iso8859_5
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  100.0     |      41274746      |       24.228       |                            |
|      cchardet      |  100.0     |      1931337       |      517.776       |                            |
| charset-normalizer |  100.0     |     235748017      |       4.242        |                            |


iso8859_6
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  0.0      |      8770859       |      114.014       |        mac_cyrillic        |
|      cchardet      |  100.0     |       248962       |      4016.677      |                            |
| charset-normalizer |  100.0     |      58873846      |       16.985       |                            |

iso8859_7
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  90.91     |      26917723      |       37.15        |           cp1253           |
|      cchardet      |  100.0     |       475691       |      2102.205      |                            |
| charset-normalizer |  100.0     |     219005790      |       4.566        |                            |

iso8859_9
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  0.0      |      16149994      |       61.92        |          latin_1           |
|      cchardet      |  100.0     |       303994       |      3289.539      |                            |
| charset-normalizer |  33.33     |     313328579      |       3.192        |           cp1252           |

koi8_r
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      48102976      |       20.789       |                            |
|      cchardet      |    100.0     |      4506055       |      221.924       |                            |
| charset-normalizer |    100.0     |     285609163      |       3.501        |                            |


mac_cyrillic
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       | 100.0     |      39849823      |       25.094       |                            |
|      cchardet      | 100.0     |      2161876       |      462.561       |                            |
| charset-normalizer | 100.0     |     273638883      |       3.654        |                            |


shift_jis
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |  100.0     |     261271302      |       3.827        |                            |
|      cchardet      |  100.0     |       199649       |      5008.79       |                            |
| charset-normalizer |  96.67     |     394586122      |       2.534        |           cp932            |


tis_620
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |   100.0     |      89417757      |       11.183       |                            |
|      cchardet      |   100.0     |      2988084       |      334.663       |                            |
| charset-normalizer |   100.0     |     367614610      |        2.72        |                            |


utf_16
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |       24339        |     41086.322      |                            |
|      cchardet      |    100.0     |        5718        |     174886.324     |                            |
| charset-normalizer |    100.0     |      99274930      |       10.073       |                            |


utf_32
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |       39001        |     25640.368      |                            |
|      cchardet      |    100.0     |        9383        |     106575.722     |                            |
| charset-normalizer |    100.0     |     181745938      |       5.502        |                            |


utf_8
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      86177619      |       11.604       |                            |
|      cchardet      |    100.0     |       53297        |     18762.782      |                            |
| charset-normalizer |    100.0     |     275800555      |       3.626        |                            |


cp1250
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    16.67     |     570631080      |       1.752        |      cp1252, latin_1       |
|      cchardet      |    100.0     |      12933035      |       77.321       |                            |
| charset-normalizer |    100.0     |      86223475      |       11.598       |                            |


cp1251
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      39826493      |       25.109       |                            |
|      cchardet      |    100.0     |      2292002       |       436.3        |                            |
| charset-normalizer |    100.0     |      68469359      |       14.605       |                            |


cp1252
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      28613134      |       34.949       |                            |
|      cchardet      |    50.0     |       330630       |      3024.529      |    iso8859_7, iso8859_9    |
| charset-normalizer |    50.0     |     200121270      |       4.997        |           cp437            |


cp1253
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    66.67     |      47471533      |       21.065       |         iso8859_7          |
|      cchardet      |    100.0     |      2930658       |       341.22       |                            |
| charset-normalizer |    100.0     |     168027309      |       5.951        |                            |


cp1254
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    0.0      |      3659364       |      273.272       |          latin_1           |
|      cchardet      |    100.0     |       84747        |     11799.828      |                            |
| charset-normalizer |    0.0      |      77320217      |       12.933       |           cp1252           |


cp1255
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    100.0     |      93093102      |       10.742       |                            |
|      cchardet      |    100.0     |      2764209       |      361.767       |                            |
| charset-normalizer |    100.0     |     119266978      |       8.385        |                            |

cp1256
-----

|      Package       |  Accuracy | Mean per file (ns) | File per sec (est) | Confuse it with (sometime) |
| ------------- | :-------------: | :------------------: | :------------------: | :------------------: |
|      chardet       |    0.0      |     437728948      |       2.285        |        mac_cyrillic        |
|      cchardet      |    100.0     |      14977980      |       66.765       |                            |
| charset-normalizer |    100.0     |     336711209      |        2.97        |                            |

