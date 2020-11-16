import os
import usb.core
import logging
from kubernetes import client
from openvino.inference_engine import IECore


class NCS2Device:
    def __init__(self, inference_engine=IECore(), device='MYRIAD'):
        self._inference_engine = inference_engine
        self.device = device

    def get_optimization_capabilities(self):
        return self._inference_engine.get_metric(self.device, 'OPTIMIZATION_CAPABILITIES')

    def get_full_device_name(self):
        return self._inference_engine.get_metric(self.device, 'FULL_DEVICE_NAME')


class NCS2DeviceManager:
    def __init__(self, logger=logging):
        self.inference_engine = IECore()
        self.devices = []
        self.corev1 = client.CoreV1Api()
        self.node_name = os.getenv('NODE_NAME', os.uname().nodename).lower()
        self._log = logger

        # Carry out the initial instantiation of available NCS2 devices, this is periodically re-triggered by the USB
        # hotplug event monitoring thread.
        self.update_devices()

    @staticmethod
    def num_devices():
        """ Scan for NCS2 devices """
        devs = usb.core.find(find_all=True, idVendor=0x3e7, idProduct=0x2485)
        if devs is None:
            raise ValueError('Unable to find any connected NCS2 devices')
        return len(list(devs))

    def num_available_devices(self):
        """ Find the number of available NCS2 devices """

        # A single device is expressed as 'MYRIAD', while multiple devices have a device number appended:
        # [ 'MYRIAD.0', 'MYRIAD.1', ... ]
        return sum(map(lambda x: 'MYRIAD' in x, self.inference_engine.available_devices))

    def get_device_names(self):
        device_names = []

        for dev in self.devices:
            device_names.append(dev.get_full_device_name())

        return device_names

    def get_available_devices(self):
        """ Obtain a list of available NCS2 devices """
        return [s for s in self.inference_engine.available_devices if 'MYRIAD' in s]

    def update_devices(self):
        self.devices.clear()

        for dev in self.get_available_devices():
            self.devices.append(NCS2Device(device=dev, inference_engine=self.inference_engine))

    def generate_annotations(self):
        annotations = {}

        for dev in self.devices:
            annotations['ncs2.intel.com/' + dev.device + '.name'] = dev.get_full_device_name()

        return annotations

    def generate_labels(self):
        labels = {
            "intel.com/ncs2": str(self.num_devices()),
        }

        for dev in self.devices:
            optimizations = dev.get_optimization_capabilities()
            for opt in optimizations:
                labels['ncs2.intel.com/' + dev.device + '.' + opt] = "true"

        return labels

    def reconcile(self, device=None):
        """ Reconcile node label and annotation state """

        if device is not None:
            accepted_events = ['add', 'remove']

            # Only bother reconciling if a device has been added or removed
            if device.action in accepted_events:
                self._log.info('Received a USB {} event for {}'.format(device.action, device))
            else:
                return

        self._log.info('Reconciling node {}'.format(self.node_name))

        # Fetch current node metadata
        node = self.corev1.read_node(self.node_name)

        # Extract any annotations or labels belonging to the plugin
        old_annotations = [s for s in node.metadata.annotations if 'ncs2.intel.com/' in s]
        old_labels = [s for s in node.metadata.labels if 'ncs2.intel.com' in s or 'intel.com/ncs2' in s]

        # Flag existing annotations for removal
        annotations = {}
        for annotation in old_annotations:
            annotations[annotation] = None

        # Flag existing labels for removal
        labels = {}
        for label in old_labels:
            labels[label] = None

        # Merge new annotations and labels with the to-be-deleted set. This will clobber any keys previously marked
        # for removal where a valid value exists in the new set, and will simply patch these in-place on the cluster.
        updated_annotations = { **annotations, **self.generate_annotations() }
        updated_labels = { **labels, **self.generate_labels() }

        body = {
            'metadata': {
                'annotations': updated_annotations,
                'labels': updated_labels
            }
        }

        # Apply the patch to the current node
        self.corev1.patch_node(self.node_name, body)
