package hwcloud

import (
	"github.com/huaweicloud/huaweicloud-sdk-go-v3/core/auth/basic"
)

type ClientAuth struct {
	Region     string
	Credential *basic.Credentials
}

func newClientAuth(ak, sk, region, projectID string) (*ClientAuth, error) {
	c, err := basic.NewCredentialsBuilder().
		WithAk(ak).
		WithSk(sk).
		WithProjectId(projectID).
		SafeBuild()
	if err != nil {
		return nil, err
	}
	return &ClientAuth{
		Region:     region,
		Credential: c,
	}, nil
}
