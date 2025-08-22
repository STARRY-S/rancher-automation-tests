package aws

import (
	"context"
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/sirupsen/logrus"
)

func newEc2Client(cfg aws.Config) *ec2.Client {
	c := ec2.NewFromConfig(cfg)
	return c
}

func describeInstances(
	ctx context.Context, c *ec2.Client,
) (*ec2.DescribeInstancesOutput, error) {
	o, err := c.DescribeInstances(ctx, nil)
	if err != nil {
		logrus.Errorf("DescribeInstances failed: %v", err)
		return nil, err

	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}

func terminateInstances(
	ctx context.Context, c *ec2.Client, ids []string, dryRun bool,
) (*ec2.TerminateInstancesOutput, error) {
	o, err := c.TerminateInstances(
		ctx, &ec2.TerminateInstancesInput{
			InstanceIds: ids,
			DryRun:      &dryRun,
		},
	)
	if err != nil {
		logrus.Errorf("TerminateInstances failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}

func shutdownInstance(
	ctx context.Context, c *ec2.Client, ids []string, dryRun bool,
) (*ec2.StopInstancesOutput, error) {
	o, err := c.StopInstances(
		ctx, &ec2.StopInstancesInput{
			InstanceIds: ids,
			DryRun:      &dryRun,
		},
	)
	if err != nil {
		logrus.Errorf("StopInstances failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}

func startInstance(
	ctx context.Context, c *ec2.Client, ids []string, dryRun bool,
) (*ec2.StartInstancesOutput, error) {
	o, err := c.StartInstances(
		ctx, &ec2.StartInstancesInput{
			InstanceIds: ids,
			DryRun:      &dryRun,
		},
	)
	if err != nil {
		logrus.Errorf("StartInstances failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}
