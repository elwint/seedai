import urllib, json
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import tiktoken

from args import TYPE_SEQ2SEQ, TYPE_CAUSAL
from data_processor import PromptTuneProcessor, FineTuneProcessor
from generator import OpenAIGenerator, HFGenerator

def model(args, isOpenAI):
	if isOpenAI:
		return args.model

	config = AutoConfig.from_pretrained(args.model)
	torch_dtype = None
	if config.torch_dtype == torch.float32:
		torch_dtype = torch.bfloat16 # Use half-precision bfloat16 for float32 models (requires CUDA)

	if args.type == TYPE_CAUSAL:
		model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch_dtype) # TODO: device_map="auto" if needed?
	if args.type == TYPE_SEQ2SEQ:
		model = AutoModelForSeq2SeqLM.from_pretrained(args.model, torch_dtype=torch_dtype)

	return model

def tokenizer(args):
	try:
		tokenizer = OpenAITokenizer(args.model)
		isOpenAI = True
	except KeyError:
		tokenizer = AutoTokenizer.from_pretrained(args.model)
		isOpenAI = False

	if args.length > 0:
		tokenizer.model_max_length = args.length
	if (not hasattr(tokenizer, "model_max_length")) or tokenizer.model_max_length > 1e29:
		tokenizer.model_max_length = int(input("No default max model length. Enter max length: "))
		# TODO: Some hard-coded max lengths for known models?

	return tokenizer, isOpenAI

def processor(args, tokenizer):
	if args.type == TYPE_CAUSAL: # TODO: Get this info from model?
		max_encode_length = int(tokenizer.model_max_length*.75) # reserve 1/4 of model max length for generation
	if args.type == TYPE_SEQ2SEQ:
		max_encode_length = tokenizer.model_max_length
		args.split_token = "" # no split token for seq2seq models

	if args.prompt_tuning:
		processor = PromptTuneProcessor(tokenizer, max_encode_length)
	else:
		processor = FineTuneProcessor(tokenizer, args.split_token, max_encode_length)

	return processor

class OpenAITokenizer: # Wrapper class to make OpenAI tokenizer compatible
	def __init__(self, name):
		self.enc = tiktoken.encoding_for_model(name)

	def encode(self, text, truncation=False, max_length=-1):
		if not truncation:
			return self.enc.encode(text)

		return self.enc.encode(text)[:max_length]

	def decode(self, tokens):
		return self.enc.decode(tokens)
