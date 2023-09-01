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

def processor(args, tokenizer, isOpenAI):
	if args.type == TYPE_CAUSAL: # TODO: Get this info from model?
		max_encode_length = int(tokenizer.model_max_length*.75) # reserve 1/4 of model max length for generation
		seq2seq = False
	if args.type == TYPE_SEQ2SEQ:
		max_encode_length = tokenizer.model_max_length
		seq2seq = True
	if isOpenAI and not args.legacy:
		max_encode_length -= 11 # OpenAI uses 11 extra tokens for role (system, user) input

	if args.prompt_tuning:
		processor = PromptTuneProcessor(tokenizer, seq2seq, max_encode_length)
	else:
		processor = FineTuneProcessor(tokenizer, seq2seq, args.split, max_encode_length)

	return processor

class OpenAITokenizer: # Wrapper class to make OpenAI tokenizer compatible
	def __init__(self, name: str):
		split = name.split(':', 1)
		self.enc = tiktoken.encoding_for_model(split[0])

		self.eos_token = "<|endoftext|>"
		if len(split) > 1:
			self.eos_token = " END" # Ft-models use " END" as eos_token (assuming OpenAI's default fine-tune format)
		
		eos_token_id = self.enc.encode(self.eos_token, allowed_special="all")
		if len(eos_token_id) != 1:
			raise Exception("too many tokens for eos_token_id")
		self.eos_token_id = eos_token_id[0]

	def encode(self, text, truncation=False, max_length=-1, add_special_tokens=False):
		if not truncation:
			return self.enc.encode(text)

		return self.enc.encode(text)[:max_length]

	def decode(self, tokens):
		return self.enc.decode(tokens)
