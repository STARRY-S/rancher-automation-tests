module github.com/STARRY-S/rancher-kev2-provisioning-tests

go 1.23.3

replace golang.org/x/crypto => golang.org/x/crypto v0.31.0

require (
	github.com/antonfisher/nested-logrus-formatter v1.3.1
	github.com/aws/aws-sdk-go-v2 v1.36.3
	github.com/aws/aws-sdk-go-v2/config v1.29.9
	github.com/aws/aws-sdk-go-v2/credentials v1.17.62
	github.com/aws/aws-sdk-go-v2/service/ec2 v1.208.0
	github.com/aws/aws-sdk-go-v2/service/eks v1.60.1
	github.com/huaweicloud/huaweicloud-sdk-go-v3 v0.1.144
	github.com/sirupsen/logrus v1.9.3
	github.com/spf13/cobra v1.9.1
	github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cbs v1.0.1144
	github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/common v1.0.1146
	github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/cvm v1.0.1145
	github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/tke v1.0.1133
	github.com/tencentcloud/tencentcloud-sdk-go/tencentcloud/vpc v1.0.1146
	golang.org/x/term v0.31.0
)

require (
	github.com/aws/aws-sdk-go-v2/feature/ec2/imds v1.16.30 // indirect
	github.com/aws/aws-sdk-go-v2/internal/configsources v1.3.34 // indirect
	github.com/aws/aws-sdk-go-v2/internal/endpoints/v2 v2.6.34 // indirect
	github.com/aws/aws-sdk-go-v2/internal/ini v1.8.3 // indirect
	github.com/aws/aws-sdk-go-v2/service/internal/accept-encoding v1.12.3 // indirect
	github.com/aws/aws-sdk-go-v2/service/internal/presigned-url v1.12.15 // indirect
	github.com/aws/aws-sdk-go-v2/service/sso v1.25.1 // indirect
	github.com/aws/aws-sdk-go-v2/service/ssooidc v1.29.1 // indirect
	github.com/aws/aws-sdk-go-v2/service/sts v1.33.17 // indirect
	github.com/aws/smithy-go v1.22.2 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/json-iterator/go v1.1.12 // indirect
	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/spf13/pflag v1.0.6 // indirect
	github.com/stretchr/testify v1.9.0 // indirect
	github.com/tjfoc/gmsm v1.4.1 // indirect
	go.mongodb.org/mongo-driver v1.13.1 // indirect
	golang.org/x/crypto v0.31.0 // indirect
	golang.org/x/sys v0.32.0 // indirect
	gopkg.in/ini.v1 v1.67.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)
