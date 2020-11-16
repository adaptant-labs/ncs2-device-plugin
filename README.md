# Intel NCS2 device plugin for Kubernetes

[![PyPI](https://img.shields.io/pypi/v/ncs2-device-plugin.svg)](https://pypi.python.org/pypi/ncs2-device-plugin)
[![PyPI](https://img.shields.io/pypi/pyversions/ncs2-device-plugin.svg)](https://pypi.python.org/pypi/ncs2-device-plugin)
[![Docker Pulls](https://img.shields.io/docker/pulls/adaptant/ncs2-device-plugin.svg)](https://hub.docker.com/repository/docker/adaptant/ncs2-device-plugin)

A Kubernetes device plugin for the Intel Neural Compute Stick 2 (NCS2) / Intel Movidius MyriadX

## Quick Start

To directly install `ncs2-device-plugin` as a `DaemonSet` into the Kubernetes cluster:

```
$ kubectl apply -f https://raw.githubusercontent.com/adaptant-labs/ncs2-device-plugin/ncs2-device-plugin.yaml
```

Pods will be scheduled on any node with a `feature.node.kubernetes.io/usb-ff_03e7_2485.present` (provided by [NFD]) or
`accelerators/ncs2` (provided by [k8s-auto-labeller], in combination with NFD-based discovery) label set. These labels
can also be set manually on NCS2-capable nodes for simple deployments in order to enqueue the Pod.

[NFD]: https://github.com/kubernetes-sigs/node-feature-discovery
[k8s-auto-labeller]: https://github.com/adaptant-labs/k8s-auto-labeller

## Annotations

Annotations are produced for the per-device full device name, allowing for different device types to be explicitly
targeted, regardless of their insertion order into the system:

```
# For a single device
ncs2.intel.com/MYRIAD.name: Intel Movidius Myriad X VPU

# For multiple devices
ncs2.intel.com/MYRIAD.0.name: Intel Movidius Myriad X VPU
...
```
## Node Labels

Node labels are produced for the number of devices and per-device optimization capabilities:

```
intel.com/ncs2=<number of NCS2 devices>

# For a single device
ncs2.intel.com/MYRIAD.FP16=true

# For multiple devices
ncs2.intel.com/MYRIAD.0.FP16=true
...
```

## USB Hotplug Event Reconciliation

Node labels and annotations are reconciled on the node each time a USB device is added or removed from the system. This
can be seen below:

```
2020-11-16 00:16:52 INFO     Discovered 1 NCS2 device(s):
2020-11-16 00:16:52 INFO     	MYRIAD: Intel Movidius Myriad X VPU, Optimizations: ['FP16']
2020-11-16 00:16:52 INFO     Applying initial labels and annotations to current node...
2020-11-16 00:16:52 INFO     Reconciling node sgx-celsius-w550power
2020-11-16 00:16:52 INFO     Starting USB monitor...
2020-11-16 00:17:04 INFO     Received a USB remove event for Device('/sys/devices/pci0000:00/0000:00:14.0/usb1/1-4')
2020-11-16 00:17:04 INFO     Reconciling node sgx-celsius-w550power
2020-11-16 00:17:26 INFO     Received a USB add event for Device('/sys/devices/pci0000:00/0000:00:14.0/usb1/1-4')
2020-11-16 00:17:26 INFO     Reconciling node sgx-celsius-w550power
```

## Features and bugs

Please file feature requests and bugs in the [issue tracker][tracker].

## Acknowledgements

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant
agreement No 825480 ([SODALITE]).

## License

`ncs2-device-plugin` is licensed under the terms of the Apache 2.0 license, the full
version of which can be found in the LICENSE file included in the distribution.

[tracker]: https://github.com/adaptant-labs/ncs2-device-plugin/issues
[SODALITE]: https://sodalite.eu