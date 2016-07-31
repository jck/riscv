from random import randint

from myhdl import block, Signal, modbv, instance, concat, delay

from riscv.PC_mux import PC_mux
from riscv.control_constants import *
from riscv.opcode_constants import INST_WIDTH, XPR_LEN


@block
def test_pc_mux():

    PC_src_sel = Signal(modbv(0)[PC_SRC_SEL_WIDTH:])
    inst_DX = Signal(modbv(randint(0, (1 << INST_WIDTH) - 1))[INST_WIDTH:])
    rs1_data, PC_IF, PC_DX, handler_PC, epc = [Signal(modbv(randint(0, (1 << XPR_LEN) - 1))[XPR_LEN:]) for _ in range(5)]
    PC_PIF = Signal(modbv(0)[XPR_LEN:])

    pc_mux_inst = PC_mux(PC_src_sel, inst_DX, rs1_data, PC_IF, PC_DX, handler_PC, epc, PC_PIF)
    pc_mux_inst.convert(hdl='Verilog')

    imm_b = concat(*[inst_DX[31] for _ in range(20)], inst_DX[7], inst_DX[31:25], inst_DX[12:8], False)
    jal_offset = concat(*[inst_DX[31] for _ in range(12)], inst_DX[20:12], inst_DX[20],
                        inst_DX[31:25], inst_DX[25:21], False)
    jalr_offset = concat(*[inst_DX[31] for _ in range(21)], inst_DX[31:21], False)

    @instance
    def test():
        PC_src_sel.next = PC_JAL_TARGET
        yield delay(10)
        assert PC_PIF == modbv(PC_DX + jal_offset)[XPR_LEN:]

        PC_src_sel.next = PC_JALR_TARGET
        yield delay(10)
        assert PC_PIF == modbv(rs1_data + jalr_offset)[XPR_LEN:]

        PC_src_sel.next = PC_BRANCH_TARGET
        yield delay(10)
        assert PC_PIF == modbv(PC_DX + imm_b)[XPR_LEN:]

        PC_src_sel.next = PC_REPLAY
        yield delay(10)
        assert PC_PIF == PC_IF

        PC_src_sel.next = PC_HANDLER
        yield delay(10)
        assert PC_PIF == handler_PC

        PC_src_sel.next = PC_EPC
        yield delay(10)
        assert PC_PIF == epc

        PC_src_sel.next = PC_PLUS_FOUR
        yield delay(10)
        assert PC_PIF == modbv(PC_IF + 4)[XPR_LEN:]

    return pc_mux_inst, test

test_inst = test_pc_mux()
test_inst.run_sim()
