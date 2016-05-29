import binascii
import json
from collections import defaultdict

rd      = 0 
rs1     = 0
rs2     = 0 
rs3     = 0
imm20   = 0
imm12   = 0
imm12lo = 0 
imm12hi = 0
shamtw  = 0
shamt   = 0
rm      = 0

a = 'opcode'
b = 'rd'
c = 'funct3'
d = 'rs1'
e = 'rs2'
f = 'imm'
g = 'funct7'

r_instruction = 'gggggggeeeeedddddcccbbbbbaaaaaaa'
i_instruction = 'ffffffffffffdddddcccbbbbbaaaaaaa'
s_instruction = 'fffffffeeeeedddddcccfffffaaaaaaa'
u_instruction = 'ffffffffffffffffffffbbbbbaaaaaaa'

def get_hex(binary_str):
	"""
	Returns the hexadecimal string literal for the given binary string 
	literal input

	:param str binary_str: Binary string to be converted to hex
	"""
	return hex(int(binary_str, base=2))

def get_int(binary_str):
	"""
	Returns the integer string literal for the given binary string 
	literal input

	:param str binary_str: Binary string to be converted to int
	"""
	return str(int(binary_str, base=2))

def get_output(debug=False, instr=None, rs1=None, rs2=None, imm12lo=None, imm12hi=None, rd=None, imm20=None):
	arg_list = [rs1, rs2, imm12lo, imm12hi, rd, imm20]
	arg_keys = ['rs1', 'rs2', 'imm12lo', 'imm12hi', 'rd', 'imm20']

	output_dict = defaultdict()
	output_dict['instr'] = instr

	for i in range(len(arg_list)):
		if arg_list[i] != None:
			output_dict[arg_keys[i]] = arg_list[i]

	if debug == True:
		print_dic(output_dict)

	return output_dict

instruction_list = lambda:defaultdict(instruction_list)
instruction_table = instruction_list()

# print(get_hex(family))
# print(int(funct3, base=10))

# RV32I

## Branch
instruction_table['0x18']['0'] = 'beq'
instruction_table['0x18']['1'] = 'bne'
instruction_table['0x18']['4'] = 'blt'
instruction_table['0x18']['5'] = 'bge'
instruction_table['0x18']['6'] = 'bltu'
instruction_table['0x18']['7'] = 'bgeu'
## Jump
instruction_table['0x19'] = 'jalr'
instruction_table['0x1b'] = 'jal'

def print_dic(dictionary):
	json_dict = json.dumps(dictionary, sort_keys = False, indent = 4)
	print json_dict

def decode(instruction, debug = False):
	family = instruction[-7:-2]

	if get_hex(family) == '0x18':
		funct3 = get_int(instruction[-15:-12])
		instruction_name = instruction_table[get_hex(family)][funct3]
		
		rs1 = instruction[-25:-20]
		rs2 = instruction[-20:-15]
		imm12hi = instruction[0] + instruction[-8] + instruction[-31:-27]
		imm12lo = instruction[-27:-25] + instruction[-12:-8]
		
		return get_output(instr=instruction_name ,rs1=rs1, rs2=rs2, imm12lo=imm12lo, imm12hi=imm12hi, debug=debug) 
	
	if get_hex(family) == '0x1b':
		instruction_name = instruction_table[get_hex(family)]
		
		rd = instruction[-12:-7]
		imm20 = instruction[0] + instruction[-20:-12] + instruction[-21] + instruction[-31:-21]

		return get_output(instr=instruction_name ,rd=rd, imm20=imm20, debug = debug)
	
instruction_table['0x0D'] = 'lui'
instruction_table['0x05'] = 'auipc'

## Arithmetic & Computation
instruction_table['0x04']['0'] = 'addi'
instruction_table['0x04']['1'] = 'slli'
instruction_table['0x04']['2'] = 'slti'
instruction_table['0x04']['3'] = 'sltiu'
instruction_table['0x04']['4'] = 'xori'
instruction_table['0x04']['5']['0'] = 'srli'
instruction_table['0x04']['5']['16'] = 'srai'
instruction_table['0x04']['6'] = 'ori'
instruction_table['0x04']['7'] = 'andi'

