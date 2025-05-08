package tencent

import (
	"fmt"
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/sirupsen/logrus"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common/profile"
	cvmapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cvm/v20170312"
)

func newCVMClient(
	credential *common.Credential,
	region string,
	clientProfile *profile.ClientProfile,
) (*cvmapi.Client, error) {
	client, err := cvmapi.NewClient(
		credential,
		region,
		clientProfile,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create CVM client: %w", err)
	}
	return client, nil
}

func describeInstances(
	c *cvmapi.Client,
) (*cvmapi.DescribeInstancesResponse, error) {
	request := cvmapi.NewDescribeInstancesRequest()
	response, err := c.DescribeInstances(request)
	if err != nil {
		logrus.Errorf("DescribeInstances failed: %v", err)
		return nil, fmt.Errorf("describeInstances: %w", err)
	}
	time.Sleep(utils.DefaultInterval)
	return response, nil
}
