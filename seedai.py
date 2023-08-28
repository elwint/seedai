#!/bin/python3
import os
import hashlib

from args import parse_args
from data_processor import run_parser
from generator import OpenAIGenerator, HFGenerator
import init

generate_args = {
	'temperature': 0.2,
	'diversity_penalty': 2.0,
	'repetition_penalty': 2.0,
}

def main():
	args = parse_args()
	generate_args['count'] = args.count

	# Create corpus dir if not exists
	os.makedirs(args.corpus, exist_ok=True)

	print("Loading tokenizer ...")
	tokenizer, isOpenAI = init.tokenizer(args)

	if isOpenAI and 'OPENAI_API_KEY' not in os.environ:
		raise Exception("Please set OPENAI_API_KEY env variable")

	print("Loading model ...")
	model = init.model(args, isOpenAI)

	processor = init.processor(args, tokenizer, isOpenAI)

	print("	Model max length:", tokenizer.model_max_length)
	print("	Max encode length:", processor.max_encode_length)

	print("Parsing code ...")

	source_code = run_parser(args.parser, args.func)
	inputs = processor.encode(source_code)

	print("Generating ...")

	if isOpenAI:
		generator = OpenAIGenerator(model, tokenizer, args.legacy, **generate_args)
	else:
		generator = HFGenerator(model, tokenizer, **generate_args)

	total = 0
	new_seeds = 0
	for output in generator.generate(inputs):
		seeds = processor.extract(output)
		new_seeds += save_seeds(args.corpus, seeds)

		total += len(seeds)
		print(f"Generated {total} initial seed files.")
		print(f"Total new unique seeds saved: {new_seeds}")

def save_seeds(corpus_dir: str, seeds: list[str]) -> int:
	"""
	Save each output as a file in the given directory after converting it to bytes.
	The filename is the SHA1 hash of its content.
	If a file already exists, it skips the seed.
	Raises an exception if there's an error.
	"""

	new_seeds = 0

	for seed in seeds:
		# Convert string to bytes
		seed_bytes = seed.encode('utf-8')

		# Calculate SHA1 hash of the bytes
		sha1_hash = hashlib.sha1(seed_bytes).hexdigest()

		# Construct the full path to save the file
		file_path = os.path.join(corpus_dir, sha1_hash)

		if os.path.exists(file_path):
			continue

		try:
			# Write bytes to the file
			with open(file_path, 'wb') as file:
				file.write(seed_bytes)
			new_seeds += 1
		except Exception as e:
			raise Exception(f"Error while writing to file {file_path}: {str(e)}")

	return new_seeds


if __name__ == "__main__":
	main()
