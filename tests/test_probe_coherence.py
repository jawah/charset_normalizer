# coding: utf-8
import unittest
from charset_normalizer.api import from_path


class TestProbeCoherence(unittest.TestCase):
    def test_obvious_coherence_gap(self):

        arabic_coherence = from_path('./data/sample.1.ar.srt').best().first().coherence

        self.assertGreater(
            arabic_coherence,
            0.7
        )


if __name__ == '__main__':
    unittest.main()
