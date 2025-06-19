package commands

import (
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider"
	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/provider/tencent"
	"github.com/spf13/cobra"
)

const (
	ENV_TENCENT_ACCESS_KEY_ID     = "TENCENT_ACCESS_KEY_ID"
	ENV_TENCENT_ACCESS_KEY_SECRET = "TENCENT_ACCESS_KEY_SECRET"
	ENV_TENCENT_REGION            = "TENCENT_REGION"
)

type tencentCloudCmd struct {
	*baseCmd

	checkCVM   bool
	checkCBS   bool
	checkEIP   bool
	checkEKSCI bool

	clean    bool
	filters  []string
	excludes []string
	output   string
	autoYes  bool
	ak       string
	sk       string
	region   string
}

func newTencentCloudCmd() *tencentCloudCmd {
	cc := &tencentCloudCmd{}
	cc.baseCmd = newBaseCmd(&cobra.Command{
		Use:   "tencent",
		Short: "Check Tencent Cloud resources",
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
	flags.StringArrayVarP(&cc.excludes, "exclude", "e", nil, "whitelist to exclude instance name (Ex. DoNotDelete)")
	flags.StringVarP(&cc.output, "output", "o", "remain-resources.txt", "output file if have remaning resources")
	flags.BoolVarP(&cc.checkCVM, "check-cvm", "", true, "check CVM instances")
	flags.BoolVarP(&cc.checkEIP, "check-eip", "", true, "check EIP resources")
	flags.BoolVarP(&cc.checkEKSCI, "check-eksci", "", true, "check EKSCI instances")
	flags.BoolVarP(&cc.checkCBS, "check-cbs", "", true, "check CBS disk")
	flags.BoolVarP(&cc.autoYes, "auto-yes", "y", false, "auto yes")
	flags.StringVarP(&cc.ak, "ak", "", "", "tencent cloud access key ID (env '"+ENV_TENCENT_ACCESS_KEY_ID+"')")
	flags.StringVarP(&cc.sk, "sk", "", "", "tencent cloud secret key (env '"+ENV_TENCENT_ACCESS_KEY_SECRET+"')")
	flags.StringVarP(&cc.region, "region", "r", "", "tencent cloud region (env '"+ENV_TENCENT_REGION+"')")

	return cc
}

func (cc *tencentCloudCmd) prepareProviders() (provider.Providers, error) {
	checkEnv(&cc.ak, ENV_TENCENT_ACCESS_KEY_ID, true)
	checkEnv(&cc.sk, ENV_TENCENT_ACCESS_KEY_SECRET, true)
	checkEnv(&cc.region, ENV_TENCENT_REGION, true)

	p, err := tencent.NewProvider(&tencent.Options{
		Filters:  cc.filters,
		Excludes: cc.excludes,
		Clean:    cc.clean,

		CheckCVM:   cc.checkCVM,
		CheckTKE:   false,
		CheckCBS:   cc.checkCBS,
		CheckEIP:   cc.checkEIP,
		CheckEKSCI: cc.checkEKSCI,

		AccessKey: cc.ak,
		SecretKey: cc.sk,
		Region:    cc.region,
	})
	if err != nil {
		return nil, err
	}
	return []provider.Provider{p}, nil
}

func (cc *tencentCloudCmd) getCommand() *cobra.Command {
	return cc.cmd
}
