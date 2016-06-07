import os
import sys
import unittest

lib_path = os.path.abspath(os.path.join('..','riscv'))
sys.path.append(lib_path)

from riscv import decoder
from collections import defaultdict
from test_instructions import test_instruction


class TestDecoder(unittest.TestCase):

	def test_floatd_instructions(self):
		instructions = ['fcvt.wu.d', 'fcvt.d.w', 'fmv.s.x', 'fcvt.s.wu', 'fmv.x.s', 'fcvt.s.l', 'fcvt.s.lu', 'fcvt.w.s', 'fcvt.l.s', 'fcvt.lu.s', 'fclass.s', 'fmv.x.d', 'fcvt.s.w', 'fcvt.d.lu', 'fcvt.d.wu', 'fcvt.wu.s', 'fclass.d', 'fcvt.lu.d', 'fcvt.l.d', 'fcvt.w.d', 'fcvt.d.l']

		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rd'] = '00011'
			ground_truth['rs1'] = '00001'
			
			if not instr in ['fmv.x.s', 'fmv.x.d', 'fclass.s', 'fclass.d', 'fmv.d.x', 'fmv.s.x']:
				ground_truth['rm'] = '010'
				
			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_system_instructions(self):
		instructions = ['ecall', 'ebreak', 'uret', 'sret', 'hret', 'mret', 'sfence.vm', 'wfi', 'csrrw', 'csrrs', 'csrrc', 'csrrwi', 'csrrsi', 'csrrci']		
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			
			if instr[:2] == 'cs':
				ground_truth['rd'] = '00010'
				ground_truth['rs1'] = '00001'
				ground_truth['imm12'] = '000000000001'

			elif instr == 'sfence.vm':
				ground_truth['rs1'] = '00001'
				
			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_float_instructions(self):
		instructions = ['fadd.s', 'fsub.s', 'fmul.s', 'fdiv.s', 'fsgnj.s', 'fsgnjn.s', 'fsgnjx.s', 'fmin.s', 'fmax.s', 'fsqrt.s']		
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['rd'] = '00100'
			
			if not instr in ['fsgnj.s', 'fsgnjn.s', 'fsgnjx.s', 'fmin.s', 'fmax.s']:
				ground_truth['rm'] = '011'
			if instr == 'fsqrt.s':
				ground_truth['rs2'] = '00000'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])	

	def test_atomic_d_instructions(self):
		instructions = ['amoadd.d', 'amoxor.d', 'amoor.d', 'amoand.d', 'amomax.d', 'amomin.d', 'amomaxu.d', 'amominu.d', 'amoswap.d', 'lr.d', 'sc.d']		
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rd'] = '00011'
			
			if instr != 'lr.d':
				ground_truth['rs2'] = '00010'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_atomic_instructions(self):
		instructions = ['amoadd.w', 'amoxor.w', 'amoor.w', 'amoand.w', 'amomax.w', 'amomin.w', 'amomaxu.w', 'amominu.w', 'amoswap.w', 'lr.w', 'sc.w']		
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rd'] = '00011'
			
			if instr != 'lr.w':
				ground_truth['rs2'] = '00010'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

	def test_divw_multw_instructions(self):
		instructions = ['mulw', 'divw', 'divuw', 'remw', 'remuw']
		
		for instr in instructions:
			ground_truth = defaultdict()
			ground_truth['instr'] = instr		
			ground_truth['rs1'] = '00001'
			ground_truth['rs2'] = '00010'
			ground_truth['rd'] = '00011'

			result = decoder.decode(test_instruction[instr], debug=False)

			for key in ground_truth:
				self.assertEqual(result[key],ground_truth[key])

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
