# !/usr/bin/env python

import unittest as unittest
import chart



class TestProcessor(unittest.TestCase):
    def test_should_chart_mongo_throughput_and_latency(self):
        expected = "x:'x', " \
                   "columns:[" \
                   "['x', 30000, 40000]" \
                   ",['load-throughput', 1798.9889, 0]" \
                   ",['wla-throughput', 2049.0405, 2233.0913]" \
                   "]"


        throughput = chart.throughput("test/data/incremental_runs_from_different_hosts")
        self.assertEqual(expected, throughput)


def main():
    unittest.main()


if __name__ == '__main__':
    main()