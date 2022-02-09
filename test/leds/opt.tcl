#!/usr/bin/env yosys

yosys read_verilog build/terasic_deca/gateware/terasic_deca.v
yosys proc
yosys opt_clean
yosys opt
yosys write_verilog opt.v
