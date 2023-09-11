package main

import (
	"flag"
	"fmt"
	"os"

	"git.ultraware.nl/elwin/scparser"
)

func main() {
	if os.Getenv(`GO111MODULE`) == `off` {
		panic(`go mod required`)
	}

	var funcName string
	var codeOnly bool
	var pkgPath string

	flag.StringVar(&funcName, "func", "", "Name of the function to parse")
	flag.BoolVar(&codeOnly, "code", false, "Return code only")
	flag.StringVar(&pkgPath, "p", ".", "Package path (optional)")

	flag.Parse()

	if funcName == "" {
		fmt.Println("Missing function name")
		fmt.Println("Usage: goparser -func func_name [-code] [-p pkg_path]")
		flag.PrintDefaults()
		os.Exit(1)
	}

	code := scparser.Parse(pkgPath, funcName, false, codeOnly)
	fmt.Println(code)
}
