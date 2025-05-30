## Rancher Prime GC Automation Tests

[![Build](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/ci.yaml/badge.svg)](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/ci.yaml)
[![HWCloud Provisioning Tests](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/provisioning-tests-hwcloud.yaml/badge.svg)](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/provisioning-tests-hwcloud.yaml)
[![AWSCN Provisioning Tests](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/provisioning-tests-awscn.yaml/badge.svg)](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/provisioning-tests-awscn.yaml)
[![Validation Tests](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/validation-tests.yaml/badge.svg)](https://github.com/STARRY-S/rancher-automation-tests/actions/workflows/validation-tests.yaml)

Automate Rancher Prime GC automation tests on GitHub Actions.

- KEv2 provisioning tests
- Rancher FlatNetwork Validation tests

### Public Cloud Resource Checker

A simple command line CLI to check if the public cloud resource is cleaned up.

```console
$ go build -o checker .
$ ./checker -h
Public cloud remain resource check CLI

Usage:
  checker [flags]
  checker [command]

Available Commands:
  aws         Check AWS (Global) resources
  awscn       Check AWS (China) resources
  completion  Generate the autocompletion script for the specified shell
  help        Help about any command
  hwcloud     Check Huawei Cloud resources
  version     
......
```

### LICENSE

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