instruction_table['0x0C']['0']['0'] = 'add'
instruction_table['0x0C']['0']['32'] = 'sub'
instruction_table['0x0C']['1']['0'] = 'sll'
instruction_table['0x0C']['2']['0'] = 'slt'
instruction_table['0x0C']['3']['0'] = 'sltu'
instruction_table['0x0C']['4']['0'] = 'xor'
instruction_table['0x0C']['5']['0'] = 'srl'
instruction_table['0x0C']['5']['32'] = 'sra'
instruction_table['0x0C']['6']['0'] = 'or'
instruction_table['0x0C']['7']['0'] = 'and'

instruction_table['0x06']['0'] = 'addiw'
instruction_table['0x06']['0'] = 'slliw'
instruction_table['0x06']['5']['0'] = 'srliw'
instruction_table['0x06']['5']['32'] = 'sraiw'

instruction_table['0x00']['0'] = 'lb'
instruction_table['0x00']['1'] = 'lh'
instruction_table['0x00']['2'] = 'lw'
instruction_table['0x00']['3'] = 'ld'
instruction_table['0x00']['4'] = 'lbu'
instruction_table['0x00']['5'] = 'lhu'
instruction_table['0x00']['6'] = 'lwu'

instruction_table['0x08']['0'] = 'sb'
instruction_table['0x08']['1'] = 'sh'
instruction_table['0x08']['2'] = 'sw'
instruction_table['0x08']['3'] = 'sd'

instruction_table['0x03']['0'] = 'fence'
instruction_table['0x03']['1'] = 'fence.i'

#RV32M
instruction_table['0x0C']['0']['1'] = 'mul'
instruction_table['0x0C']['1']['1'] = 'mulh'
instruction_table['0x0C']['2']['1'] = 'mulhsu'
instruction_table['0x0C']['3']['1'] = 'mulhu'
instruction_table['0x0C']['4']['1'] = 'div'
instruction_table['0x0C']['5']['1'] = 'divu'
instruction_table['0x0C']['6']['1'] = 'rem'
instruction_table['0x0C']['7']['1'] = 'remu'

# RV64M
instruction_table['0x0E']['0']['1'] = 'mulw'
instruction_table['0x0E']['4']['1'] = 'divw'
instruction_table['0x0E']['5']['1'] = 'divuw'
instruction_table['0x0E']['6']['1'] = 'remw'
instruction_table['0x0E']['7']['1'] = 'remuw'

# RV32A
instruction_table['0x0B']['2']['0']['0'] = 'amoadd.w'
instruction_table['0x0B']['2']['0']['1'] = 'amoxor.w'
instruction_table['0x0B']['2']['0']['2'] = 'amoor.w'
instruction_table['0x0B']['2']['0']['3'] = 'amoand.w'
instruction_table['0x0B']['2']['0']['4'] = 'amomin.w'
instruction_table['0x0B']['2']['0']['5'] = 'amomax.w'
instruction_table['0x0B']['2']['0']['6'] = 'amominu.w'
instruction_table['0x0B']['2']['0']['7'] = 'amomaxu.w'
instruction_table['0x0B']['2']['1']['0'] = 'amoswap.w'
instruction_table['0x0B']['2']['2']['0'] = 'lr.w'
instruction_table['0x0B']['2']['3']['0'] = 'sc.w'

# RV64A
instruction_table['0x0B']['3']['0']['0'] = 'amoadd.d'
instruction_table['0x0B']['3']['0']['1'] = 'amoxor.d'
instruction_table['0x0B']['3']['0']['2'] = 'amoor.d'
instruction_table['0x0B']['3']['0']['3'] = 'amoand.d'
instruction_table['0x0B']['3']['0']['4'] = 'amomin.d'
instruction_table['0x0B']['3']['0']['5'] = 'amomax.d'
instruction_table['0x0B']['3']['0']['6'] = 'amominu.d'
instruction_table['0x0B']['3']['0']['7'] = 'amomaxu.d'
instruction_table['0x0B']['3']['1']['0'] = 'amoswap.d'
instruction_table['0x0B']['3']['2']['0'] = 'lr.d'
instruction_table['0x0B']['3']['3']['0'] = 'sc.d'

# SYSTEM
instruction_table['0x1C']['0']['000'] = 'ecall'
instruction_table['0x1C']['0']['001'] = 'ebreak'
instruction_table['0x1C']['0']['002'] = 'uret'
instruction_table['0x1C']['0']['102'] = 'sret'
instruction_table['0x1C']['0']['202'] = 'hret'
instruction_table['0x1C']['0']['302'] = 'mret'
instruction_table['0x1C']['0']['104'] = 'sfence.vm'
instruction_table['0x1C']['0']['105'] = 'wfi'

