package utils

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_MatchFilters(t *testing.T) {
	type P struct {
		s        string
		filters  []string
		excludes []string
		result   bool
	}

	var cases = []P{
		{"abc", []string{}, []string{}, true},
		{"autok3s.user-validation-1.ap-region-1.aws.master", []string{"abc"}, []string{}, false},
		{"autok3s.user-validation-1.ap-region-1.aws.master", []string{"autok3s", "validation"}, []string{}, true},
		{"auto-rancher-test-1", []string{"auto", "foo"}, []string{}, true},
		{"auto-rancher-test-1", []string{"auto", "foo"}, nil, true},
		{"auto-rancher-test-1-DoNotDelete", []string{"auto-", "foo"}, []string{"DoNotDelete"}, false},
		{"auto-DoNotDelete", []string{"auto-", "foo"}, []string{"DoNotDelete"}, false},
		{"", []string{}, []string{}, true},
	}

	for _, c := range cases {
		t.Logf("s: %s, filters: %v, excludes: %v, result: %v\n", c.s, c.filters, c.excludes, c.result)
		assert.Equal(t, c.result, MatchFilters(c.s, c.filters, c.excludes))
	}
}
