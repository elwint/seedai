import subprocess
import ast
from args import printd

def run_parser(parser: str, func_name: str) -> str:
	result = subprocess.run([parser, func_name],
						 text=True,  # Output will be treated as string.
						 capture_output=True)  # Capture stdout and stderr.

	# Check the return code of the binary.
	if result.returncode != 0:
		# If the exit code is non-zero, raise an exception with stdout and stderr.
		raise Exception(f"Parser error: {result.stderr}")

	source_code = result.stdout.strip()
	if source_code == "":
		raise Exception("Parser returned empty result")

	return source_code # Return the captured output

# Processor for fine-tuned models
class FineTuneProcessor:
	def __init__(self, tokenizer, seq2seq: bool, split: str, max_encode_length: int):
		self.tokenizer = tokenizer
		self.seq2seq = seq2seq
		self.split_tokens = tokenizer.encode(split, add_special_tokens=False)
		self.max_encode_length = max_encode_length

	def encode(self, source_code: str):
		suffix_tokens = self.split_tokens
		if self.seq2seq:
			suffix_tokens = [] # Do not add split tokens for seq2seq models

		input_ids = encode(
			self.tokenizer, self.seq2seq, self.max_encode_length, source_code,
			suffix_tokens=suffix_tokens,
		)

		return input_ids, [] # Leave system empty

	def stop_token(self):
		return self.tokenizer.eos_token
		# return '\n' # For testing

	def extract(self, output: str) -> list[str]:
		if len(output) > 0:
			return [output]

		return []

# Processor for prompt-tuning
class PromptTuneProcessor:
	def __init__(
			self, tokenizer, seq2seq: bool, max_encode_length: int, count: int,
			prefix: str, suffix: str, stop: str, find_start: bool,
		):
		self.tokenizer = tokenizer
		self.seq2seq = seq2seq
		self.max_encode_length = max_encode_length
		self.find_start = find_start

		prefix = prefix.replace("<count>", str(count))
		suffix = suffix.replace("<count>", str(count))

		self.prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
		self.suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

		if stop == "<eos>":
			stop = tokenizer.eos_token
		self.stop = stop

	def encode(self, source_code: str):
		input_ids = encode(
			self.tokenizer, self.seq2seq, self.max_encode_length, source_code,
			prefix_tokens=self.prefix_tokens,
			suffix_tokens=self.suffix_tokens,
		)

		return input_ids, self.prefix_tokens

	def stop_token(self):
		return self.stop

	def extract(self, output: str) -> list[str]:
		if len(output) == 0:
			return []

		seeds = []
		for line in output.splitlines():
			values = extract_values(line, self.find_start)
			if len(values) == 0:
				continue

			for seed in values:
				# The output contains a string in source code, try to un-escape it
				seed = parse_escaped(seed)

				if len(seed) > 0:
					seeds.append(seed)

		if len(seeds) == 0: # Make sure to always return something when extraction failed
			output = parse_escaped(output)
			return [output]

		return seeds

def encode(tokenizer, seq2seq: bool, max_encode_length: int, text: str, prefix_tokens = [], suffix_tokens = []):
	max_length = max_encode_length - len(prefix_tokens) - len(suffix_tokens)
	if seq2seq:
		max_length -= 2
	if max_length <= 0:
		raise Exception("Encode length too small")

	encoded = tokenizer.encode(text, truncation=True, max_length=max_length, add_special_tokens=False)
	encoded = prefix_tokens + encoded + suffix_tokens
	if seq2seq:
		encoded = [tokenizer.bos_token_id] + encoded + [tokenizer.eos_token_id]

	if len(encoded) > max_encode_length:
		raise Exception("Encoded length too large")

	if len(encoded) == max_encode_length:
		print("	Warning: input length >= max encode length, prompt truncated")

	printd("--------------INPUT---------------") # For debugging
	printd(tokenizer.decode(encoded))
	printd("----------------------------------")

	return encoded

def extract_values(line: str, find_start: bool) -> list[str]:
	values = []

	value, i = extract_value(line, find_start)
	if value != "":
		values.append(value)

	if not find_start or i == -1:
		return values

	# Handle one-line cases like []string{"value1", "value2"}
	while True:
		line = line[i+1:]
		value, i = extract_value(line, find_start)
		if value != "":
			values.append(value)
		if i == -1:
			break

	return values

def extract_value(line: str, find_start: bool) -> str:
	stringType = '"'
	start = 0
	if find_start:
		start = line.find('"')
		startBT = line.find('`')
		if start == -1 or (startBT != -1 and startBT < start):
			start = startBT
			stringType = '`'
		if start == -1:
			return "", -1
		start += 1

	# iterate from the start to the end
	for i in range(start, len(line)):
		if line[i] == stringType and (i == 0 or line[i-1] != '\\'):
			return line[start:i], i

	return "", -1

def parse_escaped(value):
	str_val = '"'+value+'"'
	try:
		return ast.literal_eval(str_val)
	except SyntaxError: # Just return the original value on failure
		return value
