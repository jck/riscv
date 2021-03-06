from myhdl import always_comb, block, intbv

from riscv.control_constants import *
from riscv.opcode_constants import *


@block
def src_b_mux(src_b_sel, imm, rs2_data, alu_src_b):
    """
    Source B multiplexer module

    :param Signal src_b_sel : Select signal
    :param Signal imm: Mux input 1
    :param Signal rs2_data: Mux input 2
    :param Signal alu_src_b: Output of mux to alu
    """

    @always_comb
    def src_b_mux_output():
        alu_src_b.next = intbv(0)[XPR_LEN:]

        if src_b_sel == SRC_B_RS2:
            alu_src_b.next = rs2_data
        elif src_b_sel == SRC_B_IMM:
            alu_src_b.next = imm
        elif src_b_sel == SRC_B_FOUR:
            alu_src_b.next = intbv(4)[XPR_LEN:]

    return src_b_mux_output
