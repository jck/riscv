from myhdl import always_comb, modbv, concat, block, Signal, always

from riscv.control_constants import *
from riscv.csr_constants import *
from riscv.alu_constants import *
from riscv.opcode_constants import *
from riscv.md_constants import *


@block
def controller(clock, reset, inst_DX, imem_wait, imem_badmem_e, dmem_wait, dmem_badmem_e, cmp_true, prv, PC_src_sel,
               imm_type, bypass_rs1, bypass_rs2, src_a_sel, src_b_sel, alu_op, dmem_en, dmem_wen, dmem_size, dmem_type,
               md_req_valid, md_req_ready, md_req_in_1_signed, md_req_in_2_signed, md_req_op, md_req_out_sel,
               md_resp_valid, eret, csr_cmd, csr_imm_sel, illegal_csr_access, interrupt_pending, interrupt_taken,
               wr_reg_WB, reg_to_wr_WB, wb_src_sel_WB, stall_IF, kill_IF, stall_DX, kill_DX, stall_WB, kill_WB,
               exception_WB, exception_code_WB, retire_WB):

    # IF stage ctrl pipeline registers
    replay_IF = Signal(False)

    # IF stage ctrl signals
    ex_IF = Signal(False)

    # DX stage ctrl pipeline registers
    had_ex_DX, prev_killed_DX = [Signal(False) for _ in range(2)]

    opcode = inst_DX(7, 0)
    funct7 = inst_DX(32, 25)
    funct12 = inst_DX(32, 20)
    funct3 = inst_DX(15, 12)
    rs1_addr = inst_DX(20, 15)
    rs2_addr = inst_DX(23, 20)
    reg_to_wr_DX = inst_DX(12, 7)

    illegal_instruction, ebreak, ecall, eret_unkilled, fence_i = [Signal(False) for _ in range(5)]
    add_or_sub, srl_or_sra, alu_op_arith = [Signal(modbv(0)[ALU_OP_WIDTH:]) for _ in range(3)]

    branch_taken_unkilled, branch_taken, dmem_en_unkilled, dmem_wen_unkilled = [Signal(False) for _ in range(4)]
    jal_unkilled, jal, jalr_unkilled, jalr, redirect, wr_reg_unkilled_DX = [Signal(False) for _ in range(6)]
    wr_reg_DX = Signal(False)
    wb_src_sel_DX = Signal(modbv(0)[WB_SRC_SEL_WIDTH:])
    new_ex_DX = Signal(False)
    ex_DX = Signal(False)
    ex_code_DX = Signal(modbv(0)[ECODE_WIDTH:])
    killed_DX, uses_md_unkilled, uses_md, wfi_unkilled_DX, wfi_DX = [Signal(False) for _ in range(5)]
    csr_cmd_unkilled = Signal(modbv(0)[CSR_CMD_WIDTH:])

    # WB stage ctrl pipeline registers

    wr_reg_unkilled_WB = Signal(False)
    had_ex_WB = Signal(False)
    prev_ex_code_WB = Signal(modbv(0)[ECODE_WIDTH:])
    store_in_WB, dmem_en_WB, prev_killed_WB, uses_md_WB, wfi_unkilled_WB = [Signal(False) for _ in range(5)]

    # WB stage ctrl signals
    ex_WB = Signal(False)
    ex_code_WB = Signal(modbv(0)[ECODE_WIDTH:])
    dmem_access_exception = Signal(False)
    exception, killed_WB, load_in_WB, active_wfi_WB = [Signal(False) for _ in range(4)]

    # Hazard signals
    load_use, uses_rs1, uses_rs2, raw_rs1, raw_rs2, raw_on_busy_md = [Signal(False) for _ in range(6)]

    # If Stage control
    @always(clock.posedge)
    def IF_stage():
        if reset:
            replay_IF.next = modbv(1)[1:]
        else:
            replay_IF.next = (redirect & imem_wait) | (fence_i & store_in_WB)

    @always_comb
    def assign_1():
        kill_IF.next = stall_IF | ex_IF | ex_DX | ex_WB | redirect | replay_IF | interrupt_taken
        kill_DX.next = stall_DX | ex_DX | ex_WB | interrupt_taken

    @always_comb
    def assign_2():
        stall_DX.next = stall_WB | (
            (load_use | raw_on_busy_md | (fence_i & store_in_WB) | (uses_md_unkilled & ~md_req_ready)) & ~(
                ex_DX | ex_WB | interrupt_taken))
        new_ex_DX.next = ebreak | ecall | illegal_instruction | illegal_csr_access

    @always_comb
    def assign_3():
        stall_IF.next = stall_DX | ((imem_wait & ~redirect) & ~(ex_WB | interrupt_taken))
        ex_IF.next = imem_badmem_e & ~imem_wait & ~redirect & ~replay_IF
        exception.next = ex_WB
        # interrupts kill IF, DX instructions -- WB may commit
        # Exceptions never show up falsely due to hazards -- don't get exceptions on stall
        killed_DX.next = prev_killed_DX | kill_DX
        ex_DX.next = had_ex_DX | new_ex_DX

    # DX Stage control

    @always(clock.posedge)
    def DX_stage():
        if reset:
            had_ex_DX.next = 0
            prev_killed_DX.next = 0
        elif ~stall_DX:
            had_ex_DX.next = ex_IF
            prev_killed_DX.next = kill_IF

    @always_comb
    def DX_stage_comb():
        ex_code_DX.next = ECODE_INST_ADDR_MISALIGNED
        if had_ex_DX:
            ex_code_DX.next = ECODE_INST_ADDR_MISALIGNED
        elif illegal_instruction:
            ex_code_DX.next = ECODE_ILLEGAL_INST
        elif illegal_csr_access:
            ex_code_DX.next = ECODE_ILLEGAL_INST
        elif ebreak:
            ex_code_DX.next = ECODE_BREAKPOINT
        elif ecall:
            ex_code_DX.next = ECODE_ECALL_FROM_U + prv

        dmem_size.next = concat(modbv(0)[1:], funct3[1:0])
        dmem_type.next = funct3

    @always_comb
    def control():
        illegal_instruction.next = modbv(0)[1:]
        csr_cmd_unkilled.next = CSR_IDLE
        csr_imm_sel.next = funct3[2]
        ecall.next = modbv(0)[1:]
        ebreak.next = modbv(0)[1:]
        eret_unkilled.next = modbv(0)[1:]
        fence_i.next = modbv(0)[1:]
        branch_taken_unkilled.next = modbv(0)[1:]
        jal_unkilled.next = modbv(0)[1:]
        jalr_unkilled.next = modbv(0)[1:]
        uses_rs1.next = modbv(1)[1:]
        uses_rs2.next = modbv(0)[1:]
        imm_type.next = IMM_I
        src_a_sel.next = SRC_A_RS1
        src_b_sel.next = SRC_B_IMM
        alu_op.next = ALU_OP_ADD
        dmem_en_unkilled.next = modbv(0)[1:]
        dmem_wen_unkilled.next = modbv(0)[1:]
        wr_reg_unkilled_DX.next = modbv(0)[1:]
        wb_src_sel_DX.next = WB_SRC_ALU
        uses_md_unkilled.next = modbv(0)[1:]
        wfi_unkilled_DX.next = modbv(0)[1:]

        if opcode == RV32_LOAD:
            dmem_en_unkilled.next = modbv(1)[1:]
            wr_reg_unkilled_DX.next = modbv(1)[1:]
            wb_src_sel_DX.next = WB_SRC_MEM

        elif opcode == RV32_STORE:
            uses_rs2.next = modbv(1)[1:]
            imm_type.next = IMM_S
            dmem_en_unkilled.next = modbv(1)[1:]
            dmem_wen_unkilled.next = modbv(1)[1:]

        elif opcode == RV32_BRANCH:
            uses_rs2.next = modbv(1)[1:]
            branch_taken_unkilled.next = cmp_true
            src_b_sel.next = SRC_B_RS2

            if funct3 == RV32_FUNCT3_BEQ:
                alu_op.next = ALU_OP_SEQ
            elif funct3 == RV32_FUNCT3_BNE:
                alu_op.next = ALU_OP_SNE
            elif funct3 == RV32_FUNCT3_BLT:
                alu_op.next = ALU_OP_SLT
            elif funct3 == RV32_FUNCT3_BLTU:
                alu_op.next = ALU_OP_SLTU
            elif funct3 == RV32_FUNCT3_BGE:
                alu_op.next = ALU_OP_SGE
            elif funct3 == RV32_FUNCT3_BGEU:
                alu_op.next = ALU_OP_SGEU
            else:
                illegal_instruction.next = modbv(1)[1:]

        elif opcode == RV32_JAL:
            jal_unkilled.next = modbv(1)[1:]
            uses_rs1.next = modbv(0)[1:]
            src_a_sel.next = SRC_A_PC
            src_b_sel.next = SRC_B_FOUR
            wr_reg_unkilled_DX.next = modbv(1)[1:]

        elif opcode == RV32_JALR:
            illegal_instruction.next = (funct3 != 0)
            jalr_unkilled.next = modbv(1)[1:]
            src_a_sel.next = SRC_A_PC
            src_b_sel.next = SRC_B_FOUR
            wr_reg_unkilled_DX.next = modbv(1)[1:]

        elif opcode == RV32_MISC_MEM:
            if funct3 == RV32_FUNCT3_FENCE:
                # most fences are no-ops
                if (inst_DX[31:28] == 0) & (rs1_addr == 0) & (reg_to_wr_DX == 0):
                    pass
                else:
                    illegal_instruction.next = modbv(1)[1:]
            elif funct3 == RV32_FUNCT3_FENCE_I:
                if (inst_DX[31:20] == 0) & (rs1_addr == 0) & (reg_to_wr_DX == 0):
                    fence_i.next = modbv(1)[1:]
                else:
                    illegal_instruction.next = modbv(1)[1:]
            else:
                illegal_instruction.next = modbv(1)[1:]

        elif opcode == RV32_OP_IMM:
            alu_op.next = alu_op_arith
            wr_reg_unkilled_DX.next = modbv(1)[1:]

        elif opcode == RV32_OP:
            uses_rs2.next = modbv(1)[1:]
            src_b_sel.next = SRC_B_RS2
            alu_op.next = alu_op_arith
            wr_reg_unkilled_DX.next = modbv(1)[1:]
            if funct7 == RV32_FUNCT7_MUL_DIV:
                uses_md_unkilled.next = modbv(1)[1:]
                wb_src_sel_DX.next = WB_SRC_MD

        elif opcode == RV32_SYSTEM:
            wb_src_sel_DX.next = WB_SRC_CSR
            wr_reg_unkilled_DX.next = (funct3 != RV32_FUNCT3_PRIV)
            if funct3 == RV32_FUNCT3_PRIV:
                if (rs1_addr == 0) and (reg_to_wr_DX == 0):
                    if funct12 == RV32_FUNCT12_ECALL:
                        ecall.next = modbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_EBREAK:
                        ebreak.next = modbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_ERET:
                        if prv == 0:
                            illegal_instruction.next = modbv(1)[1:]
                        else:
                            eret_unkilled.next = modbv(1)[1:]
                    elif funct12 == RV32_FUNCT12_WFI:
                        wfi_unkilled_DX.next = modbv(1)[1:]
                    else:
                        illegal_instruction.next = modbv(1)[1:]
            elif funct3 == RV32_FUNCT3_CSRRW:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_WRITE
            elif funct3 == RV32_FUNCT3_CSRRS:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_SET
            elif funct3 == RV32_FUNCT3_CSRRC:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_CLEAR
            elif funct3 == RV32_FUNCT3_CSRRWI:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_WRITE
            elif funct3 == RV32_FUNCT3_CSRRSI:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_SET
            elif funct3 == RV32_FUNCT3_CSRRCI:
                if rs1_addr == 0:
                    csr_cmd_unkilled.next = CSR_READ
                else:
                    csr_cmd_unkilled.next = CSR_CLEAR
            else:
                illegal_instruction.next = modbv(1)[1:]

        elif opcode == RV32_AUIPC:
            uses_rs1.next = modbv(0)[1:]
            src_a_sel.next = SRC_A_PC
            imm_type.next = IMM_U
            wr_reg_unkilled_DX.next = modbv(1)[1:]

        elif opcode == RV32_LUI:
            uses_rs1.next = modbv(0)[1:]
            src_a_sel.next = SRC_A_ZERO
            imm_type.next = IMM_U
            wr_reg_unkilled_DX.next = modbv(1)[1:]

        else:
            illegal_instruction.next = modbv(1)[1:]

        if (opcode == RV32_OP) and (funct7[5]):
            add_or_sub.next = ALU_OP_SUB
        else:
            add_or_sub.next = ALU_OP_ADD

        if funct7[5]:
            srl_or_sra.next = ALU_OP_SRA
        else:
            srl_or_sra.next = ALU_OP_SRL

        md_req_valid.next = uses_md

    @always_comb
    def mult_div_control():
        md_req_op.next = MD_OP_MUL
        md_req_in_1_signed.next = 0
        md_req_in_2_signed.next = 0
        md_req_out_sel.next = MD_OUT_LO
        if funct3 == RV32_FUNCT3_MUL:
            pass
        elif funct3 == RV32_FUNCT3_MULH:
            md_req_in_1_signed.next = 1
            md_req_in_2_signed.next = 1
            md_req_out_sel.next = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_MULHSU:
            md_req_in_1_signed.next = 1
            md_req_out_sel.next = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_MULHU:
            md_req_out_sel.next = MD_OUT_HI
        elif funct3 == RV32_FUNCT3_DIV:
            md_req_op.next = MD_OP_DIV
            md_req_in_1_signed.next = 1
            md_req_in_2_signed.next = 1
        elif funct3 == RV32_FUNCT3_DIVU:
            md_req_op.next = MD_OP_DIV
        elif funct3 == RV32_FUNCT3_REM:
            md_req_op.next = MD_OP_REM
            md_req_in_1_signed.next = 1
            md_req_in_2_signed.next = 1
            md_req_out_sel.next = MD_OUT_REM
        elif funct3 == RV32_FUNCT3_REMU:
            md_req_op.next = MD_OP_REM
            md_req_out_sel.next = MD_OUT_REM

    @always_comb
    def alu_control():
        if funct3 == RV32_FUNCT3_ADD_SUB:
            alu_op_arith.next = add_or_sub
        elif funct3 == RV32_FUNCT3_SLL:
            alu_op_arith.next = ALU_OP_SLL
        elif funct3 == RV32_FUNCT3_SLT:
            alu_op_arith.next = ALU_OP_SLT
        elif funct3 == RV32_FUNCT3_SLTU:
            alu_op_arith.next = ALU_OP_SLTU
        elif funct3 == RV32_FUNCT3_XOR:
            alu_op_arith.next = ALU_OP_XOR
        elif funct3 == RV32_FUNCT3_SRA_SRL:
            alu_op_arith.next = srl_or_sra
        elif funct3 == RV32_FUNCT3_OR:
            alu_op_arith.next = ALU_OP_OR
        elif funct3 == RV32_FUNCT3_AND:
            alu_op_arith.next = ALU_OP_AND
        else:
            alu_op_arith.next = ALU_OP_ADD

        branch_taken.next = branch_taken_unkilled & ~kill_DX
        jal.next = jal_unkilled & ~kill_DX
        jalr.next = jalr_unkilled & ~kill_DX
        eret.next = eret_unkilled & ~kill_DX
        dmem_en.next = dmem_en_unkilled & ~kill_DX
        dmem_wen.next = dmem_wen_unkilled & ~kill_DX
        wr_reg_DX.next = wr_reg_unkilled_DX & ~kill_DX
        uses_md.next = uses_md_unkilled & ~kill_DX
        wfi_DX.next = wfi_unkilled_DX & ~kill_DX

        if kill_DX:
            csr_cmd.next = CSR_IDLE
        else:
            csr_cmd.next = csr_cmd_unkilled

    @always_comb
    def assign_4():
        redirect.next = branch_taken | jal | jalr | eret

    @always_comb
    def exception_interrupt_control():
        if exception | interrupt_taken:
            PC_src_sel.next = PC_HANDLER
        elif replay_IF | (stall_IF & ~imem_wait):
            PC_src_sel.next = PC_REPLAY
        elif eret:
            PC_src_sel.next = PC_EPC
        elif branch_taken:
            PC_src_sel.next = PC_BRANCH_TARGET
        elif jal:
            PC_src_sel.next = PC_JAL_TARGET
        elif jalr:
            PC_src_sel.next = PC_JALR_TARGET
        else:
            PC_src_sel.next = PC_PLUS_FOUR

    # WB stage ctrl

    @always(clock.posedge)
    def WB_stage():
        if reset:
            prev_killed_WB.next = 0
            had_ex_WB.next = 0
            wr_reg_unkilled_WB.next = 0
            store_in_WB.next = 0
            dmem_en_WB.next = 0
            uses_md_WB.next = 0
            wfi_unkilled_WB.next = 0
        elif not stall_WB:
            prev_killed_WB.next = killed_DX
            had_ex_WB.next = ex_DX
            wr_reg_unkilled_WB.next = wr_reg_DX
            wb_src_sel_WB.next = wb_src_sel_DX
            prev_ex_code_WB.next = ex_code_DX
            reg_to_wr_WB.next = reg_to_wr_DX
            store_in_WB.next = dmem_wen
            dmem_en_WB.next = dmem_en
            uses_md_WB.next = uses_md
            wfi_unkilled_WB.next = wfi_DX

    # WFI handling
    # can't be killed while in WB stage
    @always_comb
    def wfi_handling_1():
        active_wfi_WB.next = ~prev_killed_WB & wfi_unkilled_WB & ~(interrupt_taken | interrupt_pending)
        kill_WB.next = stall_WB | ex_WB
        dmem_access_exception.next = dmem_badmem_e

    @always_comb
    def wfi_handling_2():
        stall_WB.next = ((dmem_wait & dmem_en_WB) | (uses_md_WB & ~md_resp_valid) | active_wfi_WB) & ~exception
        ex_WB.next = had_ex_WB | dmem_access_exception
        killed_WB.next = prev_killed_WB | kill_WB

    @always_comb
    def exception_control():

        ex_code_WB.next = prev_ex_code_WB
        if not had_ex_WB:
            if dmem_access_exception:
                if wr_reg_unkilled_WB:
                    ex_code_WB.next = ECODE_LOAD_ADDR_MISALIGNED
                else:
                    ex_code_WB.next = ECODE_STORE_AMO_ADDR_MISALIGNED

        exception_WB.next = ex_WB
        exception_code_WB.next = ex_code_WB
        wr_reg_WB.next = wr_reg_unkilled_WB & ~kill_WB
        retire_WB.next = not (kill_WB | killed_WB)

    @always_comb
    def hazard_logic_1():
        # Hazard logic
        load_in_WB.next = dmem_en_WB & (not store_in_WB)
        raw_rs1.next = wr_reg_WB & (rs1_addr == reg_to_wr_WB) & (rs1_addr != 0) & uses_rs1
        raw_rs2.next = wr_reg_WB & (rs2_addr == reg_to_wr_WB) & (rs2_addr != 0) & uses_rs2

    @always_comb
    def hazard_logic_2():
        bypass_rs1.next = ~load_in_WB & raw_rs1
        bypass_rs2.next = ~load_in_WB & raw_rs2
        load_use.next = load_in_WB & (raw_rs1 | raw_rs2)
        raw_on_busy_md.next = uses_md_WB & (raw_rs1 | raw_rs2) & ~md_resp_valid

    return IF_stage, DX_stage, DX_stage_comb, control, alu_control, assign_1, assign_2, assign_3, assign_4, \
        mult_div_control, wfi_handling_1, wfi_handling_2, exception_control, exception_interrupt_control, \
        WB_stage, hazard_logic_1, hazard_logic_2
