# SeedAI

Generate initial seed files using Large Language Models (LLMs). Compatible with many state-of-the-art fuzzers such as AFL++ and libFuzzer. The core functionality involves processing the source code of a fuzzing test, including the underlying functions it calls, to generate initial seed files.

<p align="center"><img src="https://github.com/elwint/seedai/assets/14903150/d905d2cd-9f67-4672-aba4-9f6498113f1f" width="80%"><br>Implementation overview</p>

## Supported Models

- [OpenAI models (GPT-3.5 Turbo, GPT-4, etc)](https://platform.openai.com/docs/models)
- [CodeGen models](https://huggingface.co/Salesforce/codegen-16B-multi)
- [StarCoder(Base/Plus)](https://huggingface.co/bigcode/starcoder)
- [CodeT5+ models](https://github.com/salesforce/CodeT5)
- [CodeGen2.5 models](https://github.com/salesforce/CodeGen/tree/main/codegen25)
- Other causal/seq2seq models supported by the [Transformers library](https://huggingface.co/docs/transformers) *might* work

## Quick Start (Go):

Below are examples of commands to generate initial seed files for fuzzing in Go. For a full list of options, use the --help flag.

```
make goparser
cd <source_folder>
```

### HuggingFace example

`../seedai.py -p ../bin/goparser -c ../configs/temp_0.6.json -pt ../pt_configs/go/code_only/code.json -m Salesforce/codegen-16B-multi`

Add `--device-map=cpu` to run on CPU.

Note that the number of simultaneous model executions is equal to `max(n, num_beams)`.

### OpenAI example

`OPENAI_API_KEY=<key> ../seedai.py -p ../bin/goparser -c ../configs/top_p_0.75.json -pt ../pt_configs/go/code_multi.json -m gpt-4 -l 8192`

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

## Known Limitations

- [Go source code parser](https://github.com/elwint/scparser)
