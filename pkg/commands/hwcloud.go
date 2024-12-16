package commands

import "github.com/spf13/cobra"

type hwcloudCmd struct {
	*baseCmd
}

func newHwcloudCmd() *hwcloudCmd {
	cc := &hwcloudCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "hwcloud",
		Short: "Check Huawei Cloud resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			return nil
		},
	})

	return cc
}

func (cc *hwcloudCmd) getCommand() *cobra.Command {
	return cc.cmd
}
