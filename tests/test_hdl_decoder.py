import os
import sys

from myhdl import Simulation, Signal, intbv

lib_path = os.path.abspath(os.path.join('..','riscv'))
sys.path.append(lib_path)

from riscv.hdl_decoder import *

def test_bench():
    instruction_int = int('1' + '000000' + '00001' + '00010' + '000' + '0000' + '1' + '11000' + '11', 2)
    instruction = Signal(intbv(instruction_int))

    arg_select = Signal(intbv(int('0000000000', 2)))
    opcode = Signal(intbv(int('0000000', 2)))
    funct3 = Signal(intbv(int('000', 2)))
    funct7 = Signal(intbv(int('0000000', 2)))

    rd = Signal(intbv(int('00000', 2)))
    rm = Signal(intbv(int('00000', 2)))
    rs1 = Signal(intbv(int('00000', 2)))
    rs2 = Signal(intbv(int('00000', 2)))
    shamt = Signal(intbv(int('00000', 2)))
    shamtw = Signal(intbv(int('00000', 2)))
    imm12lo = Signal(intbv(int('000000', 2)))
    imm12hi = Signal(intbv(int('000000', 2)))
    imm12 = Signal(intbv(int('000000000000', 2)))
    imm20 = Signal(intbv(int('00000000000000000000', 2)))

    output = hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw, opcode, funct3, funct7)

    @instance
    def stimulus():
        for i in range(5):
            instruction.next = instruction
            yield delay(10)
            print "Argument Select: " + bin(arg_select, width = 10)

    return output, stimulus

sim = Simulation(test_bench())
sim.run()