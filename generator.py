import requests
import json
import os
import openai
import torch
from transformers import StoppingCriteria, StoppingCriteriaList

class OpenAIGenerator:
	def __init__(self, model, tokenizer, stop_token, legacy, **kwargs):
		openai.api_key = os.environ.get('OPENAI_API_KEY')
		self.model = model
		self.tokenizer = tokenizer
		self.legacy = legacy
		self.stop_token = stop_token
		self.__dict__.update(kwargs)

	def generate(self, inputs):
		args = {
			"model": self.model,
			"temperature": self.temperature,
			"top_p": self.top_p,
			"stop": self.stop_token,
			"n": self.count,
			"frequency_penalty": self.repetition_penalty,
			"presence_penalty": self.presence_penalty,
		}

		if self.legacy:
			input_ids = combine_inputs(inputs)
			args["prompt"] = self.tokenizer.decode(input_ids) # Decoding the input IDs using the tokenizer
			args["max_tokens"] = self.max_new_tokens # Default is not infinity for legacy
		else:
			args["messages"] = [{
				"role": "user",
				"content": self.tokenizer.decode(inputs['user'])
			}]
			if 'system' in inputs:
				messages.insert(0, {
					"role": "system",
					"content": self.tokenizer.decode(inputs['system'])
				})

		if self.legacy:
			completion = openai.Completion.create(**args)
		else:
			completion = openai.ChatCompletion.create(**args)

		for choice in completion.choices:
			if self.legacy:
				yield choice.text
			else:
				yield choice.message.content

class HFGenerator:
	def __init__(self, model, tokenizer, stop_token, seq2seq, **kwargs):
		self.model = model
		self.tokenizer = tokenizer
		self.seq2seq = seq2seq
		stop_token_id = tokenizer.encode(stop_token, add_special_tokens=False)
		if len(stop_token_id) != 1:
			raise Exception("too many tokens for stop_token_id")
			
		self.stop_token_id = stop_token_id[0]
		self.__dict__.update(kwargs)

	def generate(self, inputs):
		input_ids = combine_inputs(inputs)
		stopping_criteria = StoppingCriteriaList([
			StopTokenCriteria(self.stop_token_id),
		])

		for output in self.model.generate(
			input_ids=torch.as_tensor([input_ids]),
			temperature=self.temperature,
			top_p=self.top_p,
			min_new_tokens=0,
			max_new_tokens=self.max_new_tokens,
			do_sample=self.do_sample,
			num_return_sequences=self.count,
			num_beams=self.num_beams,
			num_beam_groups=self.num_beams_groups,
			diversity_penalty=self.diversity_penalty,
			repetition_penalty=self.repetition_penalty,
			pad_token_id=self.tokenizer.eos_token_id,
			stopping_criteria=stopping_criteria,
			eos_token_id=self.stop_token_id,
		):
			if not self.seq2seq:
				output = output[len(input_ids):] # Trim input from output
			output = output[output != self.stop_token_id] # Remove stop token
			yield self.tokenizer.decode(output, skip_special_tokens=True)

def combine_inputs(inputs):
	input_ids = inputs['user']
	if 'system' in inputs:
		input_ids += inputs['system']

	return input_ids

class StopTokenCriteria(StoppingCriteria):
	def __init__(self, stop_token_id):
		self.stop_token_id = stop_token_id
		self.reached_stop_token = []

	def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
		stop = False
		for k, tokens in enumerate(input_ids):
			if k not in self.reached_stop_token and tokens[-1] == self.stop_token_id:
				self.reached_stop_token.append(k)
				stop = True

		if stop:
			print('S', end='', flush=True) # Reached stop token
			if len(self.reached_stop_token) == len(input_ids):
				return True # This might be unnecessary as it is already handled by model.generate
		else:
			print('.', end='', flush=True)

		return False
