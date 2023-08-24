#!/bin/python3
import unittest
import os
import hashlib
import tempfile

from seedai import save_seeds

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

if __name__ == '__main__':
	unittest.main()
