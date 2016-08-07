from myhdl import always_comb, intbv, Signal, block, concat, enum

itypes = enum('family_code', 'opcode', 'funct3', 'funct7', 'rs1',
              'rs2', 'imm12lo', 'imm12hi', 'instruction_id', 'rd', 'rm',
              'imm12', 'imm12_sb', 'imm20', 'imm20_pc', 'shamt', 'shamtw')


def get_arg_select(arg_list):
    """
    Utility function to generate the arg_select signal depending upon the
    arguments present in the instruction

    :param list arg_list: List of arguments passed by the instruction
    :param Signal arg_select: 10 bit active low argument select signal
    """

    arg_select_string = ''
    argument_list = (itypes.rs1, itypes.rs2, itypes.rd, itypes.rm,
                     itypes.imm12lo, itypes.imm12hi, itypes.imm12,
                     itypes.imm20, itypes.shamt,
                     itypes.shamtw)
    arg_select_list = ['0' for i in range(len(argument_list))]

    for i in range(len(arg_list)):
        for j in range(len(argument_list)):
            if arg_list[i] == argument_list[j]:
                if arg_select_list[j] == '1':
                    pass
                else:
                    arg_select_list[j] = '1'

            else:
                if arg_select_list[j] == '1':
                    pass
                else:
                    arg_select_list[j] = '0'
            arg_select_string += arg_select_list[j]

    return Signal(intbv(int(arg_select_string[-10:], 2))[10:])


def get_arg(instruction, itype):
    """
    Utiity function to return commonly used slices/arguments
    of instructions in hexadecimal or binary formats

    :param Signal instruction: Input instruction
    :param str argument_name: the name of the argument to be extracted
    """

    if itype == itypes.family_code:
        return instruction[7:2]
    elif itype == itypes.opcode:
        return instruction[7:]
    elif itype == itypes.funct3:
        return instruction[15:12]
    elif itype == itypes.funct7:
        return instruction[32:25]
    elif itype == itypes.rs1:
        return instruction[20:15]
    elif itype == itypes.rs2:
        return instruction[25:20]
    elif itype == itypes.imm12lo:
        return concat(instruction[32], instruction[7], instruction[31:27])
    elif itype == itypes.imm12hi:
        return concat(instruction[27:25], instruction[12:8])
    elif itype == itypes.instruction_id:
        return instruction[15:12]
    elif itype == itypes.rd:
        return instruction[12:7]
    elif itype == itypes.imm12:
        return instruction[32:20]
    elif itype == itypes.imm12_sb:
        return concat(instruction[32:25], instruction[12:7])
    elif itype == itypes.imm20:
        return concat(instruction[31], instruction[20:12], instruction[20], instruction[31:21])
    elif itype == itypes.imm20_pc:
        return instruction[31:12]
    elif itype == itypes.shamtw:
        return instruction[25:20]
    elif itype == itypes.shamt:
        return instruction[25:20]
    else:
        return None


