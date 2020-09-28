#!/usr/bin/env python
import unittest
import time_series
import os
import pathlib


class TestTimeSeries(unittest.TestCase):
    def test_empty_file(self):
        fname = "empty.dat"
        pathlib.Path(fname).touch()
        with self.assertRaises(IndexError):
            time_series.work(fname, "", None, None, None)
        os.remove(fname)


if __name__ == "__main__":
    unittest.main()
