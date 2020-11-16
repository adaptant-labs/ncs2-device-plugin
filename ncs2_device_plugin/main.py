import logging
import signal
import sys
from kubernetes import config
from ncs2_device_plugin.ncs2 import NCS2DeviceManager
from ncs2_device_plugin.usb_monitor import USBHotplugMonitor


def setup_logger():
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger('ncs2_device_plugin')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def main():
    logger = setup_logger()

    config.load_kube_config()

    ncs2 = NCS2DeviceManager(logger=logger)

    logger.info('Discovered {} NCS2 device(s):'.format(ncs2.num_devices()))

    for dev in ncs2.devices:
        logger.info('\t{}: {}, Optimizations: {}'.format(dev.device,dev.get_full_device_name(),
                                                         dev.get_optimization_capabilities()))

    # Kick off the initial reconciliation, which will apply the labels/annotations to the node based current state.
    logger.info('Applying initial labels and annotations to current node...')
    ncs2.reconcile()

    monitor = USBHotplugMonitor(logger=logger, callback=ncs2.reconcile)

    def shutdown(signum, frame):
        logger.info('Caught signal {}, exiting...'.format(signum))
        monitor.stop()
        sys.exit(1)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Kick off the USB hotplug event monitoring thread, this will trigger a reconciliation of node labels and
    # annotations when a USB device is added or removed from the system.
    monitor.start()


if __name__ == '__main__':
    sys.exit(main() or 0)
