import requests
import json
import os

class OpenAIGenerator:
	def __init__(self, model, tokenizer, **kwargs):
		self.model = model
		self.tokenizer = tokenizer
		self.__dict__.update(kwargs)
		self.base_url = "https://api.openai.com/v1/chat/completions"

	def generate(self, input_ids):
		headers = {
			"Authorization": "Bearer "+os.environ.get('OPENAI_API_KEY'),
			"Content-Type": "application/json"
		}

		data = {
			"model": self.model,
			"messages": [{
				"role": "user",
				"content": self.tokenizer.decode(input_ids)  # Decoding the input IDs using the tokenizer
			}],
			"temperature": self.temperature,
			"n": self.count,
			"presence_penalty": self.diversity_penalty,  # map the given parameters to the actual request parameters
			"frequency_penalty": self.repetition_penalty,
		}

		response = requests.post(self.base_url, headers=headers, json=data, stream=True)

		# Check if the response is not successful
		if response.status_code != 200:
			raise Exception(f"API returned an error: {response.text}")

		data = response.json()
		for choice in data.get("choices", []):
			message = choice.get("message", {})
			content = message.get("content")

			if content:
				yield content

class HFGenerator:
	def __init__(self, model, tokenizer, **kwargs):
		self.model = model
		self.tokenizer = tokenizer
		self.__dict__.update(kwargs)

	def generate(self, input_ids):
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
