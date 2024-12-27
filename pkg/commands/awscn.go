package commands

import "github.com/spf13/cobra"

const (
	ENV_AWSCN_AK     = "AWSCN_AK"
	ENV_AWSCN_SK     = "AWSCN_SK"
	ENV_AWSCN_REGION = "AWSCN_REGION"
)

type awscnCmd struct {
	*baseCmd

	clean  bool
	filter string
	ak     string
	sk     string
	region string
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

	flags := cc.baseCmd.cmd.Flags()
	flags.BoolVarP(&cc.clean, "clean", "c", false, "cleanup remaning resources")
	flags.StringVarP(&cc.filter, "filter", "f", "", "filter string for mating instance name (Ex. auto-rancher-automation-)")
	flags.StringVarP(&cc.ak, "ak", "", "", "aws cloud access key (env '"+ENV_AWSCN_AK+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "aws cloud secret key (env '"+ENV_AWSCN_SK+"')")
	flags.StringVarP(&cc.sk, "region", "r", "", "aws cloud region (env '"+ENV_AWSCN_REGION+"')")

	return cc
}

func (cc *awscnCmd) getCommand() *cobra.Command {
	return cc.cmd
}
