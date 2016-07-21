from myhdl import modbv

ALU_OP_WIDTH = 4

ALU_OP_ADD = modbv(0)[ALU_OP_WIDTH:]
ALU_OP_SLL = modbv(1)[ALU_OP_WIDTH:]
ALU_OP_XOR = modbv(4)[ALU_OP_WIDTH:]
ALU_OP_OR = modbv(6)[ALU_OP_WIDTH:]
ALU_OP_AND = modbv(7)[ALU_OP_WIDTH:]
ALU_OP_SRL = modbv(5)[ALU_OP_WIDTH:]
ALU_OP_SEQ = modbv(8)[ALU_OP_WIDTH:]
ALU_OP_SNE = modbv(9)[ALU_OP_WIDTH:]
ALU_OP_SUB = modbv(10)[ALU_OP_WIDTH:]
ALU_OP_SRA = modbv(11)[ALU_OP_WIDTH:]
ALU_OP_SLT = modbv(12)[ALU_OP_WIDTH:]
ALU_OP_SGE = modbv(13)[ALU_OP_WIDTH:]
ALU_OP_SLTU = modbv(14)[ALU_OP_WIDTH:]
ALU_OP_SGEU = modbv(15)[ALU_OP_WIDTH:]
