import os
import sys
import unittest

from collections import defaultdict

lib_path = os.path.abspath(os.path.join('..', '..', '..', 'riscv'))
sys.path.append(lib_path)

from riscv import decoder

test_instruction = defaultdict()
test_instruction['beq']  = '1' + '000000' + '00001' + '00010' + '000' + '0000' + '1' + '11000' + '11'
test_instruction['bne']  = '1' + '000000' + '00001' + '00010' + '001' + '0000' + '1' + '11000' + '11'
test_instruction['blt']  = '1' + '000000' + '00001' + '00010' + '100' + '0000' + '1' + '11000' + '11'
test_instruction['bge']  = '1' + '000000' + '00001' + '00010' + '101' + '0000' + '1' + '11000' + '11'
test_instruction['bltu'] = '1' + '000000' + '00001' + '00010' + '110' + '0000' + '1' + '11000' + '11'
test_instruction['bgeu'] = '1' + '000000' + '00001' + '00010' + '111' + '0000' + '1' + '11000' + '11'

test_instruction['jal'] = '1' + '0000000001' + '1' + '00011000' + '00001' + '11011' + '11'
test_instruction['jalr'] = '000000000001' + '00001' + '000' + '00001' + '11001' + '11'

test_instruction['lui'] = '00000000000000000001' + '00001' + '01101' + '11'
test_instruction['auipc'] = '00000000000000000001' + '00001' + '00101' + '11'

test_instruction['addi'] = '000000000001' + '00001' + '000' + '00001' + '00100' + '11' 
test_instruction['slli'] = '0000000' + '00001' + '00001' + '001' + '00001' + '00100' + '11'
test_instruction['slti'] = '000000000001' + '00001' + '010' + '00001' + '00100' + '11'
test_instruction['sltiu'] = '000000000001' + '00001' + '011' + '00001' + '00100' + '11'
test_instruction['xori'] = '000000000001' + '00001' + '100' + '00001' + '00100' + '11'
test_instruction['srli'] = '0000000' + '00001' + '00001' + '101' + '00001' + '00100' + '11'
test_instruction['srai'] = '0010000' + '00001' + '00001' + '101' + '00001' + '00100' + '11'
test_instruction['ori'] = '000000000001' + '00001' + '110' + '00001' + '00100' + '11'
test_instruction['andi'] = '000000000001' + '00001' + '111' + '00001' + '00100' + '11'

test_instruction['add'] = '0000000' + '00010' + '00001' + '000' + '00011' + '01100' + '11' 
test_instruction['sub'] = '0100000' + '00010' + '00001' + '000' + '00011' + '01100' + '11' 
test_instruction['sll'] = '0000000' + '00010' + '00001' + '001' + '00011' + '01100' + '11' 
test_instruction['slt'] = '0000000' + '00010' + '00001' + '010' + '00011' + '01100' + '11' 
test_instruction['sltu'] = '0000000' + '00010' + '00001' + '011' + '00011' + '01100' + '11' 
test_instruction['xor'] = '0000000' + '00010' + '00001' + '100' + '00011' + '01100' + '11' 
test_instruction['srl'] = '0000000' + '00010' + '00001' + '101' + '00011' + '01100' + '11' 
test_instruction['sra'] = '0100000' + '00010' + '00001' + '101' + '00011' + '01100' + '11' 
test_instruction['or'] = '0000000' + '00010' + '00001' + '110' + '00011' + '01100' + '11' 
test_instruction['and'] = '0000000' + '00010' + '00001' + '111' + '00011' + '01100' + '11' 

test_instruction['addiw'] = '000000000001' + '00001' + '000' + '00001' + '00110' + '11'
test_instruction['slliw'] = '000000' + '0' + '00001' + '00001' + '001' + '00001' + '00110' + '11'
test_instruction['srliw'] = '000000' + '0' + '00001' + '00001' + '101' + '00001' + '00110' + '11'
test_instruction['sraiw'] = '010000' + '0' + '00001' + '00001' + '101' + '00001' + '00110' + '11'

test_instruction['addw'] = '0000000' + '00010' + '00001' + '000' + '00011' + '01110' + '11' 
test_instruction['subw'] = '0100000' + '00010' + '00001' + '000' + '00011' + '01110' + '11' 
test_instruction['sllw'] = '0000000' + '00010' + '00001' + '001' + '00011' + '01110' + '11' 
test_instruction['srlw'] = '0000000' + '00010' + '00001' + '101' + '00011' + '01110' + '11' 
test_instruction['sraw'] = '0100000' + '00010' + '00001' + '101' + '00011' + '01110' + '11' 

