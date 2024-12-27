package hwcloud

import (
	"context"
	"fmt"
	"strings"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	cce "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/cce/v3"
	ecs "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/ecs/v2"
	eip "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/eip/v2"
	"github.com/sirupsen/logrus"
)

type provider struct {
	filter string
	clean  bool

	clientAuth *ClientAuth
	cceClient  *cce.CceClient
	ecsCliet   *ecs.EcsClient
	eipClient  *eip.EipClient
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

		if p.filter != "" {
			if strings.Index(c.Metadata.Name, p.filter) < 0 {
				// skip filter not match
				continue
			}
		}

		// Check cluster name, AliasName, tag
		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warnf("CCE cluster [%v] status [%v] not cleanup!",
				utils.Value(c.Metadata.Alias), utils.Value(c.Status.Phase))

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

		if p.filter != "" {
			if strings.Index(c.Name, p.filter) < 0 {
				// skip filter not match
				continue
			}
		}

		// Check server name, tag
		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warnf("ECS Server [%v] status [%v] flavor [%v] not cleanup!",
				c.Name, c.Status, c.Flavor)
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

		logrus.WithFields(logrus.Fields{"Provider": "HWCloud"}).
			Warnf("EIP [%v] status [%v] ID [%v] not cleanup!",
				utils.Value(c.BandwidthName), c.Status.Value(), utils.Value(c.Id))
	}
	return nil
}

type Options struct {
	Filter string
	Clean  bool

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
		filter: o.Filter,
		clean:  o.Clean,

		clientAuth: c,
		cceClient:  cceClient,
		ecsCliet:   ecsClient,
		eipClient:  eipClient,
	}, nil
}
