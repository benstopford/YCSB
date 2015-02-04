# !/usr/bin/env python

import unittest as unittest

import panda_parser


class TestProcessor(unittest.TestCase):
    columns = {'col1': {'index': 0, 'Name': 'key', 'dtype': 'object'},
               'col2': {'index': 1, 'Name': 'db', 'dtype': 'object'},
               'col3': {'index': 2, 'Name': 'luckynumber', 'dtype': 'float32'}
    }

    data = [['c1', 'mongodb', '13']]

    larger = [['c1', 'mongodb', '13'],
              ['c1', 'mongodb', '14'],
              ['c1', 'mongodb', '17']]

    def test_should_convert_basic_table_to_panda_columns(self):
        panda = panda_parser.convert_to_panda(self.data, self.columns)

        self.assertEqual('c1', panda['col1'][0])
        self.assertEqual('mongodb', panda['col2'][0])


    def test_should_convert_different_data_types_as_defined_in_column_definition(self):
        panda = panda_parser.convert_to_panda(self.data, self.columns)

        print panda

        self.assertEqual('c1', panda['col1'][0])
        self.assertEqual(13, panda['col3'][0])

    def test_should_convert_something_larger(self):
        panda = panda_parser.convert_to_panda(self.larger, self.columns)
        self.assertEqual(3, len(panda))
        self.assertEqual(13, panda['col3'][0])
        self.assertEqual(14, panda['col3'][1])
        self.assertEqual(17, panda['col3'][2])




def main():
    unittest.main()


if __name__ == '__main__':
    main()