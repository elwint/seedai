import subprocess
import ast
from args import printd

def run_parser(parser: str, func_name: str, code_only: bool) -> str:
	parser_args = [parser, "-func", func_name]
	if code_only:
		parser_args.append("-code")
	result = subprocess.run(parser_args,
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
	def __init__(self, tokenizer, seq2seq, split: str, max_encode_length: int):
		self.tokenizer = tokenizer
		self.seq2seq = seq2seq
		self.split_tokens = tokenizer.encode(split, add_special_tokens=False)
		self.max_encode_length = max_encode_length
		if seq2seq == "t5" or seq2seq == "t5-ft":
			self.max_encode_length -= 2

	def encode(self, source_code: str):
		suffix_tokens = self.split_tokens
		if self.seq2seq:
			suffix_tokens = [] # Do not add split tokens for seq2seq models

		input_ids = encode(
			self.tokenizer, self.max_encode_length, source_code,
			suffix_tokens=suffix_tokens,
		)

		if self.seq2seq == "t5" or self.seq2seq == "t5-ft":
			input_ids = [self.tokenizer.bos_token_id] + input_ids + [self.tokenizer.eos_token_id]

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
			self, tokenizer, seq2seq, max_encode_length: int, count: int,
			prefix: str, suffix: str, multi_vals: bool, code_only: bool, stop: str = ""
		):
		self.tokenizer = tokenizer
		self.seq2seq = seq2seq
		self.max_encode_length = max_encode_length
		if seq2seq == "t5" or seq2seq == "t5-ft":
			self.max_encode_length -= 3
		self.multi_vals = multi_vals

		prefix = prefix.replace("<count>", str(count))
		suffix = suffix.replace("<count>", str(count))

		self.prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
		self.suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

		if stop == "":
			stop = tokenizer.eos_token
		self.stop = stop

		self.start_with_string = False
		if len(suffix) > 0 and (suffix[-1] == '"' or suffix[-1] == "`"):
			self.start_with_string = suffix[-1]

		self.check_suffix_tokens = []
		if not code_only:
			self.check_suffix_tokens = tokenizer.encode("\n```", add_special_tokens=False)

	def encode(self, source_code: str):
		input_ids = encode(
			self.tokenizer, self.max_encode_length, source_code,
			prefix_tokens=self.prefix_tokens,
			suffix_tokens=self.suffix_tokens,
			check_suffix_tokens=self.check_suffix_tokens,
		)

		if self.seq2seq == "t5" or self.seq2seq == "t5-ft":
			input_ids = [self.tokenizer.bos_token_id] + input_ids + [self.tokenizer.extra_token_id, self.tokenizer.eos_token_id]

		return input_ids, self.prefix_tokens

	def stop_token(self):
		return self.stop

	def extract(self, output: str) -> list[str]:
		if len(output) == 0:
			return []

		if self.start_with_string and output[0] != self.start_with_string:
			output = self.start_with_string + output

		seeds = []
		for line in output.splitlines():
			values = extract_values(line, self.multi_vals)
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

def encode(tokenizer, max_encode_length: int, text: str, prefix_tokens = [], suffix_tokens = [], check_suffix_tokens = []):
	max_length = max_encode_length - len(prefix_tokens) - len(suffix_tokens) - len(check_suffix_tokens)
	if max_length <= 0:
		raise Exception("Encode length too small")

	encoded = tokenizer.encode(text, truncation=True, max_length=max_length, add_special_tokens=False)
	if len(encoded) >= max_length:
		print("	Warning: input length >= max encode length, prompt truncated")

		if len(check_suffix_tokens) > 0 and encoded[-len(check_suffix_tokens):] != check_suffix_tokens:
			suffix_tokens = check_suffix_tokens + suffix_tokens

	encoded = prefix_tokens + encoded + suffix_tokens

	if len(encoded) > max_encode_length:
		raise Exception("Encoded length too large")

	return encoded

def extract_values(line: str, multi_vals: bool) -> list[str]:
	values = []

	value, i = extract_value(line)
	if value != "":
		values.append(value)

	if not multi_vals or i == -1:
		return values

	# Handle one-line cases like []string{"value1", "value2"}
	while True:
		line = line[i+1:]
		value, i = extract_value(line)
		if value != "":
			values.append(value)
		if i == -1:
			break

	return values

def extract_value(line: str) -> str:
	stringType = '"'
	start = 0

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
