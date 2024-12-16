package commands

import "github.com/spf13/cobra"

type awsCmd struct {
	*baseCmd
}

func newAwsCmd() *awsCmd {
	cc := &awsCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "aws",
		Short: "Check AWS (Global) resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			return nil
		},
	})

	return cc
}

func (cc *awsCmd) getCommand() *cobra.Command {
	return cc.cmd
}
