package wrapper

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var (
	kubeConfig = `kind: Config
clusters:
- name: "local"
  cluster:
    server: "https://127.0.0.1:6443/k8s/clusters/local"
    certificate-authority-data: "ABCABCABCABCABCABC\
      ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC\
      ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC"

users:
- name: "local"
  user:
    token: "kubeconfig-user-123asd:ABCABCABCBAC"`

	expectedKubeConfig = `kind: Config
clusters:
- name: "local"
  cluster:
    server: "<hidden-url>
    <hidden-config>
      ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC\
      ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC"

users:
- name: "local"
  user:
    token: "kubeconfig-<hidden-token>`
)

func Test_hideSensitive(t *testing.T) {
	assert.Equal(t,
		"foo bar address IP is *.*.*.*/123, *.*.*.*, *.*.*.*, *.*.*.* lorem ipsum",
		hideIPv4Address("foo bar address IP is 192.168.1.2/123, 112.22.33.4, 10.2.3.4, 8.8.8.8 lorem ipsum"),
	)

	assert.Equal(t,
		"foo is <hidden-url> lorem ipsum",
		hideURL("foo is http://12.23.34.11.sslip.io/test/asd lorem ipsum"),
	)

	assert.Equal(t,
		"foo is <hidden-url> lorem <hidden-url> ipsum",
		hideURL("foo is http://12.23.34.11.sslip.io/test/asd lorem https://www.baidu.com/ ipsum"),
	)

	s := hideSensitiveInfo(kubeConfig)
	assert.Equal(t, expectedKubeConfig, s)
}
