#!/usr/bin/env python3

import argparse, sys

import dgi

def read_power_data(serial_number=None, show_config=False):
    with dgi.DGI(serial_number=serial_number) as dev:
        if show_config:
            print("Connected to %s" % dev)
            print("Available interfaces: ", ", ".join([ intf['name'] for intf in dev.interfaces.values() ]))
        power = dev.power()
        if show_config:
            print("Configuration for power interface:")
            print("\tType: %s" % power.type)
            for range_id, r in power.ranges.items():
                print("\tRange %02x: calibration=%d, offset=%d, float gain=%.3f, resolution=%.3f" % (
                    range_id, r['calibration'], r['offset'], r['float_gain'], r['resolution']
                ))
            input("Press ENTER to start acquisition\n")
        for sample_type, sample in power.poll():
            if sample_type == 'PRI':
                print('%.3fμA' %  sample)

def command_args():
    parser = argparse.ArgumentParser(description='Read DGI power interface measures')
    parser.add_argument('-s', '--serial_number',
                        help='specify serial number of EDBG device if you have more than one')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False,
                        help='also print information about device')
    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = command_args()
        read_power_data(serial_number=args.serial_number, show_config=args.verbose)
    except KeyboardInterrupt:
        if args.verbose:
            print("Interrupted by user.")
    except Exception as e:
        print("Error: ",e)
        sys.exit(1)
