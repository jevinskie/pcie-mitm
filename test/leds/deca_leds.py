#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from litex_boards.platforms import deca

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_usb    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)
        pll.create_clkout(self.cd_hdmi, 40e6)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_led_chaser=True, with_uartbone=False, with_jtagbone=False,
                 **kwargs):
        self.platform = platform = deca.Platform()

        # Defaults to JTAG-UART since no hardware UART.
        real_uart_name = kwargs["uart_name"]
        if real_uart_name == "serial":
            kwargs["uart_name"] = "jtag_uart"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Terasic DECA",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=False)

        # Bug --------------------------------------------------------------------------------------
        input_pads = platform.request("gpio")

        # this is what I want to work but only user_led7 is ever set
        led_pads = platform.request_all("user_led")

        # this works as expected
        # led_pads = [platform.request("user_led") for i in range(8)]

        for src, sink in zip(input_pads, led_pads):
            self.comb += sink.eq(src)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DECA")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    args.cpu_type = "None"

    soc = BaseSoC(
        sys_clk_freq = int(50e6),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=False)

if __name__ == "__main__":
    main()
