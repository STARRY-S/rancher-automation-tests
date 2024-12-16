package commands

import (
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

func Execute(args []string) {
	checkerCmd := newCheckerCmd()
	checkerCmd.addCommands()
	checkerCmd.cmd.SetArgs(args)

	_, err := checkerCmd.cmd.ExecuteC()
	if err != nil {
		if signalContext.Err() != nil {
			logrus.Fatal(signalContext.Err())
		}
		logrus.Fatal(err)
	}
}

type checkerCmd struct {
	*baseCmd
}

func newCheckerCmd() *checkerCmd {
	cc := &checkerCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "checker",
		Short: "Rancher KEv2 Provisioning test resource checker tools",
		Run: func(cmd *cobra.Command, args []string) {
			cmd.Help()
		},
	})
	cc.cmd.Version = utils.Version
	cc.cmd.SilenceUsage = true
	cc.cmd.SilenceErrors = true

	flags := cc.cmd.PersistentFlags()
	flags.BoolVarP(&cc.baseCmd.debug, "debug", "", false, "enable debug output")

	return cc
}

func (cc *checkerCmd) getCommand() *cobra.Command {
	return cc.cmd
}

func (cc *checkerCmd) addCommands() {
	addCommands(
		cc.cmd,
		newAwsCmd(),
		newAwscnCmd(),
		newHwcloudCmd(),
		newVersionCmd(),
	)
}
