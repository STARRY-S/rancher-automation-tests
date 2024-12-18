package main

import (
	"os"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/commands"
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
)

func main() {
	utils.SetupLogrus()
	commands.Execute(os.Args[1:])
}
