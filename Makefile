build: goparser

goparser:
	@mkdir bin/ 2> /dev/null || true
	@go build -C ./parsers/go -trimpath -ldflags "-w -s" -o ${PWD}/bin/goparser

.PHONY: test
test:
	@./test.py
