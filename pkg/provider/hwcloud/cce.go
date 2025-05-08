package hwcloud

import (
	"time"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	cce "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/cce/v3"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/cce/v3/model"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/cce/v3/region"
	"github.com/sirupsen/logrus"
)

func newCCEClient(auth *ClientAuth) (*cce.CceClient, error) {
	reg, err := region.SafeValueOf(auth.Region)
	if err != nil {
		return nil, err
	}
	cli, err := cce.CceClientBuilder().
		WithRegion(reg).
		WithCredential(auth.Credential).
		SafeBuild()
	if err != nil {
		return nil, err
	}
	return cce.NewCceClient(cli), nil
}

func listClusters(client *cce.CceClient) (*model.ListClustersResponse, error) {
	res, err := client.ListClusters(&model.ListClustersRequest{})
	if err != nil {
		logrus.Errorf("ListClusters failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return res, nil
}

func deleteCluster(client *cce.CceClient, id string) (*model.DeleteClusterResponse, error) {
	res, err := client.DeleteCluster(&model.DeleteClusterRequest{
		ClusterId: id,
	})
	if err != nil {
		logrus.Errorf("DeleteCluster failed: %v", err)
		return nil, err
	}
	time.Sleep(utils.DefaultInterval)
	return res, nil
}
