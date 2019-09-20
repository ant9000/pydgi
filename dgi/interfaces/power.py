from ..utils import *
from time import sleep

class Power:

    def __init__(self, dev):
        self.dev = dev
        self.id  = 0x40
        self.parse_config()

    def parse_config(self):
        cfg = dict(self.dev.interfaces[self.id]['config'])
        typ = u32(cfg[0])
        assert typ in [0x10, 0x11]
        self.type = { 0x10: 'XAM', 0x11: 'PAM' }[typ]
        assert typ == 0x10, "TODO: Only XAM power interface is supported at present"
        self.channel = u32(cfg[1])
        self.ranges   = {}
        for i in range(4):
            range_id    = (cfg[i*12 + 10][3] >> 4) - 1
            calibration = cfg[i*12 + 10][2]
            offset      = u16(cfg[i*12 + 13][2:])
            float_gain  = f32(cfg[i*12 + 14])
            resolution  = f32(cfg[i*12 + 20])
            self.ranges[range_id] = {
                 'calibration': calibration,
                 'offset':      offset,
                 'float_gain':  float_gain,
                 'resolution':  resolution
             }

    def poll(self):
        self.dev.start(self.id)
        res = []
        while True:
            res += self.dev.poll(self.id)
            while len(res):
                sample_type = (res[0] & (3 << 6)) >> 6
                if sample_type == 2: # primary sample
                    if(len(res)<3):
                        break
                    ctrl   = res[0]
                    rng    = (ctrl & (3 << 4)) >> 4
                    raw    = u16(res[1:3])
                    r      = self.ranges[rng]
                    sample = (float(raw) - r['offset']) * r['float_gain'] * r['resolution']
                    res = res[3:]
                elif sample_type == 0: # auxiliary sample
                    if(len(res)<2):
                        break
                    # TODO, PAM only
                    sample = u16(res[:2])
                    res = res[2:]
                elif sample_type == 3: # notification
                    # TODO
                    sample = res[0]
                    res = res[1:]
                else: # reserved
                    # TODO
                    sample = res[0]
                    res = res[1:]
                sample_type = ['AUX', 'RES', 'PRI', 'EVT'][sample_type]
                yield (sample_type, sample)
            sleep(.0001)
