import decoder
import instruction_table
from myhdl import always_comb, Signal, Simulation, delay

def hdl_decoder(instruction):
    """
    HDL decoder module to decode instructions from
    RISC-V ISA.
    """

    @always_comb
    def decoder_output():
    

