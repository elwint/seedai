#!/bin/python3
from args import parse_args, TYPE_SEQ2SEQ, TYPE_CAUSAL
import data_processor as dp

import os
import hashlib

from transformers import AutoTokenizer

def initialize_processor(args):
	tokenizer = AutoTokenizer.from_pretrained(args.model)

	if args.length > 0:
		tokenizer.model_max_length = args.length
	if tokenizer.model_max_length > 1e29:
		tokenizer.model_max_length = int(input("No default max model length. Enter max length: "))

	max_encode_length = tokenizer.model_max_length

	if args.type == TYPE_CAUSAL:
		max_encode_length = int(tokenizer.model_max_length*.75) # reserve 1/4 of model max length for generation
	if args.type == TYPE_SEQ2SEQ:
		args.split_token = "" # no split token for seq2seq models

	if args.prompt_tuning:
		processor = dp.PromptTuneProcessor(tokenizer, max_encode_length)
	else:
		processor = dp.FineTuneProcessor(tokenizer, args.split_token, max_encode_length)

	return processor

def main():
	args = parse_args()

	# Create corpus dir if not exists
	os.makedirs(args.corpus, exist_ok=True)

	print("Loading model ...")

	processor = initialize_processor(args)

	print("	Model max length:", processor.tokenizer.model_max_length)
	print("	Max encode length:", processor.max_encode_length)

	print("Parsing code ...")

	source_code = dp.run_parser(args.parser, args.func)
	tok_input = processor.encode(source_code)

	print("Generating ...")

	total = 0
	for tok_output in generate(tok_input):
		outputs = processor.decode(tok_outputs)
		save_seeds(outputs)

		total += len(outputs)
		print("Generated ", total, " initial seed files.")

		if len(outputs) <= args.count:
			break

def save_seeds(corpus_dir: str, outputs: list[str]):
	"""
	Save each output as a file in the given directory after converting it to bytes.
	The filename is the SHA1 hash of its content.
	Raises an exception if there's an error.
	"""
	for output in outputs:
		# Convert string to bytes
		output_bytes = output.encode('utf-8')

		# Calculate SHA1 hash of the bytes
		sha1_hash = hashlib.sha1(output_bytes).hexdigest()

		# Construct the full path to save the file
		file_path = os.path.join(corpus_dir, sha1_hash)

		try:
			# Write bytes to the file
			with open(file_path, 'wb') as file:
				file.write(output_bytes)
		except Exception as e:
			raise Exception(f"Error while writing to file {file_path}: {str(e)}")

if __name__ == "__main__":
	main()
