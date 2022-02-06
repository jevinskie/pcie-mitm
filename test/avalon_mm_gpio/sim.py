#!/usr/bin/env python3

import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig

from litex.soc.interconnect import avalon
from litex.soc.interconnect import wishbone
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from pcie_mitm.ip.gpio import AvalonMMGPIO


# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
    ),

    # Leds.
    ("user_led", 0, Pins(1)),
    ("user_led", 1, Pins(1)),
    ("user_led", 2, Pins(1)),
    ("user_led", 3, Pins(1)),
    ("user_led", 4, Pins(1)),
    ("user_led", 5, Pins(1)),
    ("user_led", 6, Pins(1)),
    ("user_led", 7, Pins(1)),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)

# Bench SoC ----------------------------------------------------------------------------------------

class SimSoC(SoCCore):
    def __init__(self, sys_clk_freq = None, **kwargs):
        platform     = Platform()
        sys_clk_freq = int(sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            ident         = "Avalon-MM GPIO WB bridge test simulation",
            **kwargs)

        self.add_constant("CONFIG_DISABLE_DELAYS", 1)


        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # Trace ------------------------------------------------------------------------------------
        self.platform.add_debug(self, reset=0)

#
        # Leds -------------------------------------------------------------------------------------
        led_pads = platform.request_all("user_led")
        if False:
            self.submodules.leds = LedChaser(
                pads         = led_pads,
                sys_clk_freq = sys_clk_freq)
        else:
            self.submodules.led_gpio = AvalonMMGPIO(self.platform)
            for src, sink in zip(self.led_gpio.out_port, led_pads):
                self.comb += sink.eq(src)
            self.led_gpio_wb = wishbone.Interface(adr_width=1)
            self.add_wb_slave(0x9000_0000, self.led_gpio_wb)
            self.add_memory_region("gpio", 0x9000_0000, length=4, type="io")
            self.submodules.led_gpi_avmm2wb = avalon.AvalonMM2Wishbone(self.led_gpio.avmm, self.led_gpio_wb)


# Main ---------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteEth Bench Simulation")
    parser.add_argument("--sys-clk-freq",         default=200e6,           help="System clock frequency (default: 200MHz)")
    parser.add_argument("--trace",                action="store_true",     help="Enable Tracing")
    parser.add_argument("--trace-cycles",         default=128,             help="Number of cycles to trace")
    parser.add_argument("--opt-level",            default="O3",            help="Verilator optimization level")
    parser.add_argument("--debug-soc-gen",        action="store_true",     help="Don't run simulation")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    sim_config = SimConfig()
    sim_config.add_clocker("sys_clk", freq_hz=args.sys_clk_freq)
    sim_config.add_module("serial2console", "serial")

    soc_kwargs     = soc_core_argdict(args)
    builder_kwargs = builder_argdict(args)

    soc_kwargs['sys_clk_freq'] = int(args.sys_clk_freq)
    soc_kwargs['uart_name'] = 'sim'
    # soc_kwargs['cpu_type'] = 'None'
    soc_kwargs['cpu_type'] = 'femtorv' # slow
    soc_kwargs['cpu_variant'] = 'quark'
    builder_kwargs['csr_csv'] = 'csr.csv'

    soc     = SimSoC(**soc_kwargs)
    if not args.debug_soc_gen:
        builder = Builder(soc, **builder_kwargs)
        for i in range(2):
            build = (i == 0)
            run   = (i == 1)
            builder.build(
                build=build,
                run=run,
                sim_config=sim_config,
                trace=args.trace,
                opt_level=args.opt_level,
            )

if __name__ == "__main__":
    main()
