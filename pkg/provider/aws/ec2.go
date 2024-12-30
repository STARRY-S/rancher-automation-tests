package aws

import (
	"context"

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
	return o, nil
}

func terminateInstances(
	ctx context.Context, c *ec2.Client, ids []string,
) (*ec2.TerminateInstancesOutput, error) {
	o, err := c.TerminateInstances(
		ctx, &ec2.TerminateInstancesInput{
			InstanceIds: ids,
		},
	)
	if err != nil {
		logrus.Errorf("TerminateInstances failed: %v", err)
		return nil, err
	}
	return o, nil
}
