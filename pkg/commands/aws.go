package commands

import (
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider"
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider/aws"
	"github.com/spf13/cobra"
)

const (
	ENV_AWS_AK     = "AWS_AK"
	ENV_AWS_SK     = "AWS_SK"
	ENV_AWS_REGION = "AWS_REGION"
)

type awsCmd struct {
	*baseCmd

	ak     string
	sk     string
	region string
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
	flags := cc.baseCmd.cmd.Flags()
	flags.StringVarP(&cc.ak, "ak", "", "", "aws cloud access key (env '"+ENV_AWS_AK+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "aws cloud secret key (env '"+ENV_AWS_SK+"')")
	flags.StringVarP(&cc.sk, "region", "r", "", "aws cloud region (env '"+ENV_AWS_REGION+"')")

	return cc
}

func (cc *awsCmd) prepareProviders() (provider.Providers, error) {
	checkEnv(&cc.ak, ENV_AWS_AK)
	checkEnv(&cc.sk, ENV_AWS_SK)
	checkEnv(&cc.region, ENV_AWS_REGION)

	p, err := aws.NewProvider(&aws.Options{})
	if err != nil {
		return nil, err
	}
	return []provider.Provider{p}, nil
}

func (cc *awsCmd) getCommand() *cobra.Command {
	return cc.cmd
}
