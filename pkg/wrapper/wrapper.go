package wrapper

import (
	"bufio"
	"context"
	"io"
	"os"
	"regexp"

	"github.com/sirupsen/logrus"
)

const (
	DefaultWrapperEOF = "WRAPPER_EOF"
)

type Wrapper struct {
	pipeReader *io.PipeReader
	pipeWriter *io.PipeWriter

	pipeErrReader *io.PipeReader
	pipeErrWriter *io.PipeWriter

	eof string // Mark to exit this wrapper
}

func NewWrapper(eof string) *Wrapper {
	r, w := io.Pipe()
	er, ew := io.Pipe()
	if eof == "" {
		eof = DefaultWrapperEOF // Default wrapper EOF
	}
	wrapper := &Wrapper{
		pipeReader:    r,
		pipeWriter:    w,
		pipeErrReader: er,
		pipeErrWriter: ew,

		eof: eof,
	}
	return wrapper
}

func (w *Wrapper) Run(ctx context.Context) {
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	// Start a goroutine to read from the pipe and write to stdout
	go func() {
		io.Copy(os.Stdout, w.pipeReader)
	}()

	// Start a goroutine to read from the err pipe and write to stderr
	go func() {
		io.Copy(os.Stderr, w.pipeErrReader)
	}()

	// Start a goroutine to read from os stdin and write to the pipe
	go func() {
		sc := bufio.NewScanner(os.Stdin)
		sc.Split(bufio.ScanLines)
		for sc.Scan() {
			line := hideSensitiveInfo(sc.Text())
			if line == w.eof {
				logrus.Warnf("Wrapper: STDERR EOF")
				cancel()
				return
			}
			w.pipeWriter.Write([]byte(line + "\n"))
		}
	}()

	// Start a goroutine to read from os stderr and write to the pipe
	go func() {
		sc := bufio.NewScanner(os.Stderr)
		sc.Split(bufio.ScanLines)
		for sc.Scan() {
			line := hideSensitiveInfo(sc.Text())
			if line == w.eof {
				logrus.Warnf("Wrapper: STDIO EOF")
				cancel()
				return
			}
			w.pipeErrWriter.Write([]byte(line + "\n"))
		}
	}()

	// Wait for context canceled
	<-ctx.Done()
	logrus.Infof("Wrapper finished.")

	w.pipeReader.Close()
	w.pipeWriter.Close()
	w.pipeErrReader.Close()
	w.pipeErrWriter.Close()
}

var (
	ipRegex              = regexp.MustCompile(`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`)
	urlRegex             = regexp.MustCompile(`(http|https)://[^\s]+`)
	kubeConfigRegex      = regexp.MustCompile(`(?i)certificate-authority-data:\s*([^\s]+)`)
	kubeConfigTokenRegex = regexp.MustCompile(`(?i)kubeconfig-user-\s*([^\s]+)`)
)

func hideIPv4Address(line string) string {
	return ipRegex.ReplaceAllString(line, "*.*.*.*")
}

func hideURL(line string) string {
	return urlRegex.ReplaceAllString(line, "<hidden-url>")
}

func hideKubeConfig(line string) string {
	return kubeConfigTokenRegex.ReplaceAllString(
		kubeConfigRegex.ReplaceAllString(line, "<hidden-config>"), "kubeconfig-<hidden-token>",
	)
}

func hideSensitiveInfo(s string) string {
	s = hideKubeConfig(s)
	s = hideURL(s)
	s = hideIPv4Address(s)
	return s
}
