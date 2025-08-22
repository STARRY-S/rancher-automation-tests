package commands

import (
	"context"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider/aws"
	"github.com/spf13/cobra"
)

type awsStartCmd struct {
	*awsCmd

	dryRun      bool
	instanceIDs []string
}

func newAwsStartCmd() *awsStartCmd {
	cc := &awsStartCmd{
		awsCmd: &awsCmd{},
	}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "start",
		Short: "Startup AWS EC2 instance resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			s, err := cc.prepareStarter()
			if err != nil {
				return err
			}
			if err := s.Start(signalContext); err != nil {
				return err
			}

			return nil
		},
	})
	flags := cc.baseCmd.cmd.Flags()
	flags.BoolVarP(&cc.dryRun, "dry-run", "", false, "Dry-Run, do not delete/shutdown instance")
	flags.StringSliceVarP(&cc.instanceIDs, "id", "", nil, "EC2 instance ID, separated by comma")
	// flags.StringArrayVarP(&cc.instanceIDs, "id", "", nil, "EC2 instance ID")
	flags.StringVarP(&cc.ak, "ak", "", "", "aws cloud access key (env '"+ENV_AWS_AK+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "aws cloud secret key (env '"+ENV_AWS_SK+"')")
	flags.StringVarP(&cc.token, "token", "", "", "aws cloud token (optional) (env '"+ENV_AWS_TK+"')")
	flags.StringVarP(&cc.region, "region", "r", "", "aws cloud region (env '"+ENV_AWS_REGION+"')")

	return cc
}

type starter interface {
	Start(context.Context) error
}

func (cc *awsStartCmd) prepareStarter() (starter, error) {
	checkEnv(&cc.ak, ENV_AWS_AK, true)
	checkEnv(&cc.sk, ENV_AWS_SK, true)
	checkEnv(&cc.token, ENV_AWS_TK, false)
	checkEnv(&cc.region, ENV_AWS_REGION, true)

	p, err := aws.NewProvider(&aws.Options{
		DryRun:      cc.dryRun,
		InstanceIDs: cc.instanceIDs,

		AccessKey: cc.ak,
		SecretKey: cc.sk,
		Token:     cc.token,
		Region:    cc.region,
	})
	if err != nil {
		return nil, err
	}
	return p, nil
}

func (cc *awsStartCmd) getCommand() *cobra.Command {
	return cc.cmd
}
