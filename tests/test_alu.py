from myhdl import block, instance, Signal, delay

from riscv.alu import alu
from riscv.alu_constants import *
from riscv.opcode_constants import XPR_LEN, SHAMT_WIDTH
from random import randint


@block
def test_alu():

    op = Signal(modbv(0)[ALU_OP_WIDTH:])
    out = Signal(modbv(0)[XPR_LEN:])
    val1 = randint(-(1 << (XPR_LEN - 1)), (1 << (XPR_LEN - 1)) - 1)
    val2 = randint(-(1 << (XPR_LEN - 1)), (1 << (XPR_LEN - 1)) - 1)
    in1 = Signal(modbv(val1)[XPR_LEN:])
    in2 = Signal(modbv(val2)[XPR_LEN:])
    alu_inst = alu(op, in1, in2, out)
    shamt = in2[SHAMT_WIDTH:]
    @instance
    def test():
        op.next = ALU_OP_ADD
        yield delay(10)
        assert out == modbv(val1 + val2)[XPR_LEN:]

        op.next = ALU_OP_SLL
        yield delay(10)
        assert out == modbv(val1 << shamt)[XPR_LEN:]

        op.next = ALU_OP_XOR
        yield delay(10)
        assert out == modbv(val1 ^ shamt)[XPR_LEN:]

        op.next = ALU_OP_OR
        yield delay(10)
        assert out == modbv(val1 | shamt)[XPR_LEN:]

        op.next = ALU_OP_AND
        yield delay(10)
        assert out == modbv(val1 & shamt)[XPR_LEN:]

        op.next = ALU_OP_SRL
        yield delay(10)
        assert out == modbv(in1.val >> shamt)[XPR_LEN:]

        op.next = ALU_OP_SEQ
        yield delay(10)
        assert out == (val1 == val2)

        op.next = ALU_OP_SNE
        yield delay(10)
        assert out == (val1 != val2)

        op.next = ALU_OP_SUB
        yield delay(10)
        assert out == modbv(val1 - val2)[XPR_LEN:]

        op.next = ALU_OP_SRA
        yield delay(10)
        assert out == modbv(val1 >> shamt)[XPR_LEN:]

        op.next = ALU_OP_SLT
        yield delay(10)
        assert out == (val1 < val2)

        op.next = ALU_OP_SGE
        yield delay(10)
        assert out == (val1 >= val2)

        op.next = ALU_OP_SLTU
        yield delay(10)
        assert out == (in1.val < in2.val)

        op.next = ALU_OP_SGEU
        yield delay(10)
        assert out == (in1.val >= in2.val)

    return test, alu_inst

test_inst = test_alu()
test_inst.run_sim()
