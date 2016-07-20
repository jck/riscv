import os
import sys

from myhdl import Simulation, bin, instance, delay

lib_path = os.path.abspath(os.path.join('..','riscv'))
sys.path.append(lib_path)

from riscv.hdl_decoder import *
from tests.test_instructions import test_instruction


def test_bench():
    instruction = Signal(intbv(0)[32:])

    arg_select = Signal(intbv(int('0000000000', 2))[10:])
    opcode = Signal(intbv(int('0000000', 2))[7:])
    funct3 = Signal(intbv(int('000', 2))[3:])
    funct7 = Signal(intbv(int('0000000', 2))[7:])

    rd = Signal(intbv(int('00000', 2))[5:])
    rm = Signal(intbv(int('00000', 2))[5:])
    rs1 = Signal(intbv(int('00000', 2))[5:])
    rs2 = Signal(intbv(int('00000', 2))[5:])
    shamt = Signal(intbv(int('00000', 2))[5:])
    shamtw = Signal(intbv(int('00000', 2))[5:])
    imm12lo = Signal(intbv(int('000000', 2))[6:])
    imm12hi = Signal(intbv(int('000000', 2))[6:])
    imm12 = Signal(intbv(int('000000000000', 2))[12:])
    imm20 = Signal(intbv(int('00000000000000000000', 2))[20:])

    output = hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw, opcode, funct3, funct7)
    output.convert(hdl='Verilog')

    @instance
    def stimulus():

        # Test Branch Instructions
        branch_instr = ['beq','bne','blt','bge','bltu','bgeu']
        for i in range(len(branch_instr)):
            instruction.next = intbv(int(test_instruction[branch_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rs1, width=5) == '00010')
            assert(bin(rs2, width=5) == '00001')
            assert(bin(imm12lo, width=6) == '010000')
            assert(bin(imm12hi, width=6) == '000000')
            assert(bin(opcode, width=7) == '1100011')
            assert(bin(arg_select, width=10) == '1100110000')
            if i < 2:
                assert(bin(funct3, width=3) == bin(i, width=3))
            else:
                assert(bin(funct3, width=3) == bin(i+2, width=3))

        # Test LUI and AUIPC Instructions
        lui_auipc_instr = ['lui', 'auipc']
        for i in range(len(lui_auipc_instr)):
            instruction.next = intbv(int(test_instruction[lui_auipc_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rd, width=5) == '00001')
            assert(bin(arg_select, width=10) == '0010000100')
            assert(bin(imm20, width=20) == '00000000000000000001')
            if i == 0:
                assert(bin(opcode, width=7) == '0110111')
            else:
                assert(bin(opcode, width=7) == '0010111')

        # Test Jump Instructions
        jump_instr = ['jalr', 'jal']
        for i in range(len(jump_instr)):
            instruction.next = intbv(int(test_instruction[jump_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rd, width=5) == '00001')
            if i == 0:
                assert(bin(imm12, width=12) == '000000000001')
                assert(bin(rs1, width=5) == '00001')
                assert(bin(arg_select, width=10) == '1010001000')
                assert(bin(opcode, width=7) == '1100111')
            else:
                assert(bin(imm20, width=20) == '10001100010000000001')
                assert(bin(arg_select, width=10) == '0010000100')
                assert(bin(opcode, width=7) == '1101111')

        # Test Addition and Logical immediate Instructions
        arith_logic_imm_instr = ['addi', 'slli', 'slti', 'sltiu', 'xori', 'srli', 'srai', 'ori', 'andi']
        for i in range(len(arith_logic_imm_instr)):
            instruction.next = intbv(int(test_instruction[arith_logic_imm_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rd, width=5) == '00001')
            assert(bin(rs1, width=5) == '00001')
            assert(bin(opcode, width=7) == '0010011')
            if i in [1,5,6]:
                assert(bin(arg_select, width=10) == '1010000010')
                assert(bin(shamt, width=5) == '00001')
            else:
                assert(bin(imm12, width=12) == '000000000001')
                assert(bin(arg_select, width=10) == '1010001000')

        # Test Addition and Logical Reg to Reg Instructions
        arith_logic_r2r_instr = ['add', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and', 'sub', 'sra']
        for i in range(len(arith_logic_r2r_instr)):
            instruction.next = intbv(int(test_instruction[arith_logic_r2r_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rd, width=5) == '00011')
            assert(bin(rs1, width=5) == '00001')
            assert(bin(rs2, width=5) == '00010')
            assert(bin(opcode, width=7) == '0110011')
            assert(bin(arg_select, width=10) == '1110000000')
            if i == 8:
                assert(bin(funct3, width=3) == bin(0, width=3))
            elif i == 9:
                assert(bin(funct3, width=3) == bin(5, width=3))
            else :
                assert(bin(funct3, width=3) == bin(i, width=3))

        # Test Load Instructions
        load_instr = ['lb', 'lh', 'lw', 'lbu', 'lhu']
        for i in range(len(load_instr)):
            instruction.next = intbv(int(test_instruction[load_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rd, width=5) == '00010')
            assert(bin(rs1, width=5) == '00001')
            assert(bin(imm12, width=12) == '000000000001')
            assert(bin(opcode, width=7) == '0000011')
            assert(bin(arg_select, width=10) == '1010001000')
            if i <= 2:
                assert(bin(funct3, width=3) == bin(i, width=3))
            else:
                assert(bin(funct3, width=3) == bin(i+1, width=3))

        # Test Store Instructions
        store_instr = ['sb', 'sh', 'sw']
        for i in range(len(store_instr)):
            instruction.next = intbv(int(test_instruction[store_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(rs1, width=5) == '00010')
            assert(bin(rs2, width=5) == '00001')
            assert(bin(imm12, width=12) == '000001000001')
            assert(bin(opcode, width=7) == '0100011')
            assert(bin(arg_select, width=10) == '1100001000')
            assert(bin(funct3, width=3) == bin(i, width=3))

        # Test System Instructions
        sys_instr = ['ecall', 'ebreak', 'rdcycle', 'rdcycleh', 'rdtime', 'rdtimeh', 'rdinstret', 'rdinstreth']
        for i in range(len(sys_instr)):
            instruction.next = intbv(int(test_instruction[sys_instr[i]],2))[32:]
            yield delay(10)
            assert(bin(opcode, width=7) == '1110011')
            if i in [0,1]:
                assert(bin(arg_select, width=10) == '0000001000')
                assert(bin(funct3, width=3) == bin(0, width=3))
                assert(bin(imm12, width=12) == bin(i, width=12))
            else:
                assert(bin(arg_select, width=10) == '0010001000')
                assert(bin(funct3, width=3) == bin(2, width=3))
                assert(bin(rd, width=5) == '00001')
                sys_imms = ['110000000000', '110010000000',
                            '110000000001', '110010000001',
                            '110000000010', '110010000010']
                assert(bin(imm12, width=12) == sys_imms[i-2])

    return output, stimulus

sim = Simulation(test_bench())
sim.run()
