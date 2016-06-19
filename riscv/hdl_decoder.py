from decoder import get_hex, get_int
from instruction_table import instruction_table
from myhdl import always_comb, intbv, Signal, Simulation, delay, bin

def get_arg_select(arg_list):
	"""
	Utility function to generate the arg_select signal depending upon the 
	arguments present in the instruction

	:param list arg_list: List of arguments passed by the instruction
    :param Signal arg_select: 10 bit active low argument select signal 
	"""

	argument_list = ['rs1', 'rs2', 'rd', 'rm', 'imm12lo', 'imm12hi', 'imm12', 'imm20', 'shamt', 'shamtw']
	arg_select_list = ['0' for i in range(len(argument_list))]
	
	for i in range(len(arg_list)):
		for j in range(len(argument_list)):
			if arg_list[i] == argument_list[j]:
				arg_select_list[j] = '1'
			elif arg_select_list[j] == '1':
				pass
			else:
				arg_select_list[j] = '0'

	arg_select_string = ''.join(arg_select_list)
	return Signal(intbv(int(arg_select_string,2)))

def get_arg(instruction, argument):
	"""
	Utiity function to return commonly used slices/arguments
	of instructions in hexadecimal or binary formats
	
	:param Signal instruction: Input instruction 
	:param str argument_name: the name of the argument to be extracted
	"""
	if argument == 'family_code':
		return get_hex(instruction[7:2])
	elif argument == 'rs1':
		return instruction[20:15]
	elif argument == 'rs2':
		return instruction[25:20]
	elif argument == 'imm12lo':
		return intbv(int(bin(instruction[31]) + bin(instruction[7]) + bin(instruction[31:27], width=4),2))
	elif argument == 'imm12hi':
		return intbv(int(bin(instruction[27:25],width=2) + bin(instruction[12:8],width=4) ,2))
	elif argument == 'instruction_id':
		return instruction[15:12]


def hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw):
    """
    HDL decoder module to decode instructions from
    RISC-V ISA. 

    :param Signal instruction: Instruction to be decoded
    
    :param Signal arg_select: 10 bit active low argument select signal 
 	:param Signal rs1: Source register 1
	:param Signal rs2: Source register 2
	:param Signal rd: Destination register
	:param Signal rm: Extended register
	:param Signal imm12lo: Lower 6 bits of Immediate 12
	:param Signal imm12hi: Higher 6 bits of Immediate 12
	:param Signal imm12: Immediate 12
	:param Signal imm20: Immediate 20
	:param Signal shamt: Shift args
	:param Signal shamtw: Shift args
    """
    @always_comb
    def decoder_output():
        instruction_family = get_arg(instruction, 'family_code')
        
        if instruction_family == '0x1b':
        		
        	instruction_id = get_arg(instruction, 'instruction_id')

        	rs1.next = get_arg(instruction, 'rs1')
        	rs2.next = get_arg(instruction, 'rs2')
        	imm12lo.next = get_arg(instruction, 'imm12lo')
        	imm12hi.next = get_arg(instruction, 'imm12hi')

        	arg_list = ['rs1', 'rs2', 'imm12lo', 'imm12hi']
        	arg_select.next = get_arg_select(arg_list)

        return decoder_output

def test_bench():
	instruction_int = int('1' + '000000' + '00001' + '00010' + '000' + '0000' + '1' + '11000' + '11', 2)
	instruction = Signal(intbv(instruction_int))

	arg_select = Signal(intbv(int('0000000000', 2)))
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

	output = hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw)

	@instance
	def stimulus():
		for i in range(instruction_table[:5]):
			instruction.next = intbv(int(instruction_table[i],2))
			yield delay(10)
			print "Argument Select: " + bin(arg_select, width = 10)

	return output, stimulus

# print bin(instruction[25:20])
# print bin(instruction[25:20]) + bin(instruction[20:15])
# print get_arg_select(['rs1', 'shamtw'])

sim = Simulation(test_bench)
sim.run()