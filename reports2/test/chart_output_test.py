# !/usr/bin/env python

import unittest as unittest


class TestProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print 'setting up'


    @classmethod
    def tearDownClass(self):
        print 'tearing down'


    def test_should_do_something(self):
        print 'something useful will go here'



def main():
    unittest.main()


if __name__ == '__main__':
    main()