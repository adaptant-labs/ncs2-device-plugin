import logging
import pyudev


class USBHotplugMonitor:
    def __init__(self, callback=None, logger=logging):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb', device_type='usb_device')

        self._log = logger
        self.observer = pyudev.MonitorObserver(monitor=monitor, callback=callback)

    def start(self):
        self._log.info('Starting USB monitor...')
        self.observer.start()
        self.observer.join()

    def stop(self):
        self._log.info('Stopping USB monitor...')
        self.observer.stop()

