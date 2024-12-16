package main

import (
	"os"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/commands"
)

func main() {
	commands.Execute(os.Args[1:])
}