test_instruction['lb'] = '000000000001' + '00001' + '000' + '00010' + '00000' + '11' 
test_instruction['lh'] = '000000000001' + '00001' + '001' + '00010' + '00000' + '11' 
test_instruction['lw'] = '000000000001' + '00001' + '010' + '00010' + '00000' + '11' 
test_instruction['ld'] = '000000000001' + '00001' + '011' + '00010' + '00000' + '11' 
test_instruction['lbu'] = '000000000001' + '00001' + '100' + '00010' + '00000' + '11' 
test_instruction['lhu'] = '000000000001' + '00001' + '101' + '00010' + '00000' + '11' 
test_instruction['lwu'] = '000000000001' + '00001' + '110' + '00010' + '00000' + '11' 

test_instruction['sb'] = '0000010' + '00001' + '00010' + '000' + '00001' + '01000' + '11' 
test_instruction['sh'] = '0000010' + '00001' + '00010' + '001' + '00001' + '01000' + '11' 
test_instruction['sw'] = '0000010' + '00001' + '00010' + '010' + '00001' + '01000' + '11' 
test_instruction['sd'] = '0000010' + '00001' + '00010' + '011' + '00001' + '01000' + '11' 

test_instruction['fence'] = '0000' + '11111111' + '00001' + '000' + '00010' + '00011' + '11' 
test_instruction['fence.i'] = '000000000001' + '00001' + '001' + '00010' + '00011' + '11' 

test_instruction['mul'] = '0000001' + '00010' + '00001' + '000' + '00011' +'01100' + '11'
test_instruction['mulh'] = '0000001' + '00010' + '00001' + '001' + '00011' +'01100' + '11'
test_instruction['mulhsu'] = '0000001' + '00010' + '00001' + '010' + '00011' +'01100' + '11'
test_instruction['mulhu'] = '0000001' + '00010' + '00001' + '011' + '00011' +'01100' + '11'
test_instruction['div'] = '0000001' + '00010' + '00001' + '100' + '00011' +'01100' + '11'
test_instruction['divu'] = '0000001' + '00010' + '00001' + '101' + '00011' +'01100' + '11'
test_instruction['rem'] = '0000001' + '00010' + '00001' + '110' + '00011' +'01100' + '11'
test_instruction['remu'] = '0000001' + '00010' + '00001' + '111' + '00011' +'01100' + '11'


class TestDecoder(unittest.TestCase):

	def test_div_mult_instructions(self):
		instructions = ['mul', 'mulh', 'mulhsu', 'mulhu', 'div', 'divu', 'rem', 'remu']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['rd'] = '00011'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_fence_instructions(self):
		instructions = ['fence', 'fence.i']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rd'] = '00010'
			ground_truth['rs1'] = '00001'

			if instr == 'fence.i':
				ground_truth['imm12'] = '000000000001'

			result = decoder.decode(test_instruction[instr], debug=False)

	def test_store_instructions(self):
		instructions = ['sb', 'sh', 'sw', 'sd']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['imm12lo'] = '000001'
			ground_truth['imm12hi'] = '000001'

			result = decoder.decode(test_instruction[instr], debug=False)

	def test_load_instructions(self):
		instructions = ['lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rd'] = '00010'
			ground_truth['imm12'] = '000000000001'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_arithmetic_regw_instructions(self):
		instructions = ['addw', 'subw', 'sllw', 'srlw', 'sraw']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['rd'] = '00011'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_arithmetic_immw_instructions(self):
		instructions = ['addiw', 'slliw', 'srliw', 'sraiw']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rd'] = '00001'
			
			if instr == 'addiw':
				ground_truth['imm12'] = '000000000001'
			else:
				ground_truth['shamtw'] = '00001'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_arithmetic_reg_instructions(self):
		instructions = ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'sra', 'or', 'and']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['rd'] = '00011'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_arithmetic_imm_instructions(self):
		instructions = ['addi', 'slli', 'slti', 'sltiu', 'xori', 'srli', 'srai', 'ori', 'andi']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rd'] = '00001'
			ground_truth['rs1'] = '00001'

			if instr in ['slli', 'srli', 'srai']:
				ground_truth['shamt'] = '00001'
			else:
				ground_truth['imm12'] = '000000000001'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_upper_immediate_instructions(self):
		instructions = ['lui', 'auipc']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rd'] = '00001'
			ground_truth['imm20'] = '00000000000000000001'
			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])
	
	def test_branch_instructions(self):
		instructions = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['imm12hi'] = '110000'
			ground_truth['imm12lo'] = '000000'
			
			result = decoder.decode(test_instruction[instr], debug=False)
			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])
	
	def test_jump_instrunctions(self):
		instructions = ['jal', 'jalr']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr
			if instr == 'jal':
				ground_truth['rd'] = '00001'
				ground_truth['imm20'] = '10001100010000000001'
			else:
				ground_truth['rd'] = '00001'
				ground_truth['rs1'] = '00001'
				ground_truth['imm12'] = '000000000001'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])


if __name__ == '__main__':
	unittest.main(verbosity=2)