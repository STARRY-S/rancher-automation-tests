package hwcloud

import (
	"context"
	"fmt"
	"slices"
	"strings"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	cce "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/cce/v3"
	ecs "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/ecs/v2"
	eip "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/eip/v2"
	"github.com/sirupsen/logrus"
)

type provider struct {
	filters []string
	clean   bool

	clientAuth *ClientAuth
	cceClient  *cce.CceClient
	ecsCliet   *ecs.EcsClient
	eipClient  *eip.EipClient

	unclean bool
	reports []string
}

func (p *provider) Name() string {
	return "hwcloud"
}

func (p *provider) Check(ctx context.Context) error {
	logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
		Infof("start check huawei cloud resources")
	if err := p.checkCCE(ctx); err != nil {
		return err
	}
	if err := p.checkECS(ctx); err != nil {
		return err
	}
	if err := p.checkEIP(ctx); err != nil {
		return err
	}
	return nil
}

func (p *provider) checkCCE(ctx context.Context) error {
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := listClusters(p.cceClient)
	if err != nil {
		return fmt.Errorf("failed to list cluster: %w", err)
	}
	if res == nil || res.Items == nil || len(*res.Items) == 0 {
		return nil
	}
	for _, c := range *res.Items {
		if c.Spec == nil || c.Metadata == nil {
			continue
		}

		if !utils.MatchFilters(c.Metadata.Name, p.filters) {
			// skip filter not match
			continue
		}

		// Check cluster name, AliasName, tag
		s := fmt.Sprintf("CCE cluster [%v] status [%v] not cleanup!",
			utils.Value(c.Metadata.Alias), utils.Value(c.Status.Phase))
		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warn(s)
		p.reports = append(p.reports, s)
		p.unclean = true
		if p.clean {
			if _, err := deleteCluster(p.cceClient, utils.Value(c.Metadata.Uid)); err != nil {
				logrus.Errorf("failed to delete CCE cluster %v: %v", c.Metadata.Name, err)
				return fmt.Errorf("failed to delete hwcloud cce cluster: %w", err)
			}
		}
	}

	return nil
}

func (p *provider) checkECS(ctx context.Context) error {
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := listCloudServers(p.ecsCliet)
	if err != nil {
		return fmt.Errorf("failed to list cluster: %w", err)
	}
	if res == nil || res.Servers == nil || len(*res.Servers) == 0 {
		return nil
	}
	for _, c := range *res.Servers {
		if c.Name == "" || c.Status == "" {
			continue
		}

		if !utils.MatchFilters(c.Name, p.filters) {
			// skip filter not match
			continue
		}
		// Check server name, tag
		s := fmt.Sprintf("ECS Server [%v] status [%v] flavor [%v] not cleanup!",
			c.Name, c.Status, c.Flavor)
		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warn(s)
		p.reports = append(p.reports, s)
		p.unclean = true
		if p.clean {
			if _, err := deleteServer(p.ecsCliet, c.Id); err != nil {
				logrus.Errorf("failed to delete server %v: %v", c.Name, err)
				return fmt.Errorf("failed to delete hwcloud ECS server: %w", err)
			}
		}
	}
	return nil
}

func (p *provider) checkEIP(ctx context.Context) error {
	if ctx.Err() != nil {
		return ctx.Err()
	}

	res, err := listPublicips(p.eipClient)
	if err != nil {
		return fmt.Errorf("failed to list cluster: %w", err)
	}
	if res == nil || res.Publicips == nil || len(*res.Publicips) == 0 {
		return nil
	}
	for _, c := range *res.Publicips {
		if c.BandwidthName == nil || *c.BandwidthName == "" {
			continue
		}
		if c.Id == nil || *c.Id == "" || c.Status == nil {
			continue
		}

		s := fmt.Sprintf("EIP [%v] status [%v] ID [%v] not cleanup!",
			utils.Value(c.BandwidthName), c.Status.Value(), utils.Value(c.Id))
		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warn(s)
		p.reports = append(p.reports, s)
		p.unclean = true
	}
	return nil
}

func (p *provider) Report() string {
	return strings.Join(p.reports, "\n")
}

func (p *provider) Unclean() bool {
	return false
}

type Options struct {
	Filters []string
	Clean   bool

	AccessKey string
	SecretKey string
	ProjectID string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	c, err := newClientAuth(o.AccessKey, o.SecretKey, o.Region, o.ProjectID)
	if err != nil {
		return nil, fmt.Errorf("failed to init hwcloud provider: %w", err)
	}

	cceClient, err := newCCEClient(c)
	if err != nil {
		return nil, fmt.Errorf("failed to init hwcloud cce client: %w", err)
	}
	ecsClient, err := newEcsClient(c)
	if err != nil {
		return nil, fmt.Errorf("failed to init hwcloud ecs client: %w", err)
	}
	eipClient, err := newEipClient(c)
	if err != nil {
		return nil, fmt.Errorf("failed to init hwcloud eip client: %w", err)
	}
	return &provider{
		filters: slices.Clone(o.Filters),
		clean:   o.Clean,

		clientAuth: c,
		cceClient:  cceClient,
		ecsCliet:   ecsClient,
		eipClient:  eipClient,
	}, nil
}
