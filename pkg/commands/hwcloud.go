package commands

import (
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider"
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider/hwcloud"
	"github.com/spf13/cobra"
)

const (
	ENV_HUAWEI_ACCESS_KEY = "HUAWEI_ACCESS_KEY"
	ENV_HUAWEI_SECRET_KEY = "HUAWEI_SECRET_KEY"
	ENV_HUAWEI_REGION_ID  = "HUAWEI_REGION_ID"
	ENV_HUAWEI_PROJECT_ID = "HUAWEI_PROJECT_ID"
)

type hwcloudCmd struct {
	*baseCmd

	checkCCE bool
	checkECS bool
	checkEIP bool

	clean     bool
	filters   []string
	output    string
	autoYes   bool
	ak        string
	sk        string
	region    string
	projectID string
}

func newHwcloudCmd() *hwcloudCmd {
	cc := &hwcloudCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "hwcloud",
		Short: "Check Huawei Cloud resources",
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
	flags.BoolVarP(&cc.checkCCE, "check-cce", "", true, "check CCE cluster")
	flags.BoolVarP(&cc.checkECS, "check-ecs", "", true, "check ECS instances")
	flags.BoolVarP(&cc.checkEIP, "check-eip", "", true, "check EIP resources")
	flags.BoolVarP(&cc.autoYes, "auto-yes", "y", false, "auto yes")
	flags.StringVarP(&cc.ak, "ak", "", "", "huawei cloud access key ID (env '"+ENV_HUAWEI_ACCESS_KEY+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "huawei cloud secret key (env '"+ENV_HUAWEI_SECRET_KEY+"')")
	flags.StringVarP(&cc.region, "region", "r", "", "huawei cloud region (env '"+ENV_HUAWEI_REGION_ID+"')")
	flags.StringVarP(&cc.projectID, "project-id", "p", "", "huawei cloud project ID (env '"+ENV_HUAWEI_PROJECT_ID+"')")

	return cc
}

func (cc *hwcloudCmd) prepareProviders() (provider.Providers, error) {
	checkEnv(&cc.ak, ENV_HUAWEI_ACCESS_KEY, true)
	checkEnv(&cc.sk, ENV_HUAWEI_SECRET_KEY, true)
	checkEnv(&cc.region, ENV_HUAWEI_REGION_ID, true)
	checkEnv(&cc.projectID, ENV_HUAWEI_PROJECT_ID, true)

	p, err := hwcloud.NewProvider(&hwcloud.Options{
		Filters: cc.filters,
		Clean:   cc.clean,

		CheckCCE: cc.checkCCE,
		CheckECS: cc.checkECS,
		CheckEIP: cc.checkEIP,

		AccessKey: cc.ak,
		SecretKey: cc.sk,
		ProjectID: cc.projectID,
		Region:    cc.region,
	})
	if err != nil {
		return nil, err
	}
	return []provider.Provider{p}, nil
}

func (cc *hwcloudCmd) getCommand() *cobra.Command {
	return cc.cmd
}
