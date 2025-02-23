package tencent

import (
	"fmt"

	"github.com/sirupsen/logrus"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common/profile"
	tkeapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/tke/v20180525"
)

func newTKEClient(
	credential *common.Credential,
	region string,
	clientProfile *profile.ClientProfile,
) (*tkeapi.Client, error) {
	client, err := tkeapi.NewClient(
		credential,
		region,
		clientProfile,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create TKE client: %w", err)
	}
	return client, nil
}

func describeEKSContainerInstances(
	c *tkeapi.Client,
) (*tkeapi.DescribeEKSContainerInstancesResponse, error) {
	request := tkeapi.NewDescribeEKSContainerInstancesRequest()
	response, err := c.DescribeEKSContainerInstances(request)
	if err != nil {
		logrus.Errorf("ListEKSContainerInstances failed: %v", err)
		return nil, fmt.Errorf("ListEKSContainerInstances: %w", err)
	}
	return response, nil
}
