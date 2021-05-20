<h1 align="center">Charset Detection, for Everyone 👋 <a href="https://twitter.com/intent/tweet?text=The%20Real%20First%20Universal%20Charset%20%26%20Language%20Detector&url=https://www.github.com/Ousret/charset_normalizer&hashtags=python,encoding,chardet,developers"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"/></a></h1>

<p align="center">
  <sup>The Real First Universal Charset Detector</sup><br>
  <a href="https://travis-ci.org/Ousret/charset_normalizer">
    <img src="https://travis-ci.org/Ousret/charset_normalizer.svg?branch=master"/>
  </a>
  <a href="https://pypi.org/project/charset-normalizer">
    <img src="https://img.shields.io/pypi/pyversions/charset_normalizer.svg?orange=blue" />
  </a>
  <a href="https://app.codacy.com/project/Ousret/charset_normalizer/dashboard">
    <img alt="Code Quality Badge" src="https://api.codacy.com/project/badge/Grade/a0c85b7f56dd4f628dc022763f82762c"/>
  </a>
  <a href="https://codecov.io/gh/Ousret/charset_normalizer">
      <img src="https://codecov.io/gh/Ousret/charset_normalizer/branch/master/graph/badge.svg" />
  </a>
  <a href='https://charset-normalizer.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/charset-normalizer/badge/?version=latest' alt='Documentation Status' />
  </a>
  <a href="https://pepy.tech/project/charset-normalizer/">
    <img alt="Download Count Total" src="https://pepy.tech/badge/charset-normalizer" />
  </a>
</p>

> A library that helps you read text from an unknown charset encoding.<br /> Motivated by `chardet`,
> I'm trying to resolve the issue by taking a new approach.
> All IANA character set names for which the Python core library provides codecs are supported.

<p align="center">
  >>>>> <a href="https://charsetnormalizerweb.ousret.now.sh" target="_blank">❤️ Try Me Online Now, Then Adopt Me ❤️ </a> <<<<<
</p>

This project offers you an alternative to **Universal Charset Encoding Detector**, also known as **Chardet**.

| Feature       | [Chardet](https://github.com/chardet/chardet)       | Charset Normalizer | [cChardet](https://github.com/PyYoshi/cChardet) |
| ------------- | :-------------: | :------------------: | :------------------: |
| `Fast`         | ❌<br>          | ❌<br>             | :heavy_check_mark: <br> |
| `Universal**`     | ❌            | :heavy_check_mark:                 | ❌ |
| `Reliable` **without** distinguishable standards | ❌ | :heavy_check_mark: | :heavy_check_mark: |
| `Reliable` **with** distinguishable standards | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| `Free & Open`  | :heavy_check_mark:             | :heavy_check_mark:                | :heavy_check_mark: |
| `License` | LGPL-2.1 | MIT | MPL-1.1
| `Native Python` | :heavy_check_mark: | :heavy_check_mark: | ❌ |
| `Detect spoken language` | ❌ | :heavy_check_mark: | N/A |
| `Supported Encoding` | 30 | :tada: [92](https://charset-normalizer.readthedocs.io/en/latest/support.html)  | 40

| Package       | Accuracy       | Mean per file (ns) | File per sec (est) |
| ------------- | :-------------: | :------------------: | :------------------: |
|      [chardet](https://github.com/chardet/chardet)       |     93.5 %     |     126 081 168 ns      |       7.931 file/sec        |
|      [cchardet](https://github.com/PyYoshi/cChardet)      |     97.0 %     |      1 668 145 ns       |      **599.468 file/sec**      |
| charset-normalizer |    **97.25 %**     |     209 503 253 ns      |       4.773 file/sec    |

<p align="center">
<img src="https://i.imgflip.com/373iay.gif" alt="Reading Normalized Text" width="226"/><img src="https://media.tenor.com/images/c0180f70732a18b4965448d33adba3d0/tenor.gif" alt="Cat Reading Text" width="200"/>

*\*\* : They are clearly using specific code for a specific encoding even if covering most of used one*<br> 

## Your support

Please ⭐ this repository if this project helped you!

## ✨ Installation

Using PyPi
```sh
pip install charset_normalizer
```

## 🚀 Basic Usage

### CLI
This package comes with a CLI

```
usage: normalizer [-h] [--verbose] [--normalize] [--replace] [--force]
                  file [file ...]
```

```bash
normalizer ./data/sample.1.fr.srt
```

```
+----------------------+----------+----------+------------------------------------+-------+-----------+
|       Filename       | Encoding | Language |             Alphabets              | Chaos | Coherence |
+----------------------+----------+----------+------------------------------------+-------+-----------+
| data/sample.1.fr.srt |  cp1252  |  French  | Basic Latin and Latin-1 Supplement | 0.0 % |  84.924 % |
+----------------------+----------+----------+------------------------------------+-------+-----------+
```

### Python
*Just print out normalized text*
```python
from charset_normalizer import CharsetNormalizerMatches as CnM
print(CnM.from_path('./my_subtitle.srt').best().first())
```

*Normalize any text file*
```python
from charset_normalizer import CharsetNormalizerMatches as CnM
try:
    CnM.normalize('./my_subtitle.srt') # should write to disk my_subtitle-***.srt
except IOError as e:
    print('Sadly, we are unable to perform charset normalization.', str(e))
```

*Upgrade your code without effort*
```python
from charset_normalizer import detect
```

The above code will behave the same as **chardet**.

See the docs for advanced usage : [readthedocs.io](https://charset-normalizer.readthedocs.io/en/latest/)

## 😇 Why

When I started using Chardet, I noticed that it was not suited to my expectations, and I wanted to propose a
reliable alternative using a completely different method. Also! I never back down on a good challenge !

I **don't care** about the **originating charset** encoding, because **two different tables** can
produce **two identical files.**
What I want is to get readable text, the best I can. 

In a way, **I'm brute forcing text decoding.** How cool is that ? 😎

Don't confuse package **ftfy** with charset-normalizer or chardet. ftfy goal is to repair unicode string whereas charset-normalizer to convert raw file in unknown encoding to unicode.

## 🍰 How

  - Discard all charset encoding table that could not fit the binary content.
  - Measure chaos, or the mess once opened with a corresponding charset encoding.
  - Extract matches with the lowest mess detected.
  - Finally, if there is too much match left, we measure coherence.

**Wait a minute**, what is chaos/mess and coherence according to **YOU ?**

*Chaos :* I opened hundred of text files, **written by humans**, with the wrong encoding table. **I observed**, then
**I established** some ground rules about **what is obvious** when **it seems like** a mess.
 I know that my interpretation of what is chaotic is very subjective, feel free to contribute in order to
 improve or rewrite it.

*Coherence :* For each language there is on earth, we have computed ranked letter appearance occurrences (the best we can). So I thought
that intel is worth something here. So I use those records against decoded text to check if I can detect intelligent design.

## ⚡ Known limitations

  - Not intended to work on non (human) speakable language text content. eg. crypted text.
  - Language detection is unreliable when text contains two or more languages sharing identical letters.
  - Not well tested with tiny content.

## 👤 Contributing

Contributions, issues and feature requests are very much welcome.<br />
Feel free to check [issues page](https://github.com/ousret/charset_normalizer/issues) if you want to contribute.

## 📝 License

Copyright © 2019 [Ahmed TAHRI @Ousret](https://github.com/Ousret).<br />
This project is [MIT](https://github.com/Ousret/charset_normalizer/blob/master/LICENSE) licensed.

Letter appearances frequencies used in this project © 2012 [Denny Vrandečić](http://denny.vrandecic.de)
