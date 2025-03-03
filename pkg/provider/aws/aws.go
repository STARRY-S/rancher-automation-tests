package aws

import (
	"context"
	"fmt"
	"slices"
	"strings"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/aws/aws-sdk-go-v2/service/ec2/types"
	"github.com/aws/aws-sdk-go-v2/service/eks"
	"github.com/sirupsen/logrus"
)

type provider struct {
	filters []string
	clean   bool

	cfg          aws.Config
	ec2Client    *ec2.Client
	needCheckEC2 bool
	eksClient    *eks.Client
	needCheckEKS bool

	unclean bool
	reports []string
}

func (p *provider) Name() string {
	return "aws"
}

func (p *provider) Check(ctx context.Context) error {
	logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
		Infof("start check AWS (%v) resources", p.cfg.Region)

	if err := p.checkEC2(ctx); err != nil {
		return err
	}
	if err := p.checkEKS(ctx); err != nil {
		return err
	}
	return nil
}

func (p *provider) checkEC2(ctx context.Context) error {
	if !p.needCheckEC2 {
		logrus.Infof("Skip check %v EC2", p.Name())
		return nil
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}

	o, err := describeInstances(ctx, p.ec2Client)
	if err != nil {
		return fmt.Errorf("failed to describeInstances: %w", err)
	}
	if o == nil || len(o.Reservations) == 0 {
		return nil
	}
	ids := []string{}
	for _, r := range o.Reservations {
		if len(r.Instances) == 0 {
			continue
		}

		for _, i := range r.Instances {
			if i.State.Name == types.InstanceStateNameTerminated ||
				i.State.Name == types.InstanceStateNameStopped ||
				i.State.Name == types.InstanceStateNameShuttingDown ||
				i.State.Name == types.InstanceStateNameStopping {
				continue
			}

			var name string
			if len(i.Tags) > 0 {
				for _, t := range i.Tags {
					if strings.ToLower(utils.Value(t.Key)) == "name" {
						name = utils.Value(t.Value)
					}
				}
			}
			if !utils.MatchFilters(name, p.filters) {
				continue
			}
			s := fmt.Sprintf("EC2 instance ID [%v] name [%v] status [%v] Tags %v not cleanup!",
				utils.Value(i.InstanceId), name, i.State.Name, utils.PrintNoIndent(i.Tags))
			logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
				Warn(s)
			p.unclean = true
			p.reports = append(p.reports, s)
			ids = append(ids, utils.Value(i.InstanceId))
		}
	}

	if p.clean && len(ids) > 0 {
		if _, err := terminateInstances(ctx, p.ec2Client, ids); err != nil {
			logrus.Errorf("failed to terminate EC2 instance %v: %v", ids, err)
			return fmt.Errorf("failed to terminate AWS ec2 instance: %w", err)
		}
		logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
			Infof("request to terminate EC2 instances %v", ids)
	}
	return nil
}

func (p *provider) checkEKS(ctx context.Context) error {
	if !p.needCheckEKS {
		logrus.Infof("Skip check %v EKS", p.Name())
		return nil
	}
	o, err := listClusters(ctx, p.eksClient)
	if err != nil {
		return fmt.Errorf("failed to listClusters: %w", err)
	}
	if o == nil || len(o.Clusters) == 0 {
		return nil
	}
	for _, c := range o.Clusters {
		s := fmt.Sprintf("EKS cluster [%v] not cleanup!", c)
		logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
			Warn(s)
		p.unclean = true
		p.reports = append(p.reports, s)
	}

	if p.clean {
		logrus.Warnf("EKS cluster cleanup not supported yet, need to check manually!")
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
	Filters []string
	Clean   bool

	CheckEC2 bool
	CheckEKS bool

	AccessKey string
	SecretKey string
	Token     string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	config, err := config.LoadDefaultConfig(context.TODO(),
		config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			o.AccessKey, o.SecretKey, o.Token)),
		config.WithRegion(o.Region),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load aws config: %w", err)
	}

	return &provider{
		filters: slices.Clone(o.Filters),
		clean:   o.Clean,

		cfg:          config,
		ec2Client:    newEc2Client(config),
		needCheckEC2: o.CheckEC2,
		eksClient:    newEksClient(config),
		needCheckEKS: o.CheckEKS,
		reports:      make([]string, 0),
	}, nil
}
