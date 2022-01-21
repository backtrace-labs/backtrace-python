import json
import re
import unittest

from backtracepython.utils import parse_json

nan = float("NaN")
inf = float("Infinity")

class TestParseJson(unittest.TestCase):
    def runTest(self):
        self.test_valid_json()
        self.test_invalid_json()

    def test_valid_json(self):
        data_basic = {
            "field": 1,
            "field2": 2,
            "field3": 3,
        }
        data_nested = {
            "field": 1,
            "field2": 2,
            "field3": {
                "nest1": 1,
                "nest2": 2,
            }
        }
        # string values are acceptable
        data_string_nan = {
            "NaN": "NaN",
            "Infinity": "Infinity",
            "-Infinity": "-Infinity",
        }
        # data should not be different from json.dumps function
        self.assertEqual(parse_json(data_basic, False), json.dumps(data_basic))
        self.assertEqual(parse_json(data_nested, False), json.dumps(data_nested))
        self.assertEqual(parse_json(data_string_nan, False), json.dumps(data_string_nan))

    def test_invalid_json(self):
        data_nan = {
            "field": nan,
            "field2": 2,
            "field3": nan
        }
        data_nan_expected = """{
            "field": null,
            "field2": 2,
            "field3": null
        }"""
        data_nested_nan = {
            "field": 1,
            "field2": nan,
            "field3": {
                "nest1": nan,
                "nest2": 2
            }
        }
        data_nested_nan_expected = """{
            "field": 1,
            "field2": null,
            "field3": {
                "nest1": null,
                "nest2": 2
            }
        }"""
        data_string_nan_nan = {
            "NaN": nan,
            "Infinity": inf,
            "-Infinity": -inf
        }
        data_string_nan_nan_expected = """{
            "NaN": null,
            "Infinity": null,
            "-Infinity": null
        }"""
        # data should have illegal values replaced with nulls. Otherwise they should be the same
        self.assertEqual(json.loads(parse_json(data_nan, False)), json.loads(data_nan_expected))
        self.assertEqual(json.loads(parse_json(data_nested_nan, False)), json.loads(data_nested_nan_expected))
        self.assertEqual(json.loads(parse_json(data_string_nan_nan, False)), json.loads(data_string_nan_nan_expected))
        self.assertEqual(json.loads(parse_json(data_string_nan_nan, False)), json.loads(data_string_nan_nan_expected))
