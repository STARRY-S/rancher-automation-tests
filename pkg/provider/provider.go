package provider

import (
	"context"
	"fmt"
	"os"
	"strings"

	"github.com/STARRY-S/rancher-kev2-provisioning-tests/pkg/utils"
	"github.com/sirupsen/logrus"
)

type Provider interface {
	// Name returns provider name
	Name() string

	// Run check function of each provider
	Check(ctx context.Context) error

	// Get reports of all providers.
	Report() string

	// There are resources remain./chanhangarDockerfile
	Unclean() bool
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

func (ps *Providers) SaveReport(
	ctx context.Context, output string, autoYes bool,
) error {
	if ps == nil || len(*ps) == 0 {
		return nil
	}

	skip := true
	for _, p := range *ps {
		if p.Unclean() {
			skip = false
			break
		}
	}
	if skip {
		logrus.Infof("No remaining resources, skip writing reports")
		return nil
	}

	reports := []string{}
	for _, p := range *ps {
		s := p.Report()
		if len(s) == 0 {
			continue
		}
		logrus.Infof("Saving [%v] remaning resources reports", p.Name())
		reports = append(reports, s)
	}
	report := strings.Join(reports, "\n")

	if err := utils.CheckFileExistsPrompt(ctx, output, autoYes); err != nil {
		return err
	}
	f, err := os.OpenFile(output, os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		return fmt.Errorf("failed to open %q: %w", output, err)
	}
	defer f.Close()
	if _, err := f.WriteString(report); err != nil {
		return fmt.Errorf("failed to write file %q: %w", output, err)
	}

	logrus.Infof("Report output to %v", output)
	return nil
}
