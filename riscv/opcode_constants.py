from myhdl import modbv, intbv

INST_WIDTH = 32
REG_ADDR_WIDTH = 5
XPR_LEN = 32
DOUBLE_XPR_LEN = 64
LOG2_XPR_LEN = 5
SHAMT_WIDTH = 5

RV_NOP = modbv(int('0010011', 2))[INST_WIDTH:]


RV32_LOAD = modbv(int('0000011', 2))[7:]
RV32_STORE = modbv(int('0100011', 2))[7:]
RV32_MADD = modbv(int('1000011', 2))[7:]
RV32_BRANCH = modbv(int('1100011', 2))[7:]

RV32_LOAD_FP = modbv(int('0000111', 2))[7:]
RV32_STORE_FP = modbv(int('0100111', 2))[7:]
RV32_MSUB = modbv(int('1000111', 2))[7:]
RV32_JALR = modbv(int('1100111', 2))[7:]

RV32_CUSTOM_0 = modbv(int('0001011', 2))[7:]
RV32_CUSTOM_1 = modbv(int('0101011', 2))[7:]
RV32_NMSUB = modbv(int('1001011', 2))[7:]

# 7'b1101011 is reserved

RV32_MISC_MEM = modbv(int('0001111', 2))[7:]
RV32_AMO = modbv(int('0101111', 2))[7:]
RV32_NMADD = modbv(int('1001111', 2))[7:]
RV32_JAL = modbv(int('1101111', 2))[7:]

RV32_OP_IMM = modbv(int('0010011', 2))[7:]
RV32_OP = modbv(int('0110011', 2))[7:]
RV32_OP_FP = modbv(int('1010011', 2))[7:]
RV32_SYSTEM = modbv(int('1110011', 2))[7:]

RV32_AUIPC = modbv(int('0010111', 2))[7:]
RV32_LUI = modbv(int('0110111', 2))[7:]
# 7'b1010111 is reserved
# 7'b1110111 is reserved

# 7'b0011011 is RV64-specific
# 7'b0111011 is RV64-specific
RV32_CUSTOM_2 = modbv(int('1011011', 2))[7:]
RV32_CUSTOM_3 = modbv(int('1111011', 2))[7:]

# Arithmetic FUNCT3 encodings

RV32_FUNCT3_ADD_SUB = 0
RV32_FUNCT3_SLL = 1
RV32_FUNCT3_SLT = 2
RV32_FUNCT3_SLTU = 3
RV32_FUNCT3_XOR = 4
RV32_FUNCT3_SRA_SRL = 5
RV32_FUNCT3_OR = 6
RV32_FUNCT3_AND = 7

# Branch FUNCT3 encodings

RV32_FUNCT3_BEQ = 0
RV32_FUNCT3_BNE = 1
RV32_FUNCT3_BLT = 4
RV32_FUNCT3_BGE = 5
RV32_FUNCT3_BLTU = 6
RV32_FUNCT3_BGEU = 7

# MISC-MEM FUNCT3 encodings
RV32_FUNCT3_FENCE = 0
RV32_FUNCT3_FENCE_I = 1

# SYSTEM FUNCT3 encodings

RV32_FUNCT3_PRIV = 0
RV32_FUNCT3_CSRRW = 1
RV32_FUNCT3_CSRRS = 2
RV32_FUNCT3_CSRRC = 3
RV32_FUNCT3_CSRRWI = 5
RV32_FUNCT3_CSRRSI = 6
RV32_FUNCT3_CSRRCI = 7

# PRIV FUNCT12 encodings

RV32_FUNCT12_ECALL = modbv(int('000000000000', 2))[12:]
RV32_FUNCT12_EBREAK = modbv(int('000000000001', 2))[12:]
RV32_FUNCT12_ERET = modbv(int('000100000000', 2))[12:]
RV32_FUNCT12_WFI = modbv(int('000100000010', 2))[12:]

# RV32M encodings
RV32_FUNCT7_MUL_DIV = modbv(1)[7:]

RV32_FUNCT3_MUL = modbv(0)[3:]
RV32_FUNCT3_MULH = modbv(1)[3:]
RV32_FUNCT3_MULHSU = modbv(2)[3:]
RV32_FUNCT3_MULHU = modbv(3)[3:]
RV32_FUNCT3_DIV = modbv(4)[3:]
RV32_FUNCT3_DIVU = modbv(5)[3:]
RV32_FUNCT3_REM = modbv(6)[3:]
RV32_FUNCT3_REMU = modbv(7)[3:]
