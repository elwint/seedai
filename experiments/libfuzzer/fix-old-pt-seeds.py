#!/bin/python3
# This script fixes PT seeds generated before commit 12b245bdb52f5dd5e202a6a1190e9f9764c36144
import ast
import os
import glob

def parse_escaped(value):
	str_val = '"'+value+'"'
	try:
		return ast.literal_eval(str_val)
	except SyntaxError: # Just return the original value on failure
		return value

def process_file_content(file_path: str):
	"""
	Read, process, and overwrite the content of a file if the content starts with a `"` character.
	"""
	with open(file_path, 'r', encoding='utf-8', errors='surrogatepass') as f:
		content = f.read()

	# Check if content starts with a `"` character.
	if not content.startswith('"'):
		return
	
	print("Updating: " + file_path)
	
	data = parse_escaped(content[1:]).encode('utf-8', 'surrogatepass')
	
	with open(file_path, 'wb') as f:
		f.write(data)

def main():
	for file_path in glob.glob('./results/*/*/pt/*/corpus/*'):
		process_file_content(file_path)

if __name__ == '__main__':
	main()
