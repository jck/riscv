import json
import binascii
from collections import defaultdict

def get_hex(binary_str):
	"""
	Returns the hexadecimal string literal for the given binary string 
	literal input

	:param str binary_str: Binary string to be converted to hex
	"""

	return "{0:#0{1}x}".format(int(binary_str, base=2),4)

def get_int(binary_str):
	"""
	Returns the integer string literal for the given binary string 
	literal input

	:param str binary_str: Binary string to be converted to int
	"""
	return str(int(binary_str, base=2))

def get_output(debug=False, instr=None, rs1=None, rs2=None, imm12lo=None, imm12hi=None, rd=None, imm20=None, imm12=None, shamt=None, shamtw=None, rm=None):
	"""	
	Wraps the non-empty arguments and the instruction name into a dictionary with
	arguments as keys and vals as values

	:param str instr: Name of the instruction
	:param str rs1: Source register 1
	:param str rs2: Source register 2
	:param str rd: Destination register
	:param str rm: Extended register
	:param str imm12lo: Lower 6 bits of Immediate 12
	:param str imm12hi: Higher 6 bits of Immediate 12
	:param str imm12: Immediate 12
	:param str imm20: Immediate 20
	:param str shamt: Shift args
	:param str shamtw: Shift args
	"""
	arg_list = [rs1, rs2, imm12lo, imm12hi, rd, imm20, imm12, shamt, shamtw, rm]
	arg_keys = ['rs1', 'rs2', 'imm12lo', 'imm12hi', 'rd', 'imm20', 'imm12', 'shamt', 'shamtw', 'rm']

	output_dict = defaultdict()
	output_dict['instr'] = instr

	for i in range(len(arg_list)):
		if arg_list[i] != None:
			output_dict[arg_keys[i]] = arg_list[i]

	if debug == True:
		print_dic(output_dict)

	return output_dict

def print_dic(dictionary):
	"""
	Utility function to print the output dictionary for 
	debug purposes

	:param dictionary dictionary: Dictionary object of the decoded instruction
	"""
	json_dict = json.dumps(dictionary, sort_keys = False, indent = 4)
	print json_dict

