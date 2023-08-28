import argparse

TYPE_SEQ2SEQ = "seq2seq"
TYPE_CAUSAL  = "causal"

def parse_args():
	default_parser = "goparser"
	default_model = "./ft-models/starcoder"
	default_type = TYPE_CAUSAL
	default_prompt_tuning = False
	default_legacy = False
	default_count = 100
	default_func = "Fuzz"
	default_corpus = "corpus"
	default_split_token = "\n\n###\n\n"
	default_verbose = False

	parser = argparse.ArgumentParser(description="TODO.")

	parser.add_argument("--parser", "-p", default=default_parser,
					 help=f"source code parser binary. Default is '{default_parser}'.")

	parser.add_argument("--model", "-m", default=default_model,
					 help=f"name of the LLM model to be used for seed generation. Default is '{default_model}'.")

	parser.add_argument("--type", "-t", default=default_type,
					 help=f"model type '{TYPE_CAUSAL}' or '{TYPE_SEQ2SEQ}'. Default is '{default_type}'.")

	parser.add_argument("--length", "-l", type=int, default=-1,
					 help="model max length. Default is tokenizer.model_max_length.")

	parser.add_argument("--prompt-tuning", "-pt", action="store_true", default=default_prompt_tuning,
					 help=f"enable prompt tuning. Default is {default_prompt_tuning}.")

	parser.add_argument("--legacy", "-L", action="store_true", default=default_legacy,
					 help=f"enable legacy support (OpenAI). Default is {default_legacy}.")

	parser.add_argument("--count", "-c", type=int, default=default_count,
					 help=f"number of seeds to be generated by the LLM. Default is {default_count}.")

	parser.add_argument("--func", "-f", default=default_func,
					 help=f"name of the Fuzz function. Default is '{default_func}'.")

	parser.add_argument("--corpus",  "-d", default=default_corpus,
					 help=f"corpus directory. Default is '{default_corpus}'.")

	parser.add_argument("--split-token", "-s", default=default_split_token,
					 help="split token for causal model inference without prompt tuning. Default is '{}'.".
						format(default_split_token.replace('\n', '\\n')))

	parser.add_argument("--verbose", "-v", action="store_true", default=default_verbose,
					 help=f"show verbose output. Default is {default_verbose}.")

	args = parser.parse_args()
	if args.type not in [TYPE_CAUSAL, TYPE_SEQ2SEQ]:
		raise Exception("Invalid type")

	return args
