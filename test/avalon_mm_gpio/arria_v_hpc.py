#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *
from litex.gen.fhdl.utils import get_signals
from litex_boards.platforms import hpc_store_arriav_v31 as arriav_board

from litex.soc.cores.clock import ArriaVPLL
from litex.soc.interconnect import avalon
from litex.soc.interconnect import wishbone
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.config import DEFAULT_IP_PREFIX

from liteeth.phy.gmii import LiteEthPHYGMII

from litescope.core import LiteScopeAnalyzer

from pcie_mitm.ip.gpio import AvalonMMGPIO

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = ArriaVPLL(speedgrade="-3")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(150e6), with_led_chaser=True, with_jtagbone=False,
                 with_etherbone=False, eth_ip=DEFAULT_IP_PREFIX + "50",
                 **kwargs):
        self.platform = platform = arriav_board.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC Avalon-MM<>WB test on Arria V thingy",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq)

        # Ethernet ---------------------------------------------------------------------------------
        if with_etherbone:
            self.platform.toolchain.additional_sdc_commands += [
                'create_clock -name eth_rx_clk -period 8.0 [get_ports {eth_clocks_rx}]',
                'create_clock -name eth_tx_clk -period 8.0 [get_ports {eth_clocks_tx}]',
                'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_rx_clk}]',
                'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_tx_clk}]',
                'set_false_path -from [get_clocks {eth_rx_clk}] -to [get_clocks {eth_tx_clk}]',
            ]
            eth_clock_pads = self.platform.request("eth_clocks")
            eth_pads = self.platform.request("eth")
            self.submodules.ethphy = LiteEthPHYGMII(
                clock_pads = eth_clock_pads,
                pads       = eth_pads,
                # clk_freq   = self.sys_clk_freq,
            )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # JTAGbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.platform.toolchain.additional_sdc_commands += [
                'create_clock -name jtag -period 30.0 [get_ports {altera_reserved_tck}]',
            ]
            self.add_jtagbone()

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

        if True:
            analyzer_signals = set([
                *get_signals(led_pads),
                *get_signals(self.led_gpio),
                *get_signals(self.led_gpio_wb),
                # *get_signals(self.led_gpi_avmm2wb),
            ])
            analyzer_signals_denylist = set([
            ])
            analyzer_signals -= analyzer_signals_denylist
            analyzer_signals = list(analyzer_signals)
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 64*1,
                register     = True,
                clock_domain = "sys",
                samplerate   = sys_clk_freq,
                csr_csv      = "analyzer.csv")

# Build --------------------------------------------------------------------------------------------

def argparse_set_def(parser: argparse.ArgumentParser, dst: str, default):
    changed = False
    for a in parser._actions:
        if dst == a.dest:
            a.default = default
            return
    raise ValueError(f'dest var {dst} arg not found')

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Arria V thingy")
    parser.add_argument("--build",               action="store_true", help="Build bitstream.")
    parser.add_argument("--load",                action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",        default=150e6,       help="System clock frequency.")
    parser.add_argument("--with-etherbone",     action="store_true", help="Enable Etherbone support.")
    parser.add_argument("--eth-ip",              default=DEFAULT_IP_PREFIX + "50", type=str, help="Ethernet/Etherbone IP address.")
    parser.add_argument("--with-jtagbone",       action="store_true", help="Enable JTAGbone support.")
    builder_args(parser)
    soc_core_args(parser)

    # argparse_set_def(parser, 'uart_name', 'crossover')
    argparse_set_def(parser, 'uart_baudrate', 2_000_000)
    argparse_set_def(parser, 'integrated_rom_size', 32*1024)
    argparse_set_def(parser, 'integrated_sram_size', 4*1024)
    argparse_set_def(parser, 'cpu_type', 'picorv32')
    argparse_set_def(parser, 'with_jtagbone', True)
    argparse_set_def(parser, 'with_etherbone', False)
    argparse_set_def(parser, 'csr_csv', 'csr.csv')


    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_etherbone           = args.with_etherbone,
        eth_ip                   = args.eth_ip,
        with_jtagbone            = args.with_jtagbone,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