instruction_list = lambda:defaultdict(instruction_list)
instruction_table = instruction_list()

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
## Upper Immediate
instruction_table['0x0d'] = 'lui'
instruction_table['0x05'] = 'auipc'
## Arithmetic & Computation Immediate
instruction_table['0x04']['0'] = 'addi'
instruction_table['0x04']['1'] = 'slli'
instruction_table['0x04']['2'] = 'slti'
instruction_table['0x04']['3'] = 'sltiu'
instruction_table['0x04']['4'] = 'xori'
instruction_table['0x04']['5']['0'] = 'srli'
instruction_table['0x04']['5']['16'] = 'srai'
instruction_table['0x04']['6'] = 'ori'
instruction_table['0x04']['7'] = 'andi'
## Arithmetic & Computation Register to Register
instruction_table['0x0c']['0']['0'] = 'add'
instruction_table['0x0c']['0']['32'] = 'sub'
instruction_table['0x0c']['1']['0'] = 'sll'
instruction_table['0x0c']['2']['0'] = 'slt'
instruction_table['0x0c']['3']['0'] = 'sltu'
instruction_table['0x0c']['4']['0'] = 'xor'
instruction_table['0x0c']['5']['0'] = 'srl'
instruction_table['0x0c']['5']['32'] = 'sra'
instruction_table['0x0c']['6']['0'] = 'or'
instruction_table['0x0c']['7']['0'] = 'and'
## Extended Arithmetic & Computation Immediate
instruction_table['0x06']['0'] = 'addiw'
instruction_table['0x06']['1'] = 'slliw'
instruction_table['0x06']['5']['0'] = 'srliw'
instruction_table['0x06']['5']['16'] = 'sraiw'
## Extended Arithmetic & Computation Register to Register
instruction_table['0x0e']['0']['0'] = 'addw'
instruction_table['0x0e']['0']['32'] = 'subw'
instruction_table['0x0e']['1']['0'] = 'sllw'
instruction_table['0x0e']['5']['0'] = 'srlw'
instruction_table['0x0e']['5']['32'] = 'sraw'
## Load
instruction_table['0x00']['0'] = 'lb'
instruction_table['0x00']['1'] = 'lh'
instruction_table['0x00']['2'] = 'lw'
instruction_table['0x00']['3'] = 'ld'
instruction_table['0x00']['4'] = 'lbu'
instruction_table['0x00']['5'] = 'lhu'
instruction_table['0x00']['6'] = 'lwu'
## Store
instruction_table['0x08']['0'] = 'sb'
instruction_table['0x08']['1'] = 'sh'
instruction_table['0x08']['2'] = 'sw'
instruction_table['0x08']['3'] = 'sd'
## Fence
instruction_table['0x03']['0'] = 'fence'
instruction_table['0x03']['1'] = 'fence.i'
# RV32M
instruction_table['0x0c']['0']['1'] = 'mul'
instruction_table['0x0c']['1']['1'] = 'mulh'
instruction_table['0x0c']['2']['1'] = 'mulhsu'
instruction_table['0x0c']['3']['1'] = 'mulhu'
instruction_table['0x0c']['4']['1'] = 'div'
instruction_table['0x0c']['5']['1'] = 'divu'
instruction_table['0x0c']['6']['1'] = 'rem'
instruction_table['0x0c']['7']['1'] = 'remu'
# RV64M
instruction_table['0x0e']['0']['1'] = 'mulw'
instruction_table['0x0e']['4']['1'] = 'divw'
instruction_table['0x0e']['5']['1'] = 'divuw'
instruction_table['0x0e']['6']['1'] = 'remw'
instruction_table['0x0e']['7']['1'] = 'remuw'

# RV32A
instruction_table['0x0b']['2']['0']['0'] = 'amoadd.w'
instruction_table['0x0b']['2']['0']['1'] = 'amoxor.w'
instruction_table['0x0b']['2']['0']['2'] = 'amoor.w'
instruction_table['0x0b']['2']['0']['3'] = 'amoand.w'
instruction_table['0x0b']['2']['0']['4'] = 'amomin.w'
instruction_table['0x0b']['2']['0']['5'] = 'amomax.w'
instruction_table['0x0b']['2']['0']['6'] = 'amominu.w'
instruction_table['0x0b']['2']['0']['7'] = 'amomaxu.w'
instruction_table['0x0b']['2']['1']['0'] = 'amoswap.w'
instruction_table['0x0b']['2']['2']['0'] = 'lr.w'
instruction_table['0x0b']['2']['3']['0'] = 'sc.w'
# RV64A
instruction_table['0x0b']['3']['0']['0'] = 'amoadd.d'
instruction_table['0x0b']['3']['0']['1'] = 'amoxor.d'
instruction_table['0x0b']['3']['0']['2'] = 'amoor.d'
instruction_table['0x0b']['3']['0']['3'] = 'amoand.d'
instruction_table['0x0b']['3']['0']['4'] = 'amomin.d'
instruction_table['0x0b']['3']['0']['5'] = 'amomax.d'
instruction_table['0x0b']['3']['0']['6'] = 'amominu.d'
instruction_table['0x0b']['3']['0']['7'] = 'amomaxu.d'
instruction_table['0x0b']['3']['1']['0'] = 'amoswap.d'
instruction_table['0x0b']['3']['2']['0'] = 'lr.d'
instruction_table['0x0b']['3']['3']['0'] = 'sc.d'
# F/D EXTENSIONS
instruction_table['0x14']['0']['0'] = 'fadd.s'
instruction_table['0x14']['1']['0'] = 'fsub.s'
instruction_table['0x14']['2']['0'] = 'fmul.s'
instruction_table['0x14']['3']['0'] = 'fdiv.s'
instruction_table['0x14']['11']['0'] = 'fsqrt.s'
instruction_table['0x14']['4']['0']['0'] = 'fsgnj.s'
instruction_table['0x14']['4']['0']['1'] = 'fsgnjn.s'
instruction_table['0x14']['4']['0']['2'] = 'fsgnjx.s'
instruction_table['0x14']['5']['0']['0'] = 'fmin.s'
instruction_table['0x14']['5']['0']['1'] = 'fmax.s'

