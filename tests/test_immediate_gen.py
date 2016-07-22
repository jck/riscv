from random import randint

from myhdl import block, instance, delay, Signal, modbv, concat

from riscv.control_constants import *
from riscv.immediate_gen import immediate_gen
from riscv.opcode_constants import XPR_LEN


@block
def test_immediate_gen():

    instruction = Signal(modbv(0)[XPR_LEN:])
    imm_type = Signal(modbv(0)[IMM_TYPE_WIDTH:])
    imm = Signal(modbv(0)[XPR_LEN:])
    imm_gen_inst = immediate_gen(instruction, imm_type, imm)
    imm_gen_inst.convert(hdl='Verilog')

    rand_value = randint(0, (1 << XPR_LEN) - 1)

    @instance
    def test():

        instruction.next = rand_value
        imm_type.next = IMM_I
        yield delay(10)
        assert imm == concat(*[instruction[31] for _ in range(21)], instruction[31:20])

        imm_type.next = IMM_S
        yield delay(10)
        assert imm == concat(*[instruction[31] for _ in range(21)], instruction[31:25], instruction[12:8],
                             instruction[7])

        imm_type.next = IMM_U
        yield delay(10)
        assert imm == concat(instruction[31], instruction[31:12], modbv(0)[12:])

        imm_type.next = IMM_J
        yield delay(10)
        assert imm == concat(*[instruction[31] for _ in range(12)], instruction[20:12], instruction[20],
                             instruction[31:21], False)

    return test, imm_gen_inst

test_inst = test_immediate_gen()
test_inst.run_sim()
