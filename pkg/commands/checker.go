package commands

import (
	"os"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider"
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
		Short: "Public cloud remain resource check CLI",
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
		newHwcloudCmd(),
		newVersionCmd(),
	)
}

// checkEnv will raise fatal error if both ENV and command options were not provided.
func checkEnv(p *string, key string, required bool) {
	if *p == "" {
		*p, _ = os.LookupEnv(key)
		if *p == "" && required {
			logrus.Fatalf("%v not set", key)
		}
	}
}

// run executes providers.Run()
func run(ps provider.Providers) error {
	if err := ps.Run(signalContext); err != nil {
		return err
	}
	logrus.Infof("Done")
	return nil
}

// saveReport executes providers.SaveReport()
func saveReport(ps provider.Providers, output string, autoYes bool) error {
	return ps.SaveReport(signalContext, output, autoYes)
}
