# SeedAI

TODO

Known limitations:

- [Go source code parser](https://git.ultraware.nl/elwin/scparser)

## Generation config example

```json
{
	"do_sample": false,             # Ignored by OpenAI
	"temperature": 1.0,             # Default = 1.0, ignored if do_sample is false
	"top_p": 1.0,                   # Default = 1.0, ignored if do_sample is false
	"diversity_penalty": 2.0,       # Ignore by OpenAI
	"repetition_penalty": 2.0,      # frequency_penalty for OpenAI
	"presence_penalty": 2.0,        # Ignored by HuggingFace, requires group beam search)
	"num_beams": "<execs>",         # Ignored by OpenAI, default = 1 (no beam search)
	"num_beams_groups": "<execs>"   # Ignored by OpenAI, default = 1 (no group beam search)
}
```

## Prompt-tuning config example
```json
{
	"prefix": "You are a code completer.\n",
	"suffix": "\n```\nfunc Test<count>Bugs() {\n\tinputs := []string{",
	"stop": "}",
	"find_start": true		# Find start of string, may extract multiple values when true
}
```
