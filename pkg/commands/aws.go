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

	checkEKS  bool
	checckEC2 bool

	clean   bool
	filters []string
	output  string
	autoYes bool
	ak      string
	sk      string
	token   string
	region  string
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
			if err := run(ps); err != nil {
				return err
			}
			if err := saveReport(ps, cc.output, cc.autoYes); err != nil {
				return err
			}

			return nil
		},
	})
	flags := cc.baseCmd.cmd.Flags()
	flags.BoolVarP(&cc.clean, "clean", "c", false, "cleanup remaning resources")
	flags.StringArrayVarP(&cc.filters, "filter", "f", nil, "filters for mating instance name (Ex. auto-rancher-)")
	flags.StringVarP(&cc.output, "output", "o", "remain-resources.txt", "output file if have remaning resources")
	flags.BoolVarP(&cc.checckEC2, "check-ec2", "", true, "check EC2 instances")
	flags.BoolVarP(&cc.checkEKS, "check-eks", "", true, "check EKS clusters") // Disable EKS by default
	flags.BoolVarP(&cc.autoYes, "auto-yes", "y", false, "auto yes")
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
		Filters: cc.filters,
		Clean:   cc.clean,

		CheckEC2: cc.checckEC2,
		CheckEKS: cc.checkEKS,

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
