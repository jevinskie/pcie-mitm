from pathlib import Path

from migen import *
from litex.soc.interconnect import avalon
from litex.soc.interconnect import wishbone


# Avalon-MM PIO ------------------------------------------------------------------------------------

class AvalonMMGPIO(Module):
    def __init__(self, platform):
        platform.add_ip((Path(__file__).parent / "gpio.qsys").resolve())
        self.avmm     = avalon.AvalonMMInterface()
        self.out_port = Signal(8)
        self.specials += Instance("gpio_pio",
            i_clk        =  ClockSignal(),
            i_reset_n    = ~ResetSignal(),
            i_address    =  self.avmm.address,
            i_write_n    = ~self.avmm.write,
            i_writedata  =  self.avmm.writedata,
            i_chipselect =  self.avmm.chipselect,
            o_readdata   =  self.avmm.readdata,
            o_out_port   =  self.out_port,
        )
