import argparse
import json

debug=False

TYPE_SEQ2SEQ = "seq2seq"
TYPE_CAUSAL  = "causal"

def parse_args():
	default_parser = "goparser"
	default_model = "./ft-models/starcoder"
	default_type = TYPE_CAUSAL
	default_prompt_tuning = "no prompt tuning"
	default_pt_count = 10
	default_legacy = False
	default_n = 10
	default_func = "Fuzz"
	default_corpus = "corpus"
	default_split = "\n\n###\n\n"
	default_debug = False
	default_device_map = "auto"

	parser = argparse.ArgumentParser()

	parser.add_argument("--config", "-c", required=True,
					 help="generate config json file.")

	parser.add_argument("--parser", "-p", default=default_parser,
					 help=f"source code parser binary. Default is '{default_parser}'.")

	parser.add_argument("--model", "-m", default=default_model,
					 help=f"name of the LLM model to be used for seed generation. Default is '{default_model}'.")

	parser.add_argument("--type", "-t", default=default_type,
					 help=f"model type '{TYPE_CAUSAL}' or '{TYPE_SEQ2SEQ}'. Default is '{default_type}'.")

	parser.add_argument("--length", "-l", type=int, default=-1,
					 help="model max length. Default is tokenizer.model_max_length.")

	parser.add_argument("--gen-length", "-g", type=int, default=-1,
					 help="max seed generation length. Default is model max length - encode length.")

	parser.add_argument("--prompt-tuning", "-pt", default=default_prompt_tuning,
					 help=f"enable prompt tuning config json file. Default is {default_prompt_tuning}.")

	parser.add_argument("--pt-count", "-C", default=default_pt_count,
					 help=f"replacement for <count> in multiline prompt-tuning. Default is {default_pt_count}.")

	parser.add_argument("--legacy", "-L", action="store_true", default=default_legacy,
					 help=f"enable legacy support (OpenAI). Default is {default_legacy}.")

	parser.add_argument("-n", type=int, default=default_n,
					 help=f"number of model return sequences. Default is {default_n}.")

	parser.add_argument("--func", "-f", default=default_func,
					 help=f"name of the Fuzz function. Default is '{default_func}'.")

	parser.add_argument("--corpus",  "-d", default=default_corpus,
					 help=f"corpus directory. Default is '{default_corpus}'.")

	parser.add_argument("--split", "-s", default=default_split,
					 help="split string for causal model inference without prompt tuning. Default is {}.".
						format(json.dumps(default_split)))

	parser.add_argument("--debug", "--verbose", "-v", action="store_true", default=default_debug,
					 help=f"print debug output to debug.out. Default is {default_debug}.")

	parser.add_argument("--device-map", default=default_device_map,
					 help=f"HuggingFace device_map. Default is '{default_device_map}'.")

	args = parser.parse_args()
	if args.type not in [TYPE_CAUSAL, TYPE_SEQ2SEQ]:
		raise Exception("Invalid type")

	with open(args.config) as json_file:
		generate_args = json.load(json_file)

	if args.prompt_tuning != default_prompt_tuning:
		with open(args.prompt_tuning) as json_file:
			args.prompt_tuning = json.load(json_file)
	else:
		args.prompt_tuning = False

	generate_args['n'] = args.n

	if args.debug:
		global debug
		debug = open('debug.out', 'w')

	return args, generate_args

def printd(v: str):
	if debug:
		print(v, file=debug, flush=True)
