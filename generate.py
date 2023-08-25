import torch

def generate(model, input_ids, count):
	for output in model.generate(
		input_ids=torch.as_tensor([input_ids]),
		temperature=0.2,
		min_new_tokens=0,
		max_new_tokens=50, # TODO Max decode length?
		early_stopping=True,
		num_return_sequences=count,
		num_beams=count,
		num_beam_groups=count,
		diversity_penalty=2.0,
		repetition_penalty=2.0,
		pad_token_id=model.tokenizer.eos_token_id
	):
		yield output
