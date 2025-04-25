package commands

import (
	"os"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/wrapper"
	"github.com/spf13/cobra"
)

type wrapperCmd struct {
	*baseCmd
}

func newWrapperCmd() *wrapperCmd {
	cc := &wrapperCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "wrapper",
		Short: "Safe stdio/stderr wrapper to avoid leaking sensitive information",
		Long: `Safe stdio/stderr wrapper to avoid leaking sensitive information.
Following information is hidden:
- HTTP/HTTPS URL
- KubeConfig

Example:
export WRAPPER_END_EOF="WRAPPER_EOF" # To exit the wrapper process

<COMMAND_TO_EXECUTE> | check wrapper`,
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := cc.run(); err != nil {
				return err
			}
			return nil
		},
	})

	flags := cc.baseCmd.cmd.Flags()
	_ = flags

	return cc
}

func (cc *wrapperCmd) run() error {
	eof := os.Getenv("WRAPPER_END_EOF")
	w := wrapper.NewWrapper(eof)
	w.Run(signalContext)
	return nil
}

func (cc *wrapperCmd) getCommand() *cobra.Command {
	return cc.cmd
}
