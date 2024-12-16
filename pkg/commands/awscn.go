package commands

import "github.com/spf13/cobra"

type awscnCmd struct {
	*baseCmd
}

func newAwscnCmd() *awscnCmd {
	cc := &awscnCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "awscn",
		Short: "Check AWS (China) resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			return nil
		},
	})

	return cc
}

func (cc *awscnCmd) getCommand() *cobra.Command {
	return cc.cmd
}
