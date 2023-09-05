#!/bin/python3
import unittest
import os
import hashlib
import tempfile

from seedai import save_seeds
from data_processor import extract_values

class TestSaveSeeds(unittest.TestCase):

	def setUp(self):
		# Create a temporary directory for each test
		self.corpus_dir = tempfile.mkdtemp()

	def test_save_seeds(self):
		outputs = ["\u00ff\u0000", "\u0000", "\u00ffhello world\u0001"] # \u00ff -> 0xC3, 0xBF
		expected_bytes_list = [bytearray([0xc3, 0xbf, 0x00]), bytearray([0x00]), bytearray([0xc3, 0xbf]) +  b'hello world' + bytearray([0x01])]

		save_seeds(self.corpus_dir, outputs)

		# For each output, check if the corresponding file exists and its content is correct
		for idx, output in enumerate(outputs):
			sha1_hash = hashlib.sha1(expected_bytes_list[idx]).hexdigest()
			file_path = os.path.join(self.corpus_dir, sha1_hash)

			self.assertTrue(os.path.exists(file_path), f"File {file_path} does not exist")

			with open(file_path, 'rb') as file:
				content = file.read()
				self.assertEqual(expected_bytes_list[idx], content)

	def tearDown(self):
		# Cleanup after each test to remove temporary directory
		for root, dirs, files in os.walk(self.corpus_dir, topdown=False):
			for name in files:
				os.remove(os.path.join(root, name))
			for name in dirs:
				os.rmdir(os.path.join(root, name))
		os.rmdir(self.corpus_dir)


class TestDataProcessor(unittest.TestCase):
	def test_extract_values(self):
		# Ignore escaped quotes \"
		test_string = 'a\\"bc\\"def" // asdasdas'
		expected = ['a\\"bc\\"def']
		result = extract_values(test_string, False)
		self.assertEqual(expected, result)

		# End at first "
		test_string = 'a"bc\\"def" // asdasdas'
		expected = ['a']
		result = extract_values(test_string, False)
		self.assertEqual(expected, result)

		# If " not found, return nothing
		test_string = 'a\\"bc\\"def\\" // asdasdas'
		expected = []
		result = extract_values(test_string, False)
		self.assertEqual(expected, result)

		test_string = 'abcdef // asdasdas'
		expected = []
		result = extract_values(test_string, False)
		self.assertEqual(expected, result)

	def test_extract_values_find_start(self):
		# Ignore escaped quotes \"
		test_string = '"a\\"bc\\"def" // asdasdas'
		expected = ['a\\"bc\\"def']
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Multiple values, escaped quotes not ignored when finding next start of string
		test_string = 'test. "a"bc\\"def" // asdasdas'
		expected = ['a', 'def']
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Ignore if nothing found or all scaped
		test_string = 'a\\"bc\\"def\\" // asdasdas'
		expected = []
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		test_string = 'abcdef // asdasdas'
		expected = []
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Multiple mixed values
		test_string = '[]string{"a\\"bc\\"def", `value2`, "3"} // asdasdas'
		expected = ['a\\"bc\\"def', "value2", "3"]
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Multiple mixed empty values
		test_string = '[]string{"", ``, "a"'
		expected = ['a']
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Double quotes between backticks
		test_string = '`"`'
		expected = ['"']
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

		# Backtick between double quotes
		test_string = '"`"'
		expected = ['`']
		result = extract_values(test_string, True)
		self.assertEqual(expected, result)

if __name__ == '__main__':
	unittest.main()
