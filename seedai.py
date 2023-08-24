#!/bin/python3
from args import parse_args, TYPE_SEQ2SEQ, TYPE_CAUSAL
import data_processor as dp
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

	processor = initialize_processor(args)

	print("Model max length:", processor.tokenizer.model_max_length)
	print("Max encode length:", processor.max_encode_length)

	source_code = dp.run_parser(args.parser, args.func)
	tok_input = processor.encode(source_code)

	# Uncomment below to print out the tokenized input.
	# print(processor.tokenizer.decode(tok_input))

if __name__ == "__main__":
	main()
