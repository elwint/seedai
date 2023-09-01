# SeedAI

TODO

Known limitations:

- [Go source code parser](https://git.ultraware.nl/elwin/scparser)

## Config example

```json
{
	"do_sample": false,             # Ignored by OpenAI
	"temperature": 1.0,             # Default = 1.0, ignored if do_sample is false
	"top_p": 1.0,                   # Default = 1.0, ignored if do_sample is false
	"diversity_penalty": 2.0,       # Ignore by OpenAI
	"repetition_penalty": 2.0,      # frequency_penalty for OpenAI
	"presence_penalty": 2.0,        # Ignored by HuggingFace, requires group beam search)
	"num_beams": "<count>",         # Ignored by OpenAI, default = 1 (no beam search)
	"num_beams_groups": "<count>"   # Ignored by OpenAI, default = 1 (no group beam search)
}
```