@block
def hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw, opcode,
                funct3, funct7):
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
    :param Signal opcode: Instruction opcode
    :param Signal funct3: instruction funct3
    :param Signal funct7: instruction funct7
    """

    @always_comb
    def decoder_output():
        instruction_family = instruction[7:2]
        opcode.next = instruction[7:]

        # Branch Instructions
        if instruction_family == int('11000', 2):

            funct3.next = instruction[15:12]
            funct7.next = intbv(0)

            rs1.next = instruction[20:15]
            rs2.next = instruction[25:20]
            imm12hi.next = concat(instruction[27:25], instruction[12:8])
            imm12lo.next = concat(instruction[32], instruction[7], instruction[31:27])
            imm12.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rd.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rs1, itypes.rs2, itypes.imm12lo, itypes.imm12hi)
            arg_select.next = int('1100110000', 2)

        # Jump Instructions
        elif instruction_family == int('11001', 2):

            funct3.next = intbv(0)
            funct7.next = intbv(0)

            rs1.next = instruction[20:15]
            rd.next = instruction[12:7]
            imm12.next = instruction[32:20]
            rs2.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rs1, itypes.rd, itypes.imm12)
            arg_select.next = int('1010001000', 2)

        elif instruction_family == int('11011', 2):

            funct3.next = intbv(0)
            funct7.next = intbv(0)

            rs1.next = intbv(0)
            rd.next = instruction[12:7]
            imm12.next = intbv(0)
            rs2.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = concat(instruction[31], instruction[20:12], instruction[20], instruction[31:21])
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rd, itypes.imm20)
            arg_select.next = int('0010000100', 2)

        # LUI and AUIPC
        elif instruction_family == int('01101', 2) or instruction_family == int('00101', 2):

            funct3.next = intbv(0)
            funct7.next = intbv(0)

            rs1.next = intbv(0)
            rd.next = instruction[12:7]
            imm12.next = intbv(0)
            rs2.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = instruction[31:12]
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rd, itypes.imm20)
            arg_select.next = int('0010000100', 2)

        # Addition and Logical immediate Instructions
        elif instruction_family == int('00100', 2):
            funct3.next = instruction[15:12]

            rs1.next = instruction[20:15]
            rd.next = instruction[12:7]
            imm12.next = intbv(0)
            rs2.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            if instruction[15:12] == 1 or instruction[15:12] == 5:
                shamt.next = instruction[25:20]
                funct7.next = instruction[32:25]
                imm12.next = intbv(0)
                # arg_list = (itypes.rs1, itypes.rd, itypes.shamt)
                arg_select.next = int('1010000010', 2)
            else:
                shamt.next = intbv(0)
                funct7.next = intbv(0)
                imm12.next = instruction[32:20]
                # arg_list = (itypes.rs1, itypes.rd, itypes.imm12)
                arg_select.next = int('1010001000', 2)

        # Addition and Logical Instructions
        elif instruction_family == int('01100', 2):
            funct3.next = instruction[15:12]
            funct7.next = intbv(0)
            rs1.next = instruction[20:15]
            rs2.next = instruction[25:20]
            rd.next = instruction[12:7]
            imm12.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rd, itypes.rs1, itypes.rs2)
            arg_select.next = int('1110000000', 2)

        # FENCE and FENCE.I instructions
        elif instruction_family == int('00011', 2):
            funct3.next = instruction[15:12]
            funct7.next = intbv(0)
            rs1.next = intbv(0)
            rs2.next = intbv(0)
            rd.next = intbv(0)
            imm12.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = ()
            arg_select.next = int('0000000000', 2)

        # Load Instructions
        elif instruction_family == int('00000', 2):

            funct3.next = instruction[15:12]
            funct7.next = intbv(0)

            rs1.next = instruction[20:15]
            rd.next = instruction[12:7]
            imm12.next = instruction[32:20]
            rs2.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rs1, itypes.rd, itypes.imm12)
            arg_select.next = int('1010001000', 2)

        # Store Instructions
        elif instruction_family == int('01000', 2):

            funct3.next = instruction[15:12]
            funct7.next = intbv(0)

            rs1.next = instruction[20:15]
            rs2.next = instruction[25:20]
            imm12.next = concat(instruction[32:25], instruction[12:7])
            rd.next = intbv(0)
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            # arg_list = (itypes.rs1, itypes.rs2, itypes.imm12)
            arg_select.next = int('1100001000', 2)

        # System Instructions
        elif instruction_family == int('11100', 2):
            funct3.next = instruction[15:12]
            funct7.next = intbv(0)
            rs1.next = intbv(0)
            rs2.next = intbv(0)
            imm12.next = instruction[32:20]
            imm12lo.next = intbv(0)
            imm12hi.next = intbv(0)
            imm20.next = intbv(0)
            shamt.next = intbv(0)
            shamtw.next = intbv(0)
            rm.next = intbv(0)

            if instruction[15:12] == 0:
                rd.next = intbv(0)
                # arg_list = (itypes.imm12,)
                arg_select.next = int('0000001000', 2)
            else:
                rd.next = instruction[12:7]
                # arg_list = (itypes.rd, itypes.imm12)
                arg_select.next = int('0010001000', 2)

    return decoder_output
