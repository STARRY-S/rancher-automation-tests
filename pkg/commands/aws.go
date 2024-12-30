package commands

import (
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider"
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider/aws"
	"github.com/spf13/cobra"
)

const (
	ENV_AWS_AK     = "AWS_AK"
	ENV_AWS_SK     = "AWS_SK"
	ENV_AWS_TK     = "AWS_TK"
	ENV_AWS_REGION = "AWS_REGION"
)

type awsCmd struct {
	*baseCmd

	clean  bool
	filter string
	ak     string
	sk     string
	token  string
	region string
}

func newAwsCmd() *awsCmd {
	cc := &awsCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "aws",
		Short: "Check AWS resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			ps, err := cc.prepareProviders()
			if err != nil {
				return err
			}
			run(ps)

			return nil
		},
	})
	flags := cc.baseCmd.cmd.Flags()
	flags.BoolVarP(&cc.clean, "clean", "c", false, "cleanup remaning resources")
	flags.StringVarP(&cc.filter, "filter", "f", "", "filter string for mating instance name (Ex. auto-rancher-automation-)")
	flags.StringVarP(&cc.ak, "ak", "", "", "aws cloud access key (env '"+ENV_AWS_AK+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "aws cloud secret key (env '"+ENV_AWS_SK+"')")
	flags.StringVarP(&cc.token, "token", "", "", "aws cloud token (optional) (env '"+ENV_AWS_TK+"')")
	flags.StringVarP(&cc.sk, "region", "r", "", "aws cloud region (env '"+ENV_AWS_REGION+"')")

	return cc
}

func (cc *awsCmd) prepareProviders() (provider.Providers, error) {
	checkEnv(&cc.ak, ENV_AWS_AK, true)
	checkEnv(&cc.sk, ENV_AWS_SK, true)
	checkEnv(&cc.token, ENV_AWS_TK, false)
	checkEnv(&cc.region, ENV_AWS_REGION, true)

	p, err := aws.NewProvider(&aws.Options{
		Filter: cc.filter,
		Clean:  cc.clean,

		AccessKey: cc.ak,
		SecretKey: cc.sk,
		Token:     cc.token,
		Region:    cc.region,
	})
	if err != nil {
		return nil, err
	}
	return []provider.Provider{p}, nil
}

func (cc *awsCmd) getCommand() *cobra.Command {
	return cc.cmd
}
