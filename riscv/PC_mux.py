from myhdl import always_comb, block, intbv, concat, Signal

from riscv.control_constants import *
from riscv.opcode_constants import XPR_LEN


@block
def PC_mux(PC_src_sel, inst_DX, rs1_data, PC_IF, PC_DX,
           handler_PC, epc, PC_PIF):
    """
    PC multiplexer module

    :param Signal PC_src_sel : Select signal
    :param Signal inst_DX: Instruction
    :param Signal rs1_data: data from register source 1
    :param Signal PC_IF: Program counter IF past
    :param Signal PC_DX: Program counter DX
    :param Signal handler_PC: Program counter handler
    :param Signal epc: Exception Program Counter
    :param Signal PC_PIF: Program counter IF current
    """

    base = Signal(intbv(0)[XPR_LEN:])
    offset = Signal(intbv(0)[XPR_LEN:])

    @always_comb
    def PC_mux_assign():

        imm_b = intbv(0)[XPR_LEN:]
        if inst_DX[31]:
            imm_b = concat(intbv((1 << 20) - 1)[20:], inst_DX[7], inst_DX[31:25],
                           inst_DX[12:8], False)
        else:
            imm_b = concat(intbv(0)[20:], inst_DX[7], inst_DX[31:25], inst_DX[12:8], False)

        jal_offset = intbv(0)[XPR_LEN:]
        if inst_DX[31]:
            jal_offset = concat(intbv((1 << 12) - 1)[12:], inst_DX[20:12], inst_DX[20],
                                inst_DX[31:25], inst_DX[25:21], False)
        else:
            jal_offset = concat(intbv(0)[12:], inst_DX[20:12], inst_DX[20],
                                inst_DX[31:25], inst_DX[25:21], False)

        jalr_offset = intbv(0)[XPR_LEN:]
        if inst_DX[31]:
            jalr_offset = concat(intbv((1 << 21) - 1)[21:], inst_DX[31:21], False)
        else:
            jalr_offset = concat(intbv(0)[21:], inst_DX[31:21], False)

        if PC_src_sel == PC_JAL_TARGET:
            base.next = PC_DX
            offset.next = jal_offset
        elif PC_src_sel == PC_JALR_TARGET:
            base.next = rs1_data
            offset.next = jalr_offset
        elif PC_src_sel == PC_BRANCH_TARGET:
            base.next = PC_DX
            offset.next = imm_b
        elif PC_src_sel == PC_REPLAY:
            base.next = PC_IF
            offset.next = 0
        elif PC_src_sel == PC_HANDLER:
            base.next = handler_PC
            offset.next = 0
        elif PC_src_sel == PC_EPC:
            base.next = epc
            offset.next = 0
        else:
            base.next = PC_IF
            offset.next = 4

    @always_comb
    def PC_mux_output():

        PC_PIF.next = base + offset

    return PC_mux_output, PC_mux_assign
