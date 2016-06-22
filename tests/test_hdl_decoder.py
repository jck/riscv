import os
import sys

from myhdl import Simulation, Signal, intbv

lib_path = os.path.abspath(os.path.join('..','riscv'))
sys.path.append(lib_path)

from riscv.hdl_decoder import *
from tests.test_instructions import test_instruction


def test_bench():
    instruction = Signal(intbv(0))

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
        
        # Test Branch Instructions
        branch_instr = ['beq','bne','blt','bge','bltu','bgeu']
        for i in range(len(branch_instr)):
            instruction.next = intbv(int(test_instruction[branch_instr[i]],2))
            yield delay(10)
            assert(bin(rs1, width = 5) == '00010')
            assert(bin(rs2, width = 5) == '00001')
            assert(bin(imm12lo, width = 6) == '110000')
            assert(bin(imm12hi, width = 6) == '000000')
            assert(bin(opcode, width = 7) == '1100011')
            assert(bin(arg_select, width = 10) == '1100110000')
            if i < 2:
                assert(bin(funct3, width = 3) == bin(i, width = 3))
            else:
                assert(bin(funct3, width = 3) == bin(i+2, width = 3))
        
        # Test LUI and AUIPC Instructions
        lui_auipc_instr = ['lui', 'auipc']
        for i in range(len(lui_auipc_instr)):
            instruction.next = intbv(int(test_instruction[lui_auipc_instr[i]],2))
            yield delay(10)
            assert(bin(rd, width = 5) == '00001')
            assert(bin(arg_select, width = 10) == '0010000100')
            assert(bin(imm20, width = 20) == '00000000000000000001')
            if i == 0:
                assert(bin(opcode, width = 7) == '0110111')
            else:
                assert(bin(opcode, width = 7) == '0010111')

        # Test Jump Instructions 
        jump_instr = ['jalr', 'jal']
        for i in range(len(jump_instr)):
            instruction.next = intbv(int(test_instruction[jump_instr[i]],2))
            yield delay(10)
            assert(bin(rd, width = 5) == '00001')
            if i == 0:
                assert(bin(imm12, width = 12) == '000000000001')
                assert(bin(rs1, width = 5) == '00001')
                assert(bin(arg_select, width = 10) == '1010001000')
                assert(bin(opcode, width = 7) == '1100111')
            else:
                assert(bin(imm20, width = 20) == '10001100010000000001')
                assert(bin(arg_select, width = 10) == '0010000100')
                assert(bin(opcode, width = 7) == '1101111')

    return output, stimulus

sim = Simulation(test_bench())
sim.run()
