import sys
from charset_normalizer.legacy import detect


def charset_normalizer_hook(exctype, value, traceback):
    if exctype == UnicodeDecodeError:
        cp_detection = detect(value.object)
        if cp_detection['encoding'] is not None:
            value.reason = value.reason+'; you may want to consider {} codec for this sequence.'.format(cp_detection['encoding'])

    sys.__excepthook__(exctype, value, traceback)


sys.excepthook = charset_normalizer_hook

try:
    import unicodedata2
    sys.modules['unicodedata'] = unicodedata2
except ImportError:
    pass
