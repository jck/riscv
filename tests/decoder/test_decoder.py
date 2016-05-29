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

class TestDecoder(unittest.TestCase):

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