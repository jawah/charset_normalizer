import unittest
from charset_normalizer.normalizer import CharsetNormalizerMatches
from charset_normalizer.probe_coherence import ProbeCoherence
from collections import Counter


class TestProbeCoherence(unittest.TestCase):
    def test_obvious_coherence_gap(self):

        should_be_most_coherent = CharsetNormalizerMatches.from_path('../data/sample.1.ar.srt').best().first().coherence

        with open('../data/sample.1.ar.srt', 'r', encoding='mac_cyrillic') as fp:
            r_ = ProbeCoherence(Counter(fp.read())).ratio

        with open('../data/sample.1.ar.srt', 'r', encoding='cp1251') as fp:
            t_ = ProbeCoherence(Counter(fp.read())).ratio

        self.assertLess(
            should_be_most_coherent,
            r_
        )

        self.assertLess(
            should_be_most_coherent,
            t_
        )


if __name__ == '__main__':
    unittest.main()
