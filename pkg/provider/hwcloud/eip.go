package hwcloud

import (
	eip "github.com/huaweicloud/huaweicloud-sdk-go-v3/services/eip/v2"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/eip/v2/model"
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/services/eip/v2/region"
	"github.com/sirupsen/logrus"
)

func newEipClient(auth *ClientAuth) (*eip.EipClient, error) {
	r, err := region.SafeValueOf(auth.Region)
	if err != nil {
		return nil, err
	}
	c, err := eip.EipClientBuilder().
		WithRegion(r).
		WithCredential(auth.Credential).
		SafeBuild()
	if err != nil {
		return nil, err
	}
	return eip.NewEipClient(c), nil
}

func listPublicips(client *eip.EipClient) (*model.ListPublicipsResponse, error) {
	res, err := client.ListPublicips(&model.ListPublicipsRequest{})
	if err != nil {
		logrus.Debugf("ListPublicips failed: %v", err)
		return nil, err
	}
	return res, nil
}
