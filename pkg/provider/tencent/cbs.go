package tencent

import (
	"fmt"
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	cbsapi "github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cbs/v20170312"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common/profile"
)

func newCBSClient(
	credential *common.Credential,
	region string,
	clientProfile *profile.ClientProfile,
) (*cbsapi.Client, error) {
	client, err := cbsapi.NewClient(
		credential,
		region,
		clientProfile,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create CBS client: %w", err)
	}
	time.Sleep(utils.DefaultInterval)
	return client, nil
}

func describeDisks(c *cbsapi.Client) (*cbsapi.DescribeDisksResponse, error) {
	request := cbsapi.NewDescribeDisksRequest()
	response, err := c.DescribeDisks(request)
	if err != nil {
		return nil, fmt.Errorf("describeCBSDisk: %w", err)
	}
	time.Sleep(utils.DefaultInterval)
	return response, nil
}
