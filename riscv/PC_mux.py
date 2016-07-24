from myhdl import always_comb, block, modbv, concat

from riscv.control_constants import *


@block
def PC_mux(PC_src_sel, inst_DX, rs1_data, PC_IF, PC_DX,
           handler_PC, epc, PC_PIF):
    """
    PC multiplexer module

    :param Signal PC_src_sel : Select signal
    :param Signal inst_DX: Insruction
    :param Signal rs1_data: data from register source 1
    :param Signal PC_IF: Program counter IF past
    :param Signal PC_DX: Program counter DX
    :param Signal handler_PC: Program counter handler
    :param Signal epc: Exception Program Counter
    :param Signal PC_PIF: Program counter IF current
    """
    @always_comb
    def PC_mux_output():

        imm_b = concat(inst_DX[31], inst_DX[7], inst_DX[30:25],
                       inst_DX[11:8], modbv(0)[1:])[20:]
        jal_offset = concat(inst_DX[31], inst_DX[19:12], inst_DX[20],
                            inst_DX[30:25], inst_DX[24:21], modbv(0)[1:])[12:]
        jalr_offset = concat(inst_DX[31], inst_DX[30:21], modbv(0)[1:])[21:]

        if PC_src_sel == PC_JAL_TARGET:
            base = PC_DX
            offset = jal_offset
        elif PC_src_sel == PC_JALR_TARGET:
            base = rs1_data
            offset = jalr_offset
        elif PC_src_sel == PC_BRANCH_TARGET:
            base = PC_DX
            offset = imm_b
        elif PC_src_sel == PC_REPLAY:
            base = PC_IF
            offset = 0
        elif PC_src_sel == PC_HANDLER:
            base = handler_PC
            offset = 0
        elif PC_src_sel == PC_EPC:
            base = epc
            offset = 0
        else:
            base = PC_IF
            offset = 4

        PC_PIF.next = base + offset

    return PC_mux_output
