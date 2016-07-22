from myhdl import always_comb, block

from riscv.control_constants import *
from riscv.opcode_constants import *


@block
def src_a_mux(src_a_sel, PC_DX, rs1_data, alu_src_a):
    """
    Source A multiplexer module
    
    :param Signal src_a_sel : Select signal
    :param Signal PC_DUX: Mux input 1
    :param Signal rs1_data: Mux input 2
    :param Signal alu_src_a: Output of mux to alu
    """

    @always_comb
    def src_a_mux_output():
        alu_src_a.next = modbv(0)[XPR_LEN:]

        if src_a_sel == SRC_A_RS1:
            alu_src_a.next = PC_DX
        elif src_a_sel == SRC_A_PC:
            alu_src_a.next = rs1_data

    return src_a_mux_output
