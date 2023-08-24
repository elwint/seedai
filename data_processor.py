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
	def __init__(self, tokenizer, split_token: str, max_encode_length: int):
		self.tokenizer = tokenizer
		self.split_token = tokenizer.encode(split_token)
		self.max_encode_length = max_encode_length

	def encode(self, source_code):
		max_length = self.max_encode_length - len(self.split_token)

		tok_input = self.tokenizer.encode(source_code, truncation=True, max_length=max_length)
		tok_input += self.split_token

		if len(tok_input) == self.max_encode_length:
			print("Warning: input length >= max encode length, prompt truncated")

		return tok_input

	def decode(self, tok_output) -> list[str]:
		output = self.tokenizer.decode(tok_output)
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

	def encode(self, source_code):
		raise Exception("not implemented")

	def decode(self, output) -> list[str]:
		raise Exception("not implemented")
		return []
