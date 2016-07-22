from random import randint

from myhdl import block, instance, Signal, delay, modbv

from riscv.src_a_mux import src_a_mux
from riscv.src_b_mux import src_b_mux
from riscv.control_constants import *
from riscv.opcode_constants import XPR_LEN


@block
def test_mux():

    src_a_sel = Signal(modbv(0)[SRC_A_SEL_WIDTH:])
    src_b_sel = Signal(modbv(0)[SRC_B_SEL_WIDTH:])
    PC_DX, rs1_data, alu_src_a, imm, rs2_data, alu_src_b = \
        [Signal(modbv(randint(0, (1 << XPR_LEN) - 1))[XPR_LEN:]) for _ in range(6)]

    mux_a = src_a_mux(src_a_sel, PC_DX, rs1_data, alu_src_a)
    mux_a.convert(hdl='Verilog')
    mux_b = src_b_mux(src_b_sel, imm, rs2_data, alu_src_b)
    mux_b.convert(hdl='Verilog')

    @instance
    def test():
        src_a_sel.next = SRC_A_RS1
        src_b_sel.next = SRC_B_RS2
        yield delay(10)
        assert alu_src_a == PC_DX
        assert alu_src_b == rs2_data

        src_a_sel.next = SRC_A_PC
        src_b_sel.next = SRC_B_IMM
        yield delay(10)
        assert alu_src_a == rs1_data
        assert alu_src_b == imm

        src_a_sel.next = SRC_A_ZERO
        src_b_sel.next = SRC_B_FOUR
        yield delay(10)
        assert alu_src_a == 0
        assert alu_src_b == 4

        src_b_sel.next = SRC_B_ZERO
        yield delay(10)
        assert alu_src_b == 0

    return test, mux_a, mux_b

test_inst = test_mux()
test_inst.run_sim()
