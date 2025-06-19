package tencent

import (
	"context"
	"fmt"
	"slices"
	"strings"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/sirupsen/logrus"
	cbsapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cbs/v20170312"
	cvmapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cvm/v20170312"
	tkeapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/tke/v20180525"
	vpcapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/vpc/v20170312"
)

type provider struct {
	filters    []string
	excludes   []string
	clean      bool
	clientAuth *ClientAuth

	needCheckCVM   bool
	needCheckCBS   bool
	needCheckEIP   bool
	needCheckEKSCI bool

	cvmClient *cvmapi.Client
	tkeClient *tkeapi.Client
	cbsClient *cbsapi.Client
	vpcClient *vpcapi.Client

	unclean bool
	reports []string
}

func (p *provider) Name() string {
	return "tencent"
}

func (p *provider) Check(ctx context.Context) error {
	logrus.WithFields(logrus.Fields{"Provider": "Tencent"}).
		Infof("start check tencent cloud resources")
	if err := p.checkCVM(ctx); err != nil {
		return err
	}
	if err := p.checkEIP(ctx); err != nil {
		return err
	}
	if err := p.checkEKSCI(ctx); err != nil {
		return err
	}
	if err := p.checkCBS(ctx); err != nil {
		return err
	}
	return nil
}

func (p *provider) checkCVM(ctx context.Context) error {
	if !p.needCheckCVM {
		logrus.Infof("Skip check %v CVM", p.Name())
		return nil
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := describeInstances(p.cvmClient)
	if err != nil {
		return fmt.Errorf("failed to list CVM: %w", err)
	}
	if len(res.Response.InstanceSet) == 0 {
		return nil
	}
	for _, e := range res.Response.InstanceSet {
		if !utils.MatchFilters(utils.Value(e.InstanceName), p.filters, p.excludes) {
			// skip filter not match
			continue
		}

		// Check cluster name, AliasName, tag
		s := fmt.Sprintf("CVM [%v] not cleanup!",
			utils.PrintNoIndent(e))
		logrus.WithFields(logrus.Fields{"Provider": "Tencent"}).
			Warn(s)
		p.reports = append(p.reports, utils.Value(e.InstanceName))
		p.unclean = true
		if p.clean {
			logrus.Errorf("CVM instance does not support cleanup yet, need to cleanup manually")
			return fmt.Errorf("unsupport to cleanup CVM")
		}
	}

	return nil
}

func (p *provider) checkEIP(ctx context.Context) error {
	if !p.needCheckEIP {
		logrus.Infof("Skip check %v EIP", p.Name())
		return nil
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := describeAddresses(p.vpcClient)
	if err != nil {
		return fmt.Errorf("failed to list EIP: %w", err)
	}
	if len(res.Response.AddressSet) == 0 {
		return nil
	}
	for _, e := range res.Response.AddressSet {
		if !utils.MatchFilters(utils.Value(e.AddressName), p.filters, p.excludes) {
			// skip filter not match
			continue
		}

		// Check cluster name, AliasName, tag
		s := fmt.Sprintf("EIP [%v] not cleanup!",
			utils.PrintNoIndent(e))
		logrus.WithFields(logrus.Fields{"Provider": "Tencent"}).
			Warn(s)
		p.reports = append(p.reports, utils.Value(e.AddressName))
		p.unclean = true
		if p.clean {
			logrus.Errorf("EIP does not support cleanup yet, need to cleanup manually")
			return fmt.Errorf("unsupport to cleanup EIP")
		}
	}
	return nil
}

func (p *provider) checkEKSCI(ctx context.Context) error {
	if !p.needCheckEKSCI {
		logrus.Infof("Skip check %v EKSCI", p.Name())
		return nil
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}

	response, err := describeEKSContainerInstances(p.tkeClient)
	if err != nil {
		return fmt.Errorf("failed to list EKSCI: %w", err)
	}
	if len(response.Response.EksCis) == 0 {
		return nil
	}
	for _, e := range response.Response.EksCis {
		if !utils.MatchFilters(utils.Value(e.EksCiName), p.filters, p.excludes) {
			// skip filter not match
			continue
		}

		// Check cluster name, AliasName, tag
		s := fmt.Sprintf("EKSCI [%v] not cleanup!",
			utils.PrintNoIndent(e))
		logrus.WithFields(logrus.Fields{"Provider": "Tencent"}).
			Warn(s)
		p.reports = append(p.reports, utils.Value(e.EksCiName))
		p.unclean = true
		if p.clean {
			logrus.Errorf("EKSCI does not support cleanup yet, need to cleanup manually")
			return fmt.Errorf("unsupport to cleanup EKSCI")
		}
	}
	return nil
}

func (p *provider) checkCBS(ctx context.Context) error {
	if !p.needCheckCBS {
		logrus.Infof("Skip check %v CBS", p.Name())
		return nil
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := describeDisks(p.cbsClient)
	if err != nil {
		return fmt.Errorf("failed to list CBS disk: %w", err)
	}
	if len(res.Response.DiskSet) == 0 {
		return nil
	}
	for _, d := range res.Response.DiskSet {
		if !utils.MatchFilters(utils.Value(d.DiskName), p.filters, p.excludes) {
			// skip filter not match
			continue
		}

		// Check cluster name, AliasName, tag
		s := fmt.Sprintf("CBS [%v] not cleanup!",
			utils.PrintNoIndent(d))
		logrus.WithFields(logrus.Fields{"Provider": "Tencent"}).
			Warn(s)
		p.reports = append(p.reports, utils.Value(d.DiskName))
		p.unclean = true
		if p.clean {
			logrus.Errorf("CBS does not support cleanup yet, need to cleanup manually")
			return fmt.Errorf("unsupport to cleanup CBS")
		}
	}
	return nil
}

func (p *provider) Report() string {
	return strings.Join(p.reports, "\n")
}

func (p *provider) Unclean() bool {
	return p.unclean
}

type Options struct {
	Filters  []string
	Excludes []string
	Clean    bool

	CheckCVM   bool
	CheckTKE   bool
	CheckCBS   bool
	CheckEIP   bool
	CheckEKSCI bool

	AccessKey string
	SecretKey string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	c, err := newClientAuth(o.AccessKey, o.SecretKey, o.Region)
	if err != nil {
		return nil, fmt.Errorf("failed to init tencent provider: %w", err)
	}

	cvmClient, err := newCVMClient(c.Credential, c.Region, c.ClientProfile)
	if err != nil {
		return nil, fmt.Errorf("cvm client: %w", err)
	}
	tkeClient, err := newTKEClient(c.Credential, c.Region, c.ClientProfile)
	if err != nil {
		return nil, fmt.Errorf("tke client: %w", err)
	}
	cbsClient, err := newCBSClient(c.Credential, c.Region, c.ClientProfile)
	if err != nil {
		return nil, fmt.Errorf("cbs client: %w", err)
	}
	vpcClient, err := newVPCClient(c.Credential, c.Region, c.ClientProfile)
	if err != nil {
		return nil, fmt.Errorf("vpc client: %w", err)
	}

	return &provider{
		filters:  slices.Clone(o.Filters),
		excludes: slices.Clone(o.Excludes),
		clean:    o.Clean,

		needCheckCVM:   o.CheckCVM,
		needCheckCBS:   o.CheckCBS,
		needCheckEIP:   o.CheckEIP,
		needCheckEKSCI: o.CheckEKSCI,

		clientAuth: c,
		cvmClient:  cvmClient,
		tkeClient:  tkeClient,
		cbsClient:  cbsClient,
		vpcClient:  vpcClient,
	}, nil
}
