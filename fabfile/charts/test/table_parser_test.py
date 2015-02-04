# !/usr/bin/env python

import unittest as unittest

import table_parser
from table_parser import column_defs


class TestProcessor(unittest.TestCase):
    @staticmethod
    def value_of(col, parsed_data):
        return parsed_data[0][column_defs[col]['index']]


    def test_should_parse_values_for_ycsb_run(self):
        d = table_parser.data_table('test/data/single_run_file')

        self.assertEqual('c1', self.value_of('node', d))
        self.assertEqual('2014-11-28', self.value_of('date', d))
        self.assertEqual('09:13', self.value_of('time', d))
        self.assertEqual('mongodb', self.value_of('db', d))
        self.assertEqual('workloada', self.value_of('workload', d))
        self.assertEqual('40000', self.value_of('key-start', d))
        self.assertEqual('2278.1335773101555', self.value_of('throughput', d))
        self.assertEqual('', self.value_of('insert-lat', d))
        self.assertEqual('10343.326877470356', self.value_of('read-lat', d))
        self.assertEqual('14068.371836734694', self.value_of('update-lat', d))
        self.assertEqual('66666', self.value_of('recordcount', d))
        self.assertEqual('7', self.value_of('fieldcount', d))
        self.assertEqual('13', self.value_of('fieldlength', d))
        self.assertEqual('4980.0', self.value_of('operations', d))


    def test_should_parse_values_for_ycsb_load(self):
        d = table_parser.data_table('test/data/single_load_file')

        self.assertEqual('c1', self.value_of('node', d))
        self.assertEqual('2014-11-28', self.value_of('date', d))
        self.assertEqual('09:12', self.value_of('time', d))
        self.assertEqual('mongodb', self.value_of('db', d))
        self.assertEqual('load', self.value_of('workload', d))
        self.assertEqual('40000', self.value_of('key-start', d))
        self.assertEqual('1822.1734357848518', self.value_of('throughput', d))
        self.assertEqual('15806.82891566265', self.value_of('insert-lat', d))
        self.assertEqual('', self.value_of('read-lat', d))
        self.assertEqual('', self.value_of('update-lat', d))
        self.assertEqual('10000', self.value_of('recordcount', d))
        self.assertEqual('10', self.value_of('fieldcount', d))
        self.assertEqual('10', self.value_of('fieldlength', d))
        self.assertEqual('5000', self.value_of('insertcount', d))


    def test_two_runs_should_have_twice_the_results(self):
        one = len(table_parser.data_table('test/data/single_load_file'))
        two = len(table_parser.data_table('test/data/two_incremental_runs'))

        self.assertEqual(two, 2 * one)


def main():
    unittest.main()


if __name__ == '__main__':
    main()