from myhdl import *
from opcode_constants import *
from alu_constants import *


@block
def alu(op, in1, in2, out):
    """
    Arithmetic and Logic Unit for the processor

     :param Signal in1: Input 1
     :param Signal in2: Input 2
     :param Signal op: Operation to be performed
     :param Signal out: Ouput of ALU
    """
    shamt = in2[SHAMT_WIDTH-1:]

    @always_comb
    def alu_output():

        padding = modbv(0)[XPR_LEN-1:]
        out = modbv(0)[XPR_LEN-1:]

        if op == ALU_OP_ADD:
            out = in1 + in2
        elif op == ALU_OP_SLL:
            out = in1 << shamt
        elif op == ALU_OP_XOR:
            out = in1 ^ shamt
        elif op == ALU_OP_OR:
            out = in1 | shamt
        elif op == ALU_OP_AND:
            out = in1 & shamt
        elif op == ALU_OP_SRL:
            out = in1 >> shamt

        elif op == ALU_OP_SEQ:
            if in1 == in2:
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SNE:
            if in1 != in2:
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SUB:
            out = in1 - in2

        elif op == ALU_OP_SRA:
            out = in1.signed() >> shamt

        elif op == ALU_OP_SLT:
            if in1.signed() < in2.signed():
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SGE:
            if in1.signed() >= in2.signed():
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])

        elif op == ALU_OP_SLTU:
            if in1 < in2:
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])
        elif op == ALU_OP_SGEU:
            if in1 >= in2:
                out = concat(padding, modbv(1)[1:])
            else:
                out = concat(padding, modbv(0)[1:])
        else:
            out = modbv(0)[XPR_LEN-1:]
    return alu_output
