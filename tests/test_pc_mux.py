from myhdl import block, Signal, modbv, instance

from riscv.PC_mux import PC_mux
from riscv.control_constants import PC_SRC_SEL_WIDTH
from riscv.opcode_constants import INST_WIDTH, XPR_LEN


@block
def test_pc_mux():

    PC_src_sel = Signal(modbv(0)[PC_SRC_SEL_WIDTH:])
    inst_DX = Signal(modbv(0)[INST_WIDTH:])
    rs1_data, PC_IF, PC_DX, handler_PC, epc, PC_PIF = [Signal(modbv(0)[XPR_LEN:]) for _ in range(6)]

    pc_mux_inst = PC_mux(PC_src_sel, inst_DX, rs1_data, PC_IF, PC_DX, handler_PC, epc, PC_PIF)
    pc_mux_inst.convert(hdl='Verilog')

    return pc_mux_inst