instruction_table['0x1C']['1'] = 'csrrw'
instruction_table['0x1C']['2'] = 'csrrs'
instruction_table['0x1C']['3'] = 'csrrc'
instruction_table['0x1C']['5'] = 'csrrwi'
instruction_table['0x1C']['6'] = 'csrrsi'
instruction_table['0x1C']['7'] = 'csrrci'

# F/D EXTENSIONS
instruction_table['0x14']['00']['0'] = 'fadd.s'
instruction_table['0x14']['01']['0'] = 'fsub.s'
instruction_table['0x14']['02']['0'] = 'fmul.s'
instruction_table['0x14']['03']['0'] = 'fdiv.s'
instruction_table['0x14']['0B']['0'] = 'fsqrt.s'
instruction_table['0x14']['04']['0']['0'] = 'fsgnj.s'
instruction_table['0x14']['04']['0']['1'] = 'fsgnjn.s'
instruction_table['0x14']['04']['0']['2'] = 'fsgnjx.s'
instruction_table['0x14']['05']['0']['0'] = 'fmin.s'
instruction_table['0x14']['05']['0']['1'] = 'fmax.s'

instruction_table['0x14']['00']['1'] = 'fadd.d'
instruction_table['0x14']['01']['1'] = 'fsub.d'
instruction_table['0x14']['02']['1'] = 'fmul.d'
instruction_table['0x14']['03']['1'] = 'fdiv.d'
instruction_table['0x14']['08']['0'] = 'fcvt.s.d'
instruction_table['0x14']['08']['1'] = 'fcvt.d.s'
instruction_table['0x14']['0B']['1'] = 'fsqrt.d'
instruction_table['0x14']['04']['1']['0'] = 'fsgnj.d'
instruction_table['0x14']['04']['1']['1'] = 'fsgnjn.d'
instruction_table['0x14']['04']['1']['2'] = 'fsgnjx.d'
instruction_table['0x14']['05']['1']['0'] = 'fmin.d'
instruction_table['0x14']['05']['1']['1'] = 'fmax.s'

instruction_table['0x14']['14']['0']['0'] = 'fle.s'
instruction_table['0x14']['14']['0']['1'] = 'flt.s'
instruction_table['0x14']['14']['0']['2'] = 'feq.s'

instruction_table['0x14']['14']['1']['0'] = 'fle.d'
instruction_table['0x14']['14']['1']['1'] = 'flt.d'
instruction_table['0x14']['14']['1']['2'] = 'feq.d'

instruction_table['0x14']['18']['0']['0'] = 'fcvt.w.s'
instruction_table['0x14']['18']['0']['1'] = 'fcvt.wu.s'
instruction_table['0x14']['18']['0']['2'] = 'fcvt.l.s'
instruction_table['0x14']['18']['0']['3'] = 'fcvt.lu.s'
instruction_table['0x14']['1C']['0']['0'] = 'fmv.x.s'
instruction_table['0x14']['1C']['0']['0'] = 'fclass.s'

instruction_table['0x14']['18']['1']['0'] = 'fcvt.w.d'
instruction_table['0x14']['18']['1']['1'] = 'fcvt.wu.d'
instruction_table['0x14']['18']['1']['2'] = 'fcvt.l.d'
instruction_table['0x14']['18']['1']['3'] = 'fcvt.lu.d'
instruction_table['0x14']['1C']['1']['0'] = 'fmv.x.d'
instruction_table['0x14']['1C']['1']['0'] = 'fclass.d'

instruction_table['0x01']['2'] = 'flw'
instruction_table['0x01']['3'] = 'fld'

instruction_table['0x09']['2'] = 'fsw'
instruction_table['0x09']['3'] = 'fsd'

instruction_table['0x10']['0'] = 'fmadd.s'
instruction_table['0x11']['0'] = 'fmsub.s'
instruction_table['0x12']['0'] = 'fnmsub.s'
instruction_table['0x13']['0'] = 'fnmadd.s'

instruction_table['0x10']['1'] = 'fmadd.d'
instruction_table['0x11']['1'] = 'fmsub.d'
instruction_table['0x12']['1'] = 'fnmsub.d'
instruction_table['0x13']['1'] = 'fnmadd.d'

# print(r_instruction[-7:-2])
# print(instruction_table)



# if instruction[-7:-2] == '11000':
# 	if instruction[-14:-12] == ''	