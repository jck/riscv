from decoder import get_hex, get_int
from instruction_table import instruction_table
from myhdl import always_comb, intbv, Signal, Simulation, delay, bin

def get_args(instruction, argument_list):
	"""
	Utiity function to return commonly used slices/arguments
	of instructions in hexadecimal or binary formats
	
	:param Signal instruction: Input instruction 
	:param str argument_name: the name of the argument to be extracted
	"""
	if argument_name == 'family_code':
		return get_hex(instruction[7:2])

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
        		
        	instruction_code = get_arg(instruction, 'instruction_code')

        	rs1.next = get_arg(instruction, 'rs1')
        	rs2.next = get_arg(instruction, 'rs2')
        	imm12lo.next = get_arg(instruction, 'imm12lo')
        	imm12hi.next = get_arg(instruction, 'imm12hi')

        return decoder_output



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

print bin(instruction[7:2])