instruction_table['0x14']['0']['1'] = 'fadd.d'
instruction_table['0x14']['1']['1'] = 'fsub.d'
instruction_table['0x14']['2']['1'] = 'fmul.d'
instruction_table['0x14']['3']['1'] = 'fdiv.d'
instruction_table['0x14']['8']['0'] = 'fcvt.s.d'
instruction_table['0x14']['8']['1'] = 'fcvt.d.s'
instruction_table['0x14']['11']['1'] = 'fsqrt.d'
instruction_table['0x14']['4']['1']['0'] = 'fsgnj.d'
instruction_table['0x14']['4']['1']['1'] = 'fsgnjn.d'
instruction_table['0x14']['4']['1']['2'] = 'fsgnjx.d'
instruction_table['0x14']['5']['1']['0'] = 'fmin.d'
instruction_table['0x14']['5']['1']['1'] = 'fmax.s'

instruction_table['0x14']['20']['0']['0'] = 'fle.s'
instruction_table['0x14']['20']['0']['1'] = 'flt.s'
instruction_table['0x14']['20']['0']['2'] = 'feq.s'

instruction_table['0x14']['20']['1']['0'] = 'fle.d'
instruction_table['0x14']['20']['1']['1'] = 'flt.d'
instruction_table['0x14']['20']['1']['2'] = 'feq.d'

instruction_table['0x14']['24']['0']['0'] = 'fcvt.w.s'
instruction_table['0x14']['24']['0']['1'] = 'fcvt.wu.s'
instruction_table['0x14']['24']['0']['2'] = 'fcvt.l.s'
instruction_table['0x14']['24']['0']['3'] = 'fcvt.lu.s'
instruction_table['0x14']['28']['0']['0']['0'] = 'fmv.x.s'
instruction_table['0x14']['28']['0']['0']['1'] = 'fclass.s'

instruction_table['0x14']['24']['1']['0'] = 'fcvt.w.d'
instruction_table['0x14']['24']['1']['1'] = 'fcvt.wu.d'
instruction_table['0x14']['24']['1']['2'] = 'fcvt.l.d'
instruction_table['0x14']['24']['1']['3'] = 'fcvt.lu.d'
instruction_table['0x14']['28']['1']['0']['0'] = 'fmv.x.d'
instruction_table['0x14']['28']['1']['0']['1'] = 'fclass.d'

elif get_hex(family) == '0x14':
		slice_5 = get_int(instruction[:5])
		slice_2 = get_int(instruction[-27:-25])
		
		rs2 = instruction[-25:-20]
		rs1 = instruction[-20:-15]
		rd = instruction[-12:-7]

		if slice_5 in ['4','5','20']:
			funct3 = get_int(instruction[-15:-12])
			instruction_name = instruction_table[get_hex(family)][slice_5][slice_2][funct3]
			return get_output(instr=instruction_name, rs1=rs1, rs2=rs2, rd=rd, debug=debug)
		elif slice_5 == '8':
			instruction_name = instruction_table[get_hex(family)][slice_5][get_int(rs2)]
			rm = instruction[-15:-12]
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, rm=rm, debug=debug)
		elif slice_5 == '24':
			instruction_name = instruction_table[get_hex(family)][slice_5][slice_2][get_int(rs2)]
			rm = instruction[-15:-12]
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, rm=rm, debug=debug)
		elif slice_5 == '28':
			funct3 = get_int(instruction[-15:-12])
			instruction_name = instruction_table[get_hex(family)][slice_5][slice_2][get_int(rs2)][funct3]
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, debug=debug)	
		else : 		
			instruction_name = instruction_table[get_hex(family)][slice_5][slice_2]
			rm = instruction[-15:-12]
			return get_output(instr=instruction_name, rs1=rs1, rs2=rs2, rd=rd, rm=rm, debug=debug)

