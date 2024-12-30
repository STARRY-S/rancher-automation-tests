package aws

import (
	"context"
	"fmt"

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
	filter string
	clean  bool

	cfg       aws.Config
	ec2Client *ec2.Client
	eksClient *eks.Client
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
	for _, r := range o.Reservations {
		if len(r.Instances) == 0 {
			continue
		}

		for _, i := range r.Instances {
			if i.State.Name == types.InstanceStateNameTerminated ||
				i.State.Name == types.InstanceStateNameStopped {
				continue
			}
			logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
				Warnf("EC2 instance ID [%v] status [%v] Tags %v not cleanup!",
					utils.Value(i.InstanceId), i.State.Name, utils.PrintNoIndent(i.Tags))
		}
	}
	return nil
}

func (p *provider) checkEKS(ctx context.Context) error {
	o, err := listClusters(ctx, p.eksClient)
	if err != nil {
		return fmt.Errorf("failed to listClusters: %w", err)
	}
	if o == nil || len(o.Clusters) == 0 {
		return nil
	}
	for _, c := range o.Clusters {
		logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
			Warnf("EKS cluster [%v] not cleanup!",
				c)
	}
	logrus.Infof("XXXX cluster\n%v", utils.Print(o))
	return nil
}

type Options struct {
	Filter string
	Clean  bool

	AccessKey string
	SecretKey string
	Token     string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	config, err := config.LoadDefaultConfig(context.TODO(),
		config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			o.AccessKey, o.SecretKey, o.Token)),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load aws config: %w", err)
	}

	return &provider{
		filter: o.Filter,
		clean:  o.Clean,

		cfg:       config,
		ec2Client: newEc2Client(config),
		eksClient: newEksClient(config),
	}, nil
}
