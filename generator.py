import requests
import json
import os
import openai

class OpenAIGenerator:
	def __init__(self, model, tokenizer, legacy, **kwargs):
		openai.api_key = os.environ.get('OPENAI_API_KEY')
		self.model = model
		self.tokenizer = tokenizer
		self.legacy = legacy
		self.__dict__.update(kwargs)

	def generate(self, inputs):
		args = {
			"model": self.model,
			"temperature": self.temperature,
			"stop": " END",
			"n": self.count,
			"presence_penalty": self.diversity_penalty,  # map the given parameters to the actual request parameters
			"frequency_penalty": self.repetition_penalty,
		}

		if self.legacy:
			input_ids = combine_inputs(inputs)
			args["prompt"] = self.tokenizer.decode(input_ids) # Decoding the input IDs using the tokenizer
			args["max_tokens"] = self.tokenizer.model_max_length - len(input_ids)
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
	def __init__(self, model, tokenizer, **kwargs):
		self.model = model
		self.tokenizer = tokenizer
		self.__dict__.update(kwargs)

	def generate(self, inputs):
		input_ids = combine_inputs(inputs)
		max_new_tokens = self.tokenizer.model_max_length - len(input_ids)

		for output in self.model.generate(
			input_ids=torch.as_tensor([input_ids]),
			temperature=self.temperature,
			min_new_tokens=0,
			max_new_tokens=max_new_tokens,
			early_stopping=True,
			num_return_sequences=self.count,
			num_beams=self.count,
			num_beam_groups=self.count,
			diversity_penalty=self.diversity_penalty,
			repetition_penalty=self.repetition_penalty,
			pad_token_id=self.tokenizer.eos_token_id # TODO: Remove matching prefix
		):
			yield self.tokenizer.decode(output)

def combine_inputs(inputs):
	input_ids = inputs['user']
	if 'system' in inputs:
		input_ids += inputs['system']

	return input_ids
