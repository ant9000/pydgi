import usb.core
from .utils import *

VENDOR  = 0x03eb
PRODUCT = 0x2111
EP_IN  = 0X87
EP_OUT = 0X06
DGI_RESP_DATA = 0xa0
DGI_RESP_OK   = 0x80
INTERFACES = {
    0x00: 'Timestamp',
    0x20: 'SPI',
    0x21: 'USART',
    0x22: 'I2C',
    0x30: 'GPIO',
    0x40: 'Power (data)',
    0x41: 'Power (sync)',
    0x50: '#undocumented#',
}

class Protocol:

    def __init__(self, serial_number=''):
        devs = list(usb.core.find(idVendor=VENDOR, idProduct=PRODUCT, find_all=True))
        if len(devs) > 1 and not serial_number:
            raise ValueError(
                'Multiple devices found - please specify a serial_number:\n\t%s' %
                '\n\t'.join([ d.serial_number for d in devs])
            )
        if serial_number:
            devs = [ d for d in devs if d.serial_number == serial_number ]
        if not len(devs):
            if serial_number:
                raise ValueError('Device "%s" not found' % serial_number)
            raise ValueError('No device found')
        self.dev = devs[0]
        try:
            self.dev.set_configuration()
        except usb.core.USBError as e:
            pass
        self.serial_number = self.dev.serial_number

    def interface_name(self, interface):
        return INTERFACES.get(interface, '')

    def write(self, cmd, payload=[]):
        data = [cmd]
        n = len(payload)
        data += u16(n)
        data += payload
        n = self.dev.write(EP_OUT, bytes(data))
        assert(n == len(data))
        res = self.dev.read(EP_IN, 512)
        assert(len(res) > 1)
        if res[0] != cmd:
            print('> %02x' % cmd, payload)
            print('<', res)
        assert(res[0] == cmd)
        return res

    def cmd_sign_on(self):
        res = self.write(0x00)
        assert(len(res) > 4)
        assert(res[1] == DGI_RESP_DATA)
        n = u16(res[2:4])
        name = res[4:]
        assert(len(name) == n)
        return ''.join([chr(b) for b in name])

    def cmd_sign_off(self):
        # consume remaining data
        try:
            res = self.dev.read(EP_IN, 512, 10)
            while len(res):
                res = self.dev.read(EP_IN, 512, 10)
        except usb.core.USBError:
            pass
        res = self.write(0x01)
        assert(res[1] == DGI_RESP_OK)

    def cmd_get_version(self):
        res = self.write(0x02)
        assert(res[1] == DGI_RESP_DATA)
        assert(len(res) == 4)
        return "{}.{}".format(*res[2:])

    def cmd_set_mode(self, poll_bytes=2, overflow_indicator=False):
        assert(poll_bytes in (2,4))
        assert(overflow_indicator in (True, False))
        mode = 0
        if poll_bytes == 4:
            mode |= 1 << 2   # set bit 2
        if overflow_indicator:
            mode |= 1 << 0   # set bit 0
        res = self.write(0x0a, [mode])
        assert(res[1] == DGI_RESP_OK)

    def cmd_target_reset(self, reset_asserted=False):
        assert(reset_asserted in (True, False))
        reset_state = 0
        if reset_asserted:
            reset_state |= 1 << 0   # set bit 0
        res = self.write(0x20, [reset_state])
        assert(res[1] == DGI_RESP_OK)

    def cmd_interfaces_list(self):
        res = self.write(0x08)
        assert(len(res) > 3)
        assert(res[1] == DGI_RESP_DATA)
        n = res[2]
        interfaces = res[3:]
        assert(len(interfaces) == n)
        return [i for i in interfaces if i in INTERFACES]

    def cmd_interfaces_enable(self, interface, state):
        assert(interface in INTERFACES)
        assert(state in [0, 1, 2])
        res = self.write(0x10, [interface, state])
        assert(res[1] == DGI_RESP_OK)

    def cmd_interfaces_set_config(self, interface, config):
        assert(interface in INTERFACES)
        payload = [interface]
        for config_id, config_value in config:
            payload += u16(config_id)
            payload += u32(config_value)
        res = self.write(0x12, payload)
        assert(res[1] == DGI_RESP_OK)

    def cmd_interfaces_get_config(self, interface):
        assert(interface in INTERFACES)
        res = self.write(0x13, [interface])
        assert(res[1] == DGI_RESP_DATA)
        assert(len(res) > 4)
        assert(res[4] == interface)
        n = u16(res[2:4])
        data = res[5:]
        while len(data) < n - 1:
            data += self.dev.read(EP_IN, 512)
        config = []
        assert(n == len(data) + 1)
        assert(len(data) % 6 == 0)
        while data:
            config.append([u16(data[:2]), data[2:6]])
            data = data[6:]
        return config

    def cmd_interfaces_poll_data(self, interface):
        assert(interface in INTERFACES)
        res = self.write(0x15, [interface])
        assert(res[1] == DGI_RESP_DATA)
        assert(len(res) > 4)
        assert(res[2] == interface)
        # TODO: length field is 2 or 4 bytes depending on the set mode
        n = u16(res[3:5])
        # TODO: the overflow indicator (if enabled in mode) can appear here
        #       but won't be counted in length
        data = res[5:]
        while len(data) < n:
            data += self.dev.read(EP_IN, 512)
        return data

    def cmd_interfaces_send_data(self, interface, data):
        assert(interface in INTERFACES)
        assert(len(data) <= 250)
        res = self.write(0x14, [interface, data])
        assert(res[1] == DGI_RESP_OK)

    def cmd_interfaces_status(self):
        res = self.write(0x11)
        assert(res[1] == DGI_RESP_DATA)
        data = res[2:]
        assert(len(data) % 2 == 0)
        status = []
        while data:
            if data[0] in INTERFACES:
                s = {
                    'start':     (data[1] & 1) >> 0,
                    'timestamp': (data[1] & 2) >> 1,
                    'overflow':  (data[1] & 4) >> 2,
                }
                status.append((data[0],s))
            data = data[2:]
        return status
