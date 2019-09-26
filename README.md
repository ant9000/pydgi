# pydgi
Python implementation for Microchip/Atmel Data Gateway Interface

The Atmel Embedded Debugger (EDBG) offers a [Data Gateway Interface (DGI)](http://ww1.microchip.com/downloads/en/DeviceDoc/40001905B.pdf) for streaming data to a host PC. This is meant as an aid in debugging and demonstration of features in the application running on the target device. DGI consists of multiple interfaces for data streaming. The supported interfaces are SPI Interface, USART Interface, TWI Interface, GPIO Interface.

The protocol is available on Xplained Pro boards and on the [Atmel Power Debugger](https://www.microchip.com/webdoc/GUID-EAD481FD-28E6-4CD5-87FB-5165E7687C12/), that also provide current sensing channels for measuring power consumption.

The only tool that shows power data is [Atmel Data Visualizer](https://www.microchip.com/webdoc/GUID-F897CF19-8EAC-457A-BE11-86BDAC9B59CF/): while very powerful, it unfortunately requires Windows and integrates poorly with an automated setup.

My implementation of the DGI protocol is in pure Python, with the only external requirement of PyUSB; it should work on any platform.

The generic communication protocol is fully implemented; configuration and data parsing are still WIP.

Presently there is a single working interface - the power one: pydgi can stream current data from the XAM module available on Xplained Pro boards.

## Usage

Create a virtualenv, install via pip and launch the provided console power measure reader:

```
virtualenv -p python3 env
. env/bin/activate
pip install pydgi
dgi_power_measure.py
```

Refer to [plot.py](https://github.com/ant9000/pydgi/tree/master/dgi/examples/plot.py) for a matplotlib integration example.
