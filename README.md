# SeedAI

TODO

Note that the number of simultaneous model executions is equal to `max(n, num_beams)`.

Known limitations:

- [Go source code parser](https://git.ultraware.nl/elwin/scparser)

## Generation config example

```json
{
	"do_sample": false,             # Ignored by OpenAI
	"temperature": 1.0,             # Default = 1.0, ignored if do_sample is false
	"top_p": 1.0,                   # Default = 1.0, ignored if do_sample is false
	"diversity_penalty": 2.0,       # Ignored by OpenAI, requires group beam search
	"repetition_penalty": 2.0,      # frequency_penalty for OpenAI
	"presence_penalty": 2.0,        # Ignored by HuggingFace
	"num_beams": 10,                # Ignored by OpenAI, default = 1 (no beam search)
	"num_beam_groups": 10           # Ignored by OpenAI, default = 1 (no group beam search)
}
```

## Prompt-tuning config example
```json
{
	"prefix": "You are a code completer.\n",
	"suffix": "\n```\nfunc Test<count>Bugs() {\n\tinputs := []string{",
	"stop": "}",                    # Optional stop token (next to EOS token)
	"multi_vals": true,             # Extract multiple values per line
	"code_only": false              # Set to true for code-only models
}
```
