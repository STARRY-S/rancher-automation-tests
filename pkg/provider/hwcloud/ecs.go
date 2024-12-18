package hwcloud

import (
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/core/config"
	ecs "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/ecs/v2"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/ecs/v2/model"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/ecs/v2/region"
	"github.com/sirupsen/logrus"
)

func newEcsClient(auth *ClientAuth) (*ecs.EcsClient, error) {
	reg, err := region.SafeValueOf(auth.Region)
	if err != nil {
		return nil, err
	}
	cli, err := ecs.EcsClientBuilder().
		WithHttpConfig(config.DefaultHttpConfig().WithRetries(3)).
		WithRegion(reg).
		WithCredential(auth.Credential).
		SafeBuild()
	if err != nil {
		return nil, err
	}
	return ecs.NewEcsClient(cli), nil
}

func listCloudServers(client *ecs.EcsClient) (*model.ListCloudServersResponse, error) {
	res, err := client.ListCloudServers(&model.ListCloudServersRequest{})
	if err != nil {
		logrus.Errorf("ListCloudServers failed: %v", err)
		return nil, err
	}
	return res, nil
}
