import sys

try:
    import unicodedata2  # type: ignore
    sys.modules['unicodedata'] = unicodedata2
except ImportError:
    pass
