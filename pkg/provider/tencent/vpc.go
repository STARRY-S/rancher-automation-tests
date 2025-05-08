package tencent

import (
	"fmt"
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/sirupsen/logrus"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common/profile"
	vpcapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/vpc/v20170312"
)

func newVPCClient(
	credential *common.Credential,
	region string,
	clientProfile *profile.ClientProfile,
) (*vpcapi.Client, error) {
	client, err := vpcapi.NewClient(
		credential,
		region,
		clientProfile,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create VPC client: %w", err)
	}
	return client, nil
}

func describeAddresses(
	c *vpcapi.Client,
) (*vpcapi.DescribeAddressesResponse, error) {
	request := vpcapi.NewDescribeAddressesRequest()
	response, err := c.DescribeAddresses(request)
	if err != nil {
		logrus.Errorf("DescribeAddresses failed: %v", err)
		return nil, fmt.Errorf("describeAddresses: %w", err)
	}
	time.Sleep(utils.DefaultInterval)
	return response, nil
}
