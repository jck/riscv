from myhdl import block, instance, Signal, always, delay, modbv

from riscv.alu_constants import ALU_OP_WIDTH
from riscv.control_constants import PC_SRC_SEL_WIDTH, IMM_TYPE_WIDTH, SRC_A_SEL_WIDTH, SRC_B_SEL_WIDTH, MEM_TYPE_WIDTH, \
    WB_SRC_SEL_WIDTH
from riscv.controller import controller
from riscv.csr_constants import PRV_WIDTH, CSR_CMD_WIDTH, ECODE_WIDTH
from riscv.md_constants import MD_OP_WIDTH, MD_OUT_SEL_WIDTH
from riscv.opcode_constants import INST_WIDTH, REG_ADDR_WIDTH
from tests.test_instructions import test_instruction


@block
def test_controller():
    clock = Signal(False)
    reset = Signal(False)
    inst_DX = Signal(modbv(0)[INST_WIDTH:])
    imem_wait, imem_badmem_e, dmem_wait, dmem_badmem_e, cmp_true = [Signal(False) for _ in range(5)]
    prv = Signal(modbv(0)[PRV_WIDTH:])
    PC_src_sel = Signal(modbv(0)[PC_SRC_SEL_WIDTH:])
    imm_type = Signal(modbv(0)[IMM_TYPE_WIDTH:])
    bypass_rs1, bypass_rs2 = [Signal(False) for _ in range(2)]
    src_a_sel = Signal(modbv(0)[SRC_A_SEL_WIDTH:])
    src_b_sel = Signal(modbv(0)[SRC_B_SEL_WIDTH:])
    alu_op = Signal(modbv(0)[ALU_OP_WIDTH:])
    dmem_en, dmem_wen = [Signal(False) for _ in range(2)]
    dmem_size = Signal(modbv(0)[2:])
    dmem_type = Signal(modbv(0)[MEM_TYPE_WIDTH:])
    md_req_valid, md_req_ready, md_req_in_1_signed, md_req_in_2_signed = [Signal(False) for _ in range(4)]
    md_req_op = Signal(modbv(0)[MD_OP_WIDTH:])
    md_req_out_sel = Signal(modbv(0)[MD_OUT_SEL_WIDTH:])
    md_resp_valid, eret = [Signal(False) for _ in range(2)]
    csr_cmd = Signal(modbv(0)[CSR_CMD_WIDTH:])
    csr_imm_sel, illegal_csr_access, interrupt_pending, interrupt_taken, wr_reg_WB = [Signal(False) for _ in range(5)]
    reg_to_wr_WB = Signal(modbv(0)[REG_ADDR_WIDTH:])
    wb_src_sel_WB = Signal(modbv(0)[WB_SRC_SEL_WIDTH:])
    stall_IF, kill_IF, stall_DX, kill_DX, stall_WB, kill_WB, exception_WB = [Signal(False) for _ in range(7)]
    exception_code_WB = Signal(modbv(0)[ECODE_WIDTH:])
    retire_WB = Signal(False)

    input_list = ['clock', 'reset', 'inst_DX', 'imem_wait', 'imem_badmem_e', 'dmem_wait', 'dmem_badmem_e', 'cmp_true',
                  'prv', 'md_req_ready', 'md_resp_valid', 'illegal_csr_access', 'interrupt_pending', 'interrupt_taken',
                  'input_list', 'current_output', 'output']

    current_output = {}
    output = {}
    for key, value in locals().items():
        if key[:2] != '__' and key not in input_list:
            current_output[key] = 0
            output[key] = value

    def assert_output():
        assert current_output == output

    ctrl_inst = controller(clock, reset, inst_DX, imem_wait, imem_badmem_e, dmem_wait, dmem_badmem_e, cmp_true, prv,
                           PC_src_sel, imm_type, bypass_rs1, bypass_rs2, src_a_sel, src_b_sel, alu_op, dmem_en,
                           dmem_wen, dmem_size, dmem_type, md_req_valid, md_req_ready, md_req_in_1_signed,
                           md_req_in_2_signed, md_req_op, md_req_out_sel, md_resp_valid, eret, csr_cmd, csr_imm_sel,
                           illegal_csr_access, interrupt_pending, interrupt_taken, wr_reg_WB, reg_to_wr_WB,
                           wb_src_sel_WB, stall_IF, kill_IF, stall_DX, kill_DX, stall_WB, kill_WB, exception_WB,
                           exception_code_WB, retire_WB)

    ctrl_inst.convert(hdl='Verilog')

    @always(delay(10))
    def clock_drive():
        clock.next = not clock

    @instance
    def test():
        reset.next = True
        prv.next = 3
        yield clock.posedge
        reset.next = False
        inst_DX.next = int(test_instruction['sub'], 2)
        yield clock.posedge
        yield delay(1)
        current_output['alu_op'] = 10
        current_output['wr_reg_WB'] = 1
        current_output['reg_to_wr_WB'] = 3
        current_output['retire_WB'] = 1
        assert_output()

    return ctrl_inst, clock_drive, test


test_inst = test_controller()
# test_inst.config_sim(trace=True)
test_inst.run_sim(100)
test_inst.quit_sim()