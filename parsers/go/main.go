package main

import (
	"fmt"
	"os"

	"git.ultraware.nl/elwin/scparser"
)

func main() {
	if os.Getenv(`GO111MODULE`) == `off` {
		panic(`go mod required`)
	}

	if len(os.Args) < 2 || os.Args[1] == `-h` || os.Args[1] == `--help` {
		fmt.Println("Missing function name")
		fmt.Println("Usage: goparser func_name <pkg_path>")
		os.Exit(1)
	}

	funcName := os.Args[1]
	pkgPath := `.`
	if len(os.Args) > 2 {
		pkgPath = os.Args[2]
	}

	code := scparser.Parse(pkgPath, funcName, false)
	fmt.Println(code)
}
