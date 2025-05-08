package aws

import (
	"context"
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/eks"
	"github.com/sirupsen/logrus"
)

func newEksClient(cfg aws.Config) *eks.Client {
	c := eks.NewFromConfig(cfg)
	return c
}

func listClusters(
	ctx context.Context, c *eks.Client,
) (*eks.ListClustersOutput, error) {
	o, err := c.ListClusters(ctx, &eks.ListClustersInput{})
	if err != nil {
		logrus.Errorf("ListClusters failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}

func deleteCluster(
	ctx context.Context, c *eks.Client, name string,
) (*eks.DeleteClusterOutput, error) {
	o, err := c.DeleteCluster(ctx, &eks.DeleteClusterInput{
		Name: &name,
	})
	if err != nil {
		logrus.Errorf("DeleteCluster failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}

func deleteNodegroup(
	ctx context.Context, c *eks.Client, cname string, nname string,
) (*eks.DeleteNodegroupOutput, error) {
	o, err := c.DeleteNodegroup(ctx, &eks.DeleteNodegroupInput{
		ClusterName:   &cname,
		NodegroupName: &nname,
	})
	if err != nil {
		logrus.Errorf("DeleteNodegroup failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return o, nil
}