def decode(instruction, debug = False):
	"""	
	Decodes the binary instruction string input and returns a 
	dictionary with the instruction name and arguments as keys and 
	their vals as values 

	:param str instruction: Binary string that contains the encoded instruction
	:param str debug: Flag to print decoded dictionary (if true).
	"""

	family = instruction[-7:-2]

	if get_hex(family) == '0x18':
		funct3 = get_int(instruction[-15:-12])
		instruction_name = instruction_table[get_hex(family)][funct3]
		
		rs1 = instruction[-25:-20]
		rs2 = instruction[-20:-15]
		imm12hi = instruction[0] + instruction[-8] + instruction[-31:-27]
		imm12lo = instruction[-27:-25] + instruction[-12:-8]
		
		return get_output(instr=instruction_name ,rs1=rs1, rs2=rs2, imm12lo=imm12lo, imm12hi=imm12hi, debug=debug) 
	
	elif get_hex(family) == '0x1b':
		instruction_name = instruction_table[get_hex(family)]
		
		rd = instruction[-12:-7]
		imm20 = instruction[0] + instruction[-20:-12] + instruction[-21] + instruction[-31:-21]

		return get_output(instr=instruction_name ,rd=rd, imm20=imm20, debug = debug)

	elif get_hex(family) == '0x19':
		instruction_name = instruction_table[get_hex(family)]
		
		rs1 = instruction[-20:-15]
		rd = instruction[-12:-7]
		imm12 = instruction[:12]

		return get_output(instr=instruction_name ,rd=rd, imm12=imm12, rs1=rs1,debug = debug)
	
	elif get_hex(family) == '0x0d' or get_hex(family) == '0x05':
		instruction_name = instruction_table[get_hex(family)]
		
		imm20 = instruction[:20]
		rd = instruction[-12:-7]

		return get_output(instr=instruction_name ,rd=rd, imm20=imm20, debug = debug)

	elif get_hex(family) == '0x04':
		funct3 = get_int(instruction[-15:-12])

		if funct3 in ['0','2','3','4','6','7']:
			instruction_name = instruction_table[get_hex(family)][funct3]
			rd = instruction[-12:-7]
			rs1 = instruction[-20:-15]
			imm12 = instruction[:12]
			return get_output(instr=instruction_name ,rs1=rs1, rd=rd, imm12=imm12, debug=debug)

		elif funct3 in ['1','5']:
			if funct3 == '5':
				slice_5 = str(get_int(instruction[:7]))
				instruction_name = instruction_table[get_hex(family)][funct3][slice_5]
			else :
				instruction_name = instruction_table[get_hex(family)][funct3]	
			rd = instruction[-12:-7]
			rs1 = instruction[-20:-15]
			shamt = instruction[-25:-20]
			return get_output(instr=instruction_name ,rs1=rs1, rd=rd, shamt=shamt, debug=debug)

	elif get_hex(family) == '0x0c':
		funct3 = get_int(instruction[-15:-12])
		
		slice_7 = get_int(instruction[:7])
		instruction_name = instruction_table[get_hex(family)][funct3][slice_7]
		
		rd = instruction[-12:-7]
		rs1 = instruction[-20:-15]
		rs2 = instruction[-25:-20]
		return get_output(instr=instruction_name ,rs1=rs1, rs2=rs2, rd=rd, debug=debug)

	elif get_hex(family) == '0x06':
		funct3 = get_int(instruction[-15:-12])
		
		rs1 = instruction[-20:-15]
		rd = instruction[-12:-7]
		if funct3 == '0':
			imm12 = instruction[:12]
			instruction_name = instruction_table[get_hex(family)][funct3]
			return get_output(instr=instruction_name ,rs1=rs1, rd=rd, imm12=imm12, debug=debug) 
		
		elif funct3 == '1':
			shamtw = instruction[-25:-20]
			instruction_name = instruction_table[get_hex(family)][funct3]
			return get_output(instr=instruction_name ,rs1=rs1, rd=rd, shamtw=shamtw, debug=debug) 
		
		else:
			shamtw = instruction[-25:-20]
			slice_6 = get_int(instruction[:6])
			instruction_name = instruction_table[get_hex(family)][funct3][slice_6]
			return get_output(instr=instruction_name ,rs1=rs1, rd=rd, shamtw=shamtw, debug=debug) 
	
	elif get_hex(family) == '0x0e':
		funct3 = get_int(instruction[-15:-12])
		
		slice_7 = get_int(instruction[:7])
		instruction_name = instruction_table[get_hex(family)][funct3][slice_7]
		
		rd = instruction[-12:-7]
		rs1 = instruction[-20:-15]
		rs2 = instruction[-25:-20]
		return get_output(instr=instruction_name ,rs1=rs1, rs2=rs2, rd=rd, debug=debug)

	elif get_hex(family) == '0x00':
		funct3 = get_int(instruction[-15:-12])
		instruction_name = instruction_table[get_hex(family)][funct3]
		
		rd = instruction[-12:-7]
		rs1 = instruction[-25:-20]
		imm12 = instruction[:12]
		return get_output(instr=instruction_name ,rs1=rs1, imm12=imm12, rd=rd, debug=debug)	

	elif get_hex(family) == '0x08':
		funct3 = get_int(instruction[-15:-12])
		instruction_name = instruction_table[get_hex(family)][funct3]
		
		rs1 = instruction[-20:-15]
		rs2 = instruction[-25:-20]
		imm12lo = instruction[6] + instruction[-12:-7]
		imm12hi = instruction[:6]
		return get_output(instr=instruction_name ,rs1=rs1, rs2=rs2, imm12lo=imm12lo, imm12hi=imm12hi, debug=debug)

	elif get_hex(family) == '0x03':
		funct3 = get_int(instruction[-15:-12])
		instruction_name = instruction_table[get_hex(family)][funct3]
		rs1 = instruction[-20:-15]
		rd = instruction[-12:-7]
		
		if funct3 == '0':
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, debug=debug)
		
		else:
			imm12 = instruction[:12]
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, imm12=imm12, debug=debug)

	elif get_hex(family) == '0x0c' or get_hex(family) == '0x0e':
		funct3 = get_int(instruction[-15:-12])

		slice_7 = get_int(instruction[:7])
		instruction_name = instruction_table[get_hex(family)][funct3][slice_7]
		
		rs1 = instruction[-20:-15]
		rs2 = instruction[-25:-20]
		rd = instruction[-12:-7]
		
		return get_output(instr=instruction_name, rs1=rs1, rd=rd, rs2=rs2, debug=debug)
	
	elif get_hex(family) == '0x0b':
		funct3 = get_int(instruction[-15:-12])

		slice_3 = get_int(instruction[:3])
		slice_2 = get_int(instruction[-29:-27])
		
		instruction_name = instruction_table[get_hex(family)][funct3][slice_2][slice_3]
		
		rs1 = instruction[-20:-15]
		rd = instruction[-12:-7]

		if slice_2 != '2':
			rs2 = instruction[-25:-20]
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, rs2=rs2, debug=debug)
		else : 
			return get_output(instr=instruction_name, rs1=rs1, rd=rd, debug=debug)

	

	else:
		print("Instruction does not match any known instruction")
		print("Family :" + family)





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