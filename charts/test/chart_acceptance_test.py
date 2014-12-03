# !/usr/bin/env python

import unittest as unittest
import chart



class TestProcessor(unittest.TestCase):

    def test_multiple_hosts_multiple_runs(self):
        expected = "x:'x', " \
                   "columns:[" \
                   "['x', 10000, 20000]" \
                   ",['load-throughput', 1748.5974, 1716.7574]" \
                   ",['wla-throughput', 2091.4185, 2124.3818]" \
                   "]"

        source_files = "test/data/big_run"
        c = chart.throughput(source_files)
        self.assertEqual(expected, c)

    def test_should_handle_missing_files_without_skewing_data(self):
        expected = "x:'x', " \
                   "columns:[" \
                   "['x', 10000, 20000]" \
                   ",['load-throughput', 1798.9889, 0]" \
                   ",['wla-throughput', 2049.0405, 2233.0913]" \
                   "]"
        source_files = "test/data/incomplete_run_different_hosts"
        self.assertEqual(expected, chart.throughput(source_files))


def main():
    unittest.main()


if __name__ == '__main__':
    main()