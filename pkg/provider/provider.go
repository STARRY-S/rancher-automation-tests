package provider

import (
	"context"
)

type Provider interface {
	Check(ctx context.Context) error
}

type Providers []Provider

func (ps *Providers) Run(ctx context.Context) error {
	if ps == nil || len(*ps) == 0 {
		return nil
	}
	for _, p := range *ps {
		if err := p.Check(ctx); err != nil {
			return err
		}
	}
	return nil
}
