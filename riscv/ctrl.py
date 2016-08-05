from myhdl import always_comb, intbv, concat, block

from riscv.control_constants import *
from riscv.csr_constants import *
from riscv.alu_constants import *
from riscv.opcode_constants import *
from riscv.md_constants import *

@block
def vscale_ctrl(clk,
                reset,
                inst_DX,
                imem_wait,
                imem_badmem_e,
                dmem_wait,
                dmem_badmem_e,
                cmp_true,
                prv,
                PC_src_sel,
                imm_type,
                bypass_rs1,
                bypass_rs2,
                src_a_sel,
                src_b_sel,
                alu_op,
                dmem_en,
                dmem_wen,
                dmem_size,
                dmem_type,
                md_req_valid,
                md_req_ready,
                md_req_in_1_signed,
                md_req_in_2_signed,
                md_req_op,
                md_req_out_sel,
                md_resp_valid,
                eret,
                csr_cmd,
                csr_imm_sel,
                illegal_csr_access,
                interrupt_pending,
                interrupt_taken,
                wr_reg_WB,
                reg_to_wr_WB,
                wb_src_sel_WB,
                stall_IF,
                kill_IF,
                stall_DX,
                kill_DX,
                stall_WB,
                kill_WB,
                exception_WB,
                exception_code_WB,
                retire_WB):

    # If Stage control
    @always(clk.posedge)
    def IF_stage():
        if reset:
            replay_IF = intbv(1)[1:]
        else:
            replay_IF = (redirect & imem_wait) | (fence_i & store_in_WB)

    kill_IF = stall_IF | ex_IF | ex_DX | ex_WB | redirect | replay_IF | interrupt_taken
    stall_IF = stall_DX | ((imem_wait & ~redirect) & ~(ex_WB | interrupt_taken))
    ex_IF = imem_badmem_e & ~imem_wait & ~redirect & ~replay_IF

    # DX Stage control

    @always(clk.posedge)
    def DX_stage():
        if reset:
            had_ex_DX = 0
            prev_killed_DX = 0
        elif ~stall_DX:
            had_ex_DX = ex_IF
            prev_killed_DX = kill_IF

    # interrupts kill IF, DX instructions -- WB may commit
    # Exceptions never show up falsely due to hazards -- don't get exceptions on stall

    kill_DX   = stall_DX | ex_DX | x_WB | interrupt_taken
    stall_DX  = stall_WB | ((load_use | raw_on_busy_md | (fence_i & store_in_WB) | (uses_md_unkilled & ~md_req_ready)) & ~(ex_DX | ex_WB | interrupt_taken))
    new_ex_DX = ebreak | ecall | illegal_instruction | illegal_csr_access

    killed_DX = prev_killed_DX | kill_DX
    ex_DX     = had_ex_DX | new_ex_DX

    @always_comb
    def DX_stage_comb():
        ex_code_DX = ECODE_INST_ADDR_MISALIGNED
        if had_ex_DX:
            ex_code_DX = ECODE_INST_ADDR_MISALIGNED
        elif illegal_instruction:
            ex_code_DX = ECODE_ILLEGAL_INST
        elif illegal_csr_access:
            ex_code_DX = ECODE_ILLEGAL_INST
        elif ebreak:
            ex_code_DX = ECODE_BREAKPOINT
        elif ecall:
            ex_code_DX = ECODE_ECALL_FROM_U + prv

    dmem_size = concat(intbv(0)[1:], funct3[1:0])
    dmem_type = funct3

    @always_comb
    def control():
        illegal_instruction = intbv(0)[1:]
        csr_cmd_unkilled = CSR_IDLE
        csr_imm_sel = funct3[2]
        ecall = intbv(0)[1:]
        ebreak = intbv(0)[1:]
        eret_unkilled = intbv(0)[1:]
        fence_i = intbv(0)[1:]
        branch_taken_unkilled = intbv(0)[1:]
        jal_unkilled = intbv(0)[1:]
        jalr_unkilled = intbv(0)[1:]
        uses_rs1 = intbv(1)[1:]
        uses_rs2 = intbv(0)[1:]
        imm_type = IMM_I
        src_a_sel = SRC_A_RS1
        src_b_sel = SRC_B_IMM
        alu_op = ALU_OP_ADD
        dmem_en_unkilled = intbv(0)[1:]
        dmem_wen_unkilled = intbv(0)[1:]
        wr_reg_unkilled_DX = intbv(0)[1:]
        wb_src_sel_DX = WB_SRC_ALU
        uses_md_unkilled = intbv(0)[1:]
        wfi_unkilled_DX = intbv(0)[1:]

        if opcode == RV32_LOAD:
            dmem_en_unkilled = intbv(1)[1:]
            wr_reg_unkilled_DX = intbv(1)[1:]
            wb_src_sel_DX = WB_SRC_MEM

        elif opcode == RV32_STORE:
            uses_rs2 = intbv(1)[1:]
            imm_type = IMM_S
            dmem_en_unkilled = intbv(1)[1:]
            dmem_wen_unkilled = intbv(1)[1:]

        elif opcode == RV32_BRANCH:
            uses_rs2 = intbv(1)[1:]
            branch_taken_unkilled = cmp_true
            src_b_sel = SRC_B_RS2

            if funct3 == RV32_FUNCT3_BEQ:
                alu_op = ALU_OP_SEQ
            elif funct3 == RV32_FUNCT3_BNE:
                alu_op = ALU_OP_SNE
            elif funct3 == RV32_FUNCT3_BLT:
                alu_op = ALU_OP_SLT
            elif funct3 == RV32_FUNCT3_BLTU:
                alu_op = ALU_OP_SLTU
            elif funct3 == RV32_FUNCT3_BGE:
                alu_op = ALU_OP_SGE
            elif funct3 == RV32_FUNCT3_BGEU:
                alu_op = ALU_OP_SGEU
            else:
                illegal_instruction = intbv(1)[1:]

        elif opcode == RV32_JAL:
            jal_unkilled = intbv(1)[1:]
            uses_rs1 = intbv(0)[1:]
            src_a_sel = SRC_A_PC
            src_b_sel = SRC_B_FOUR
            wr_reg_unkilled_DX = intbv(1)[1:]

        elif opcode == RV32_JALR:
            illegal_instruction = (funct3 != 0)
            jalr_unkilled = intbv(1)[1:]
            src_a_sel = SRC_A_PC
            src_b_sel = SRC_B_FOUR
            wr_reg_unkilled_DX = intbv(1)[1:]

        elif opcode == RV32_MISC_MEM:
            if funct3 == RV32_FUNCT3_FENCE:
                # most fences are no-ops
                if ((inst_DX[31:28] == 0) & (rs1_addr == 0) & (reg_to_wr_DX == 0)):
                    pass
                else:
                    illegal_instruction = intbv(1)[1:]
            elif funct3 == RV32_FUNCT3_FENCE_I:
                if ((inst_DX[31:20] == 0) & (rs1_addr == 0) & (reg_to_wr_DX == 0)):
                    fence_i = intbv(1)[1:]
                else:
                    illegal_instruction = intbv(1)[1:]
            else:
                illegal_instruction = intbv(1)[1:]

        elif opcode == RV32_OP_IMM:
            alu_op = alu_op_arith
            wr_reg_unkilled_DX = intbv(1)[1:]

        elif opcode == RV32_OP:
            uses_rs2 = intbv(1)[1:]
            src_b_sel = SRC_B_RS2
            alu_op = alu_op_arith
            wr_reg_unkilled_DX = intbv(1)[1:]
            if (funct7 == RV32_FUNCT7_MUL_DIV):
                uses_md_unkilled = intbv(1)[1:]
                wb_src_sel_DX = WB_SRC_MD

        elif opcode == RV32_SYSTEM:
            wb_src_sel_DX = WB_SRC_CSR
            wr_reg_unkilled_DX = (funct3 != RV32_FUNCT3_PRIV)
            if funct3 == RV32_FUNCT3_PRIV:
                if ((rs1_addr == 0) & (reg_to_wr_DX == 0)):
                    if funct12 == RV32_FUNCT12_ECALL:
                        ecall = intbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_EBREAK:
                        ebreak = intbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_ERET:
                        if (prv == 0):
                            illegal_instruction = intbv(1)[1:]
                        else:
                            eret_unkilled = intbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_WFI:
                        wfi_unkilled_DX = intbv(1)[1:]
                    else:
                        illegal_instruction = intbv(1)[1:]
            elif funct3 == RV32_FUNCT3_CSRRW:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_WRITE
            elif funct3 == RV32_FUNCT3_CSRRS:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_SET
            elif funct3 == RV32_FUNCT3_CSRRC:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_CLEAR
            elif funct3 == RV32_FUNCT3_CSRRWI:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_WRITE
            elif funct3 == RV32_FUNCT3_CSRRSI:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_SET
            elif funct3 == RV32_FUNCT3_CSRRCI:
                if rs1_addr == 0:
                    csr_cmd_unkilled = CSR_READ
                else:
                    csr_cmd_unkilled = CSR_CLEAR
            else:
                illegal_instruction = intbv(1)[1:]

        elif opcode == RV32_AUIPC:
            uses_rs1 = intbv(0)[1:]
            src_a_sel = SRC_A_PC
            imm_type = IMM_U
            wr_reg_unkilled_DX = intbv(1)[1:]

        elif opcode == RV32_LUI:
            uses_rs1 = intbv(0)[1:]
            src_a_sel = SRC_A_ZERO
            imm_type = IMM_U
            wr_reg_unkilled_DX = intbv(1)[1:]

        else:
            illegal_instruction = intbv(1)[1:]

    if (opcode == RV32_OP) & (funct7[5]):
        add_or_sub = ALU_OP_SUB
    else:
        add_or_sub = ALU_OP_ADD

    if (funct7[5]):
        srl_or_sra = ALU_OP_SRA
    else:
        srl_or_sra = ALU_OP_SRL

    md_req_valid = uses_md

    @always_comb
    def mult_div_control():
        md_req_op = MD_OP_MUL
        md_req_in_1_signed = 0
        md_req_in_2_signed = 0
        md_req_out_sel = MD_OUT_LO
        if funct3 == RV32_FUNCT3_MUL:
            pass
        elif funct3 == RV32_FUNCT3_MULH:
            md_req_in_1_signed = 1
            md_req_in_2_signed = 1
            md_req_out_sel = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_MULHSU:
            md_req_in_1_signed = 1
            md_req_out_sel = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_MULHU:
            md_req_out_sel = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_DIV:
            md_req_op = MD_OP_DIV
            md_req_in_1_signed = 1
            md_req_in_2_signed = 1
        elif funct3 == RV32_FUNCT3_DIVU:
            md_req_op = MD_OP_DIV
        elif funct3 == RV32_FUNCT3_REM:
            md_req_op = MD_OP_REM
            md_req_in_1_signed = 1
            md_req_in_2_signed = 1
            md_req_out_sel = MD_OUT_REM
        elif funct3 == RV32_FUNCT3_REMU:
            md_req_op = MD_OP_REM
            md_req_out_sel = MD_OUT_REM

    @always_comb
    def alu_control():
        if funct3 == RV32_FUNCT3_ADD_SUB:
            alu_op_arith = add_or_sub
        elif funct3 == RV32_FUNCT3_SLL:
            alu_op_arith = ALU_OP_SLL
        elif funct3 == RV32_FUNCT3_SLT:
            alu_op_arith = ALU_OP_SLT
        elif funct3 == RV32_FUNCT3_SLTU:
            alu_op_arith = ALU_OP_SLTU
        elif funct3 == RV32_FUNCT3_XOR:
            alu_op_arith = ALU_OP_XOR
        elif funct3 == RV32_FUNCT3_SRA_SRL:
            alu_op_arith = srl_or_sra
        elif funct3 == RV32_FUNCT3_OR:
            alu_op_arith = ALU_OP_OR
        elif funct3 == RV32_FUNCT3_AND:
            alu_op_arith = ALU_OP_AND
        else:
            alu_op_arith = ALU_OP_ADD

    branch_taken = branch_taken_unkilled & ~kill_DX
    jal = jal_unkilled & ~kill_DX
    jalr = jalr_unkilled & ~kill_DX
    eret = eret_unkilled & ~kill_DX
    dmem_en = dmem_en_unkilled & ~kill_DX
    dmem_wen = dmem_wen_unkilled & ~kill_DX
    wr_reg_DX = wr_reg_unkilled_DX & ~kill_DX
    uses_md = uses_md_unkilled & ~kill_DX
    wfi_DX = wfi_unkilled_DX & ~kill_DX
    redirect = branch_taken | jal | jalr | eret

    if kill_DX:
        csr_cmd = CSR_IDLE
    else:
        csr_cmd = csr_cmd_unkilled

    @always_comb
    def exception_interrupt_control():
        if (exception | interrupt_taken):
            PC_src_sel = PC_HANDLER
        elif (replay_IF | (stall_IF & ~imem_wait)):
            PC_src_sel = PC_REPLAY
        elif (eret):
            PC_src_sel = PC_EPC
        elif (branch_taken):
            PC_src_sel = PC_BRANCH_TARGET
        elif (jal):
            PC_src_sel = PC_JAL_TARGET
        elif (jalr):
            PC_src_sel = PC_JALR_TARGET
        else:
            PC_src_sel = PC_PLUS_FOUR

    # WB stage ctrl

    @always(clk.posedge)
    def WB_stage():
        if reset:
            prev_killed_WB = 0
            had_ex_WB = 0
            wr_reg_unkilled_WB = 0
            store_in_WB = 0
            dmem_en_WB = 0
            uses_md_WB = 0
            wfi_unkilled_WB = 0
        elif not stall_WB:
            prev_killed_WB = killed_DX
            had_ex_WB = ex_DX
            wr_reg_unkilled_WB = wr_reg_DX
            wb_src_sel_WB = wb_src_sel_DX
            prev_ex_code_WB = ex_code_DX
            reg_to_wr_WB = reg_to_wr_DX
            store_in_WB = dmem_wen
            dmem_en_WB = dmem_en
            uses_md_WB = uses_md
            wfi_unkilled_WB = wfi_DX

    # WFI handling
    # can't be killed while in WB stage
    active_wfi_WB = ~prev_killed_WB & wfi_unkilled_WB & ~(interrupt_taken | interrupt_pending)

    kill_WB = stall_WB | ex_WB
    stall_WB = ((dmem_wait & dmem_en_WB) | (uses_md_WB & ~md_resp_valid) | active_wfi_WB) & ~exception
    dmem_access_exception = dmem_badmem_e
    ex_WB = had_ex_WB | dmem_access_exception
    killed_WB = prev_killed_WB | kill_WB

    @always_comb
    def exception_control():
        ex_code_WB = prev_ex_code_WB
        if not had_ex_WB:
            if dmem_access_exception:
                if wr_reg_unkilled_WB:
                    ex_code_WB = ECODE_LOAD_ADDR_MISALIGNED
                else:
                    ex_code_WB = ECODE_STORE_AMO_ADDR_MISALIGNED

    exception_WB = ex_WB
    exception_code_WB = ex_code_WB
    wr_reg_WB = wr_reg_unkilled_WB & ~kill_WB
    retire_WB = not (kill_WB | killed_WB)

    # Hazard logic

    load_in_WB = dmem_en_WB & (not store_in_WB)

    raw_rs1 = wr_reg_WB & (rs1_addr == reg_to_wr_WB) & (rs1_addr != 0) & uses_rs1
    bypass_rs1 = ~load_in_WB & raw_rs1

    raw_rs2 = wr_reg_WB & (rs2_addr == reg_to_wr_WB) & (rs2_addr != 0) & uses_rs2
    bypass_rs2 = ~load_in_WB & raw_rs2

    raw_on_busy_md = uses_md_WB & (raw_rs1 | raw_rs2) & ~md_resp_valid
    load_use = load_in_WB & (raw_rs1 | raw_rs2)

    return IF_stage, DX_stage, DX_stage_comb, control, alu_control,
    mult_div_control, exception_control, exception_interrupt_control, WB_stage
