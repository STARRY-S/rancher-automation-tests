package awscn

import (
	"context"

	"github.com/sirupsen/logrus"
)

type provider struct {
	filter string
	clean  bool
}

func (p *provider) Check(ctx context.Context) error {
	logrus.WithFields(logrus.Fields{"Provider": "AWSCN"}).
		Infof("start check AWS (China) resources")
	return nil
}

type Options struct {
	Filter string
	Clean  bool

	AccessKey string
	SecretKey string
	ProjectID string
	Region    string
}

func NewProvider(o *Options) (*provider, error) {
	return &provider{
		filter: o.Filter,
		clean:  o.Clean,
	}, nil
}
