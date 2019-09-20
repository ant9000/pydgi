from .protocol import Protocol
from .interfaces import *

class DGI:

    def __init__(self, serial_number=''):
        self.protocol = Protocol(serial_number)
        self.serial_number = self.protocol.serial_number

    def __enter__(self):
        self.name       = self.protocol.cmd_sign_on()
        self.version    = self.protocol.cmd_get_version()
        self.interfaces = {}
        for intf in self.protocol.cmd_interfaces_list():
            self.interfaces[intf] = {
                'name':   self.protocol.interface_name(intf),
                'config': self.protocol.cmd_interfaces_get_config(intf),
            }

        for intf, s in self.protocol.cmd_interfaces_status():
            self.interfaces[intf]['status'] = s
        return self

    def __exit__(self, *exc):
        self.protocol.cmd_sign_off()
        if exc:
            return False
        return True

    def __str__(self):
        return '{} {} - {}'.format(self.name, self.version, self.serial_number)

    def config(self, intf, data):
        self.protocol.cmd_interfaces_set_config(intf, data)
        cfg = self.protocol.cmd_interfaces_get_config(intf)
        self.interfaces[intf]['config'] = cfg
        return cfg

    def start(self, intf, timestamp=False):
        s = 1
        if timestamp:
            s = 2
        self.protocol.cmd_interfaces_enable(intf, s)
        self.interfaces[intf]['status']['start'] = 1
        if timestamp:
            self.interfaces[intf]['status']['timestamp'] = 1

    def stop(self, intf):
        self.protocol.cmd_interfaces_enable(intf, 0)
        self.interfaces[intf]['status']['start'] = 0

    def poll(self, intf):
        return self.protocol.cmd_interfaces_poll_data(intf)

    def send(self, intf, data):
        self.protocol.cmd_interfaces_send_data(intf, data)

    def power(self):
        if 0x40 in self.interfaces:
            return Power(self)
