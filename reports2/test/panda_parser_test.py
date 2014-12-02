# !/usr/bin/env python

import unittest as unittest
import panda_parser

class TestProcessor(unittest.TestCase):

    columns = {'one': {'index': 0, 'Name': 'key', 'dtype': 'object'},
               'two': {'index': 1, 'Name': 'db', 'dtype': 'object'},
               'three': {'index': 2, 'Name': 'luckynumber', 'dtype': 'float32'}
    }

    data = [[
                'c1',
                'mongodb',
                '13'
            ]]

    def test_should_convert_basic_table_to_panda_columns(self):
        panda = panda_parser.convert_to_panda(self.data, self.columns)

        self.assertEqual('c1', panda['one'][0])
        self.assertEqual('mongodb', panda['two'][0])


    def test_should_convert_different_data_types_as_defined_in_column_definition(self):
        panda = panda_parser.convert_to_panda(self.data, self.columns)

        self.assertEqual('c1', panda['one'][0])
        self.assertEqual(13, panda['three'][0])


def main():
    unittest.main()


if __name__ == '__main__':
    main()