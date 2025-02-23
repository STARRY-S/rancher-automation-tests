package tencent

import (
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common"
	"github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common/profile"
)

type ClientAuth struct {
	Region        string
	ClientProfile *profile.ClientProfile
	Credential    *common.Credential
}

func newClientAuth(ak, sk, region string) (*ClientAuth, error) {
	clientProfile := profile.NewClientProfile()
	clientProfile.Language = "zh-CN"
	credential := common.NewCredential(
		ak,
		sk,
	)

	return &ClientAuth{
		Region:        region,
		Credential:    credential,
		ClientProfile: clientProfile,
	}, nil
}
