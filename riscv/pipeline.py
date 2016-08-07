from myhdl import block, concat, modbv, Signal, always_comb, always, instances

from riscv.PC_mux import PC_mux
from riscv.alu import alu
from riscv.alu_constants import ALU_OP_WIDTH
from riscv.control_constants import *
from riscv.csr_constants import CSR_ADDR_WIDTH, CSR_CMD_WIDTH, PRV_WIDTH, ECODE_WIDTH
from riscv.csr_file import csr_file
from riscv.controller import controller
from riscv.immediate_gen import immediate_gen
from riscv.md_constants import MD_OUT_SEL_WIDTH, MD_OP_WIDTH
from riscv.mult_div import mult_div
from riscv.opcode_constants import XPR_LEN, INST_WIDTH, REG_ADDR_WIDTH, RV_NOP
from riscv.register_file import register_file
from riscv.src_a_mux import src_a_mux
from riscv.src_b_mux import src_b_mux


@block
def pipeline(clock, ext_interrupts, reset, imem_wait, imem_addr, imem_rdata, imem_badmem_e, dmem_wait, dmem_en,
             dmem_wen, dmem_size, dmem_addr, dmem_wdata_delayed, dmem_rdata, dmem_badmem_e, htif_reset,
             htif_pcr_req_valid, htif_pcr_req_ready, htif_pcr_req_rw, htif_pcr_req_addr, htif_pcr_req_data,
             htif_pcr_resp_valid, htif_pcr_resp_ready, htif_pcr_resp_data):

    """
    The Pipeline Module

    :param Signal clock:
    :param Signal ext_interrupts:
    :param Signal reset:
    :param Signal imem_wait:
    :param Signal imem_addr:
    :param Signal imem_rdata:
    :param Signal imem_badmem_e:
    :param Signal dmem_wait:
    :param Signal dmem_en:
    :param Signal dmem_wen:
    :param Signal dmem_size:
    :param Signal dmem_addr:
    :param Signal dmem_wdata_delayed:
    :param Signal dmem_rdata:
    :param Signal dmem_badmem_e:
    :param Signal htif_reset:
    :param Signal htif_pcr_req_valid:
    :param Signal htif_pcr_req_ready:
    :param Signal htif_pcr_req_rw:
    :param Signal htif_pcr_req_addr:
    :param Signal htif_pcr_req_data:
    :param Signal htif_pcr_resp_valid:
    :param Signal htif_pcr_resp_ready:
    :param Signal htif_pcr_resp_data:
    """

    def store_data(data, mem_type):

        if mem_type == MEM_TYPE_SB:
            return concat(data[8:0], data[8:0], data[8:0], data[8:0])
        elif mem_type == MEM_TYPE_SH:
            return concat(data[16:0], data[16:0])
        else:
            return data

    def load_data(address, data, mem_type):

        shifted_data = data >> concat(address[2:0], False, False, False)

        b_extend = modbv(0)[32:0]
        if shifted_data[7]:
            b_extend = modbv(((1 << 24) - 1) << 8)[32:0]

        h_extend = modbv(0)[32:0]
        if shifted_data[15]:
            h_extend = modbv(((1 << 16) - 1) << 16)[32:0]

        if mem_type == MEM_TYPE_LB:
            return shifted_data & ((1 << 16) - 1) | b_extend
        elif mem_type == MEM_TYPE_LH:
            return shifted_data & ((1 << 32) - 1) | h_extend
        elif mem_type == MEM_TYPE_LBU:
            return shifted_data & ((1 << 16) - 1)
        elif mem_type == MEM_TYPE_LHU:
            return shifted_data & ((1 << 32) - 1)

    PC_src_sel = Signal(modbv(0)[PC_SRC_SEL_WIDTH:])
    PC_PIF = Signal(modbv(0)[XPR_LEN:])

    PC_IF = Signal(modbv(0)[XPR_LEN:])

    kill_IF = Signal(False)
    stall_IF = Signal(False)

    PC_DX = Signal(modbv(0)[XPR_LEN:])
    inst_DX = Signal(modbv(0)[INST_WIDTH:])

    kill_DX = Signal(False)
    stall_DX = Signal(False)

    imm_type = Signal(modbv(0)[IMM_TYPE_WIDTH:])
    imm = Signal(modbv(0)[XPR_LEN:])
    src_a_sel = Signal(modbv(0)[SRC_A_SEL_WIDTH:])
    src_b_sel = Signal(modbv(0)[SRC_B_SEL_WIDTH:])
    rs1_addr = Signal(modbv(0)[REG_ADDR_WIDTH:])
    rs1_data = Signal(modbv(0)[XPR_LEN:])
    rs1_data_bypassed = Signal(modbv(0)[XPR_LEN:])
    rs2_addr = Signal(modbv(0)[REG_ADDR_WIDTH:])
    rs2_data = Signal(modbv(0)[XPR_LEN:])
    rs2_data_bypassed = Signal(modbv(0)[XPR_LEN:])
    alu_op = Signal(modbv(0)[ALU_OP_WIDTH:])
    alu_src_a = Signal(modbv(0)[XPR_LEN:])
    alu_src_b = Signal(modbv(0)[XPR_LEN:])
    alu_out = Signal(modbv(0)[XPR_LEN:])
    cmp_true = Signal(False)
    bypass_rs1 = Signal(False)
    bypass_rs2 = Signal(False)
    dmem_type = Signal(modbv(0)[MEM_TYPE_WIDTH:])

    md_req_valid = Signal(False)
    md_req_ready = Signal(False)
    md_req_in_1_signed = Signal(False)
    md_req_in_2_signed = Signal(False)
    md_req_out_sel = Signal(modbv(0)[MD_OUT_SEL_WIDTH:])
    md_req_op = Signal(modbv(0)[MD_OP_WIDTH:])
    md_resp_valid = Signal(False)
    md_resp_result = Signal(modbv(0)[XPR_LEN:])

    PC_WB = Signal(modbv(0)[XPR_LEN:])
    alu_out_WB = Signal(modbv(0)[XPR_LEN:])
    csr_rdata_WB = Signal(modbv(0)[XPR_LEN:])
    store_data_WB = Signal(modbv(0)[XPR_LEN:])

    kill_WB = Signal(False)
    stall_WB = Signal(False)
    bypass_data_WB = Signal(modbv(0)[XPR_LEN:])
    load_data_WB = Signal(modbv(0)[XPR_LEN:])
    wb_data_WB = Signal(modbv(0)[XPR_LEN:])
    reg_to_wr_WB = Signal(modbv(0)[REG_ADDR_WIDTH:])
    wr_reg_WB = Signal(False)
    wb_src_sel_WB = Signal(modbv(0)[WB_SRC_SEL_WIDTH:])
    dmem_type_WB = Signal(modbv(0)[MEM_TYPE_WIDTH:])

    # CSR Management
    csr_addr = Signal(modbv(0)[CSR_ADDR_WIDTH:])
    csr_cmd = Signal(modbv(0)[CSR_CMD_WIDTH:])
    csr_imm_sel = Signal(False)
    prv = Signal(modbv(0)[PRV_WIDTH:])
    illegal_csr_access = Signal(False)
    interrupt_pending = Signal(False)
    interrupt_taken = Signal(False)
    csr_wdata = Signal(modbv(0)[XPR_LEN:])
    csr_rdata = Signal(modbv(0)[XPR_LEN:])
    retire_WB = Signal(False)
    exception_WB = Signal(False)
    exception_code_WB = Signal(modbv(0)[ECODE_WIDTH:])
    handler_PC = Signal(modbv(0)[XPR_LEN:])
    eret = Signal(False)
    epc = Signal(modbv(0)[XPR_LEN:])

    controller_inst = controller(clock, reset, inst_DX, imem_wait, imem_badmem_e, dmem_wait, dmem_badmem_e,
                                 cmp_true, PC_src_sel, imm_type, src_a_sel, src_b_sel, bypass_rs1, bypass_rs2,
                                 alu_op, dmem_en, dmem_wen, dmem_size, dmem_type,md_req_valid, md_req_ready,
                                 md_req_op, md_req_in_1_signed, md_req_in_2_signed, md_req_out_sel, md_resp_valid,
                                 wr_reg_WB, reg_to_wr_WB, wb_src_sel_WB, stall_IF, kill_IF, stall_DX, kill_DX,
                                 stall_WB, kill_WB, exception_WB, exception_code_WB, retire_WB, csr_cmd,
                                 csr_imm_sel, illegal_csr_access, interrupt_pending, interrupt_taken, prv, eret)

    pc_mux_inst = PC_mux(PC_src_sel, inst_DX, rs1_data_bypassed, PC_IF, PC_DX, handler_PC, epc, PC_PIF)

    @always_comb
    def assign_1():
        imem_addr.next = PC_PIF

    @always(clock.posedge)
    def sequential_1():
        if reset:
            PC_IF.next = int('200', 16)
        elif not stall_IF:
            PC_IF.next = PC_PIF

    @always(clock.posedge)
    def sequential_2():
        if reset:
            PC_DX.next = 0
            inst_DX.next = RV_NOP
        elif not stall_DX:
            if kill_IF:
                inst_DX.next = RV_NOP
            else:
                PC_DX.next = PC_IF
                inst_DX.next = imem_rdata

    @always_comb
    def assign_2():
        rs1_addr.next = inst_DX[20:15]
        rs2_addr.next = inst_DX[25:20]

    reg_file_inst = register_file(clock, rs1_addr, rs1_data, rs2_addr, rs2_data, wr_reg_WB, reg_to_wr_WB, wb_data_WB)

    imm_gen_inst = immediate_gen(inst_DX, imm_type, imm)

    src_a_mux_inst = src_a_mux(src_a_sel, PC_DX, rs1_data_bypassed, alu_src_a)

    src_b_mux_inst = src_b_mux(src_b_sel, imm, rs2_data_bypassed, alu_src_b)

    @always_comb
    def assign_3():
        if bypass_rs1:
            rs1_data_bypassed.next = bypass_data_WB
        else:
            rs1_data_bypassed.next = rs1_data
        if bypass_rs2:
            rs2_data_bypassed.next = bypass_data_WB
        else:
            rs2_data_bypassed.next = rs2_data

    alu_inst = alu(alu_op, alu_src_a, alu_src_b, alu_out)

    md_inst = mult_div(clock, reset, md_req_valid, md_req_ready, md_req_in_1_signed, md_req_in_2_signed, md_req_out_sel,
                      md_req_op, rs1_data_bypassed, rs2_data_bypassed, md_resp_valid, md_resp_result)

    @always_comb
    def assign_4():
        cmp_true.next = alu_out[0]
        dmem_addr.next = alu_out

    @always(clock.posedge)
    def seauential_3():
        if not stall_WB:
            PC_WB.next = PC_DX
            store_data_WB.next = rs2_data_bypassed
            alu_out_WB.next = alu_out
            csr_rdata_WB.next = csr_rdata
            dmem_type_WB.next = dmem_type

    @always_comb
    def assign_5():
        if wb_src_sel_WB == WB_SRC_CSR:
            bypass_data_WB.next = csr_rdata_WB
        elif wb_src_sel_WB == WB_SRC_MD:
            bypass_data_WB.next = md_resp_result
        else:
            bypass_data_WB.next = alu_out_WB
        load_data_WB.next = load_data(alu_out_WB, dmem_rdata, dmem_type_WB)

    @always_comb
    def assign_6():
        if wb_src_sel_WB == WB_SRC_ALU:
            wb_data_WB.next = bypass_data_WB
        elif wb_src_sel_WB == WB_SRC_MEM:
            wb_data_WB.next = load_data_WB
        elif wb_src_sel_WB == WB_SRC_CSR:
            wb_data_WB.next = bypass_data_WB
        elif wb_src_sel_WB == WB_SRC_MD:
            wb_data_WB.next = bypass_data_WB
        else:
            wb_data_WB.next = bypass_data_WB

        dmem_wdata_delayed.next = store_data(store_data_WB, dmem_type_WB)
        csr_addr.next = inst_DX[32:20]

        if csr_imm_sel:
            csr_wdata.next = inst_DX[20:15]
        else:
            csr_wdata.next = rs1_data_bypassed

    csr_file_inst = csr_file(clock, ext_interrupts, reset, csr_addr, csr_cmd, csr_wdata, prv, illegal_csr_access,
                             csr_rdata, retire_WB, exception_WB, exception_code_WB, alu_out_WB, PC_WB, epc, eret,
                             handler_PC, interrupt_pending, interrupt_taken, htif_reset, htif_pcr_req_valid,
                             htif_pcr_req_ready, htif_pcr_req_rw, htif_pcr_req_rw, htif_pcr_req_addr, htif_pcr_req_data,
                             htif_pcr_resp_valid, htif_pcr_resp_ready, htif_pcr_resp_data)

    return instances()
