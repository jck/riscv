from myhdl import block, always_comb, concat, modbv
from riscv.opcode_constants import *
from riscv.alu_constants import *


@block
def alu(op, in1, in2, out):
    """
    Arithmetic and Logic Unit for the processor

     :param Signal in1: Input 1
     :param Signal in2: Input 2
     :param Signal op: Operation to be performed
     :param Signal out: Output of ALU
    """

    @always_comb
    def alu_output():
        shamt = in2[SHAMT_WIDTH:]
        padding = modbv(0)[XPR_LEN-1:]
        out.next = modbv(0)[XPR_LEN:]

        if op == ALU_OP_ADD:
            out.next = in1 + in2
        elif op == ALU_OP_SLL:
            out.next = in1 << shamt
        elif op == ALU_OP_XOR:
            out.next = in1 ^ shamt
        elif op == ALU_OP_OR:
            out.next = in1 | shamt
        elif op == ALU_OP_AND:
            out.next = in1 & shamt
        elif op == ALU_OP_SRL:
            out.next = in1 >> shamt

        elif op == ALU_OP_SEQ:
            if in1 == in2:
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SNE:
            if in1 != in2:
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SUB:
            out.next = in1 - in2

        elif op == ALU_OP_SRA:
            out.next = in1.signed() >> shamt

        elif op == ALU_OP_SLT:
            if in1.signed() < in2.signed():
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SGE:
            if in1.signed() >= in2.signed():
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SLTU:
            if in1 < in2:
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])
        elif op == ALU_OP_SGEU:
            if in1 >= in2:
                out.next = concat(padding, modbv(1)[1:])
            else:
                out.next = concat(padding, modbv(0)[1:])
        else:
            out.next = modbv(0)[XPR_LEN:]

    return alu_output
