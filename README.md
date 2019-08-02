<h1 align="center">Welcome to Charset for Human 👋</h1>

<p align="center">
  <img src="https://img.shields.io/pypi/pyversions/charset_normalizer.svg?orange=blue" />
  <a href="https://github.com/ousret/charset_normalizer/blob/master/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-purple.svg" target="_blank" />
  </a>
</p>

> Library that help you read human* written text from unknown charset encoding.<br /> Project motivated by `chardet`, I'm trying to resolve the issue by taking another approach.

This project offer you a alternative to **Universal Charset Encoding Detector**, also known as **Chardet**.
Also as of July, August 2019 it's still experimental. Use it with caution.

| Feature       | [Chardet](https://github.com/chardet/chardet)       | Charset Normalizer |
| ------------- | :-------------: | :------------------: |
| `Fast**`         | ✅ <br>⚡            | ❌<br> 🐌             |
| `Universal`     | ✅            | ✅                 |
| `Reliable` **without** distinguishable standards | ❌ | ✅ |
| `Reliable` **with** distinguishable standards | ✅ | ✅ |
| `Free & Open`  | ✅             | ✅                |

<p align="center">
<img src="https://i.imgflip.com/373iay.gif" alt="Reading Normalized Text" width="226"/><img src="https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif" alt="Cat Reading Text" width="200"/>

<small>Cats are going to enjoy newly decoded text</small>
<p> 

Chardet has weaknesses where Charset Normalizer has not and vice versa. 
You could combine the strength of both lib to reach near perfect detection. 💪

<small>\*\*  : Fast when there is distinguishable standards.</small>
<small>\* : When written, should not be gibberish.</small>

## Your support

Please ⭐ this repository if this project helped you!

## ✨ Installation

Using PyPi
```sh
pip install charset_normalizer
```

## 🚀 Basic Usage

#### Just print out normalized text
```python
from charset_normalizer import CharsetNormalizerMatches as CnM

matches = CnM.from_path('./my_subtitle.srt')

if len(matches) > 0:
    print(
        str(matches.best().first())
    )
```

#### Convert any text file to UTF-8
```python
from charset_normalizer import CharsetNormalizerMatches as CnM
try:
    CnM.normalize('./my_subtitle.srt') # should write to disk my_subtitle-***.srt
except IOError as e:
    print('Sadly, we are unable to perform charset normalization.', str(e))
```


See wiki for advanced usages. *Todo, not yet available.*

## 😇 Why

When I started using Chardet, I noticed that this library was wrong most of the time 
when it's not about Unicode, Gb or Big5. That because some charset are easily identifiable 
because of there standards and Chardet does a really good job at identifying them.

I **don't care** about the **originating charset** encoding, that because **two different table** can 
produce **two identical file.**
What I want is to get readable text, the best I can.

In a way, **I'm brute forcing text decoding.** How cool is that ? 😎

## 🍰 How

- Discard all charset encoding table that could not fit the binary content.
- Measure chaos, or the mess once opened with a corresponding charset encoding.
- Extract matches with the lowest mess detected.
- Finally, if there is too much match left, we measure coherence.

**Wait a minute**, what is chaos/mess and coherence according to **YOU ?**

*Chaos :* I opened hundred of text files, **written by humans**, with the wrong encoding table. Then **I observed**, then 
**I established** some ground rules about **what is obvious** when **it's seems like** a mess.
 I know that my interpretation of what is chaotic is very subjective, feel free to contribute in order to 
 improve or rewrite it.
 
 *Coherence :* For each language there is on earth (the best we can), we have computed letter appearance occurrences ranked. So I thought that
 those intel are worth something here. So I use those records against decoded text to check if I can detect intelligent design.
 
## 👤 Contributing

Contributions, issues and feature requests are very much welcome.<br />
Feel free to check [issues page](https://github.com/ousret/charset_normalizer/issues) if you want to contribute.

## 📝 License

Copyright © 2019 [Ahmed TAHRI @Ousret](https://github.com/Ousret).<br />
This project is [MIT](https://github.com/Ousret/charset_normalizer/blob/master/LICENSE) licensed.

Letter appearances frequencies used in this project © 2012 [Denny Vrandečić](http://denny.vrandecic.de)
