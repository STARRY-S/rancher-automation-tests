package hwcloud

import (
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
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
	time.Sleep(utils.DefaultInterval)
	return res, nil
}

func deleteServer(client *ecs.EcsClient, id string) (*model.DeleteServersResponse, error) {
	res, err := client.DeleteServers(&model.DeleteServersRequest{
		Body: &model.DeleteServersRequestBody{
			DeletePublicip: utils.Pointer(true),
			DeleteVolume:   utils.Pointer(true),
			Servers: []model.ServerId{
				{
					Id: id,
				},
			},
		},
	})
	if err != nil {
		logrus.Errorf("DeleteServers failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return res, nil
}
