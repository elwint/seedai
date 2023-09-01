import subprocess

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

		tok_input = encode(
			self.tokenizer, self.seq2seq, self.max_encode_length, source_code,
			suffix_tokens=suffix_tokens,
		)

		return {'user': tok_input}, len(tok_input)

	def stop_token(self):
		return self.tokenizer.eos_token
		# return '\n' # For testing

	def extract(self, output: str) -> list[str]:
		if len(output) > 0:
			return [output]

		return []


# Processor for prompt-tuning (TODO)
class PromptTuneProcessor:
	def __init__(self, tokenizer, prefix: str, suffix: str, max_encode_length: int):
		self.tokenizer = tokenizer
		self.prefix = prefix
		self.suffix = suffix
		self.max_encode_length = max_encode_length

	def encode(self, source_code: str):
		raise Exception("not implemented")

	def stop_token(self):
		raise Exception("not implemented")

	def extract(self, output: str) -> list[str]:
		raise Exception("not implemented")
		return []

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

	# print("----------------------------------") # For debugging
	# print(tokenizer.decode(encoded))
	# print("----------------------------------")

	return encoded
