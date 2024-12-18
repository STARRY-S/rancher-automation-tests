package aws

import (
	"context"

	"github.com/sirupsen/logrus"
)

type provider struct {
}

func (p *provider) Check(ctx context.Context) error {
	logrus.WithFields(logrus.Fields{"Provider": "AWS"}).
		Infof("start check AWS (Global) resources")
	return nil
}

type Options struct {
	Regex string

	AccessKey string
	SecretKey string
	ProjectID string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	return &provider{}, nil
}
