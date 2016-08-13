from myhdl import block, always_comb, concat, intbv, always, Signal, instances

from riscv.csr_constants import *
from riscv.opcode_constants import *
from riscv.control_constants import *


def reduced_or(input):
    """
    Returns the reduced or of the input
    :param Signal input: Input
    """
    if input:
        return intbv(1)[1:]
    else:
        return intbv(0)[1:]


@block
def csr_file(clock,
             ext_interrupts,
             reset,
             addr,
             cmd,
             wdata,
             prv,
             illegal_access,
             rdata,
             retire,
             exception,
             exception_code,
             eret,
             exception_load_addr,
             exception_PC,
             handler_PC,
             epc,
             interrupt_pending,
             interrupt_taken,
             htif_reset,
             htif_pcr_req_valid,
             htif_pcr_req_ready,
             htif_pcr_req_rw,
             htif_pcr_req_addr,
             htif_pcr_req_data,
             htif_pcr_resp_valid,
             htif_pcr_resp_ready,
             htif_pcr_resp_data):

    HTIF_STATE_IDLE = 0
    HTIF_STATE_WAIT = 1

    htif_rdata = Signal(intbv(0)[HTIF_PCR_WIDTH:])
    htif_resp_data = Signal(intbv(0)[HTIF_PCR_WIDTH:])

    htif_state = Signal(intbv(0)[1:])
    htif_fire = Signal(intbv(0)[1:])
    next_htif_state = Signal(intbv(0)[1:])

    cycle_full = Signal(intbv(0)[CSR_COUNTER_WIDTH:])
    time_full = Signal(intbv(0)[CSR_COUNTER_WIDTH:])
    instret_full = Signal(intbv(0)[CSR_COUNTER_WIDTH:])
    priv_stack = Signal(intbv(0)[5:])

    mtvec = Signal(intbv(0)[XPR_LEN:])
    mie = Signal(intbv(0)[XPR_LEN:])
    mtimecmp = Signal(intbv(0)[XPR_LEN:])
    mscratch = Signal(intbv(0)[XPR_LEN:])
    mepc = Signal(intbv(0)[XPR_LEN:])
    mbadaddr = Signal(intbv(0)[XPR_LEN:])
    mcpuid = Signal(intbv(0)[XPR_LEN:])
    mimpid = Signal(intbv(0)[XPR_LEN:])
    mhartid = Signal(intbv(0)[XPR_LEN:])
    mstatus = Signal(intbv(0)[XPR_LEN:])
    mtdeleg = Signal(intbv(0)[XPR_LEN:])
    mip = Signal(intbv(0)[XPR_LEN:])
    mcause = Signal(intbv(0)[XPR_LEN:])
    to_host = Signal(intbv(0)[XPR_LEN:])
    from_host = Signal(intbv(0)[XPR_LEN:])

    wdata_internal = Signal(intbv(0)[XPR_LEN:])
    interrupt_code = Signal(intbv(0)[ECODE_WIDTH:])

    mtip = Signal(intbv(0)[1:])
    msip = Signal(intbv(0)[1:])
    mint = Signal(intbv(0)[1:])
    ie = Signal(intbv(0)[1:])

    host_wen = Signal(intbv(0)[1:])
    system_en = Signal(intbv(0)[1:])
    system_wen = Signal(intbv(0)[1:])
    wen_internal = Signal(intbv(0)[1:])
    illegal_region = Signal(intbv(0)[1:])
    defined = Signal(intbv(0)[1:])

    uinterrupt = Signal(intbv(0)[1:])
    minterrupt = Signal(intbv(0)[1:])
    code_imem = Signal(intbv(0)[1:])
    mtimer_expired = Signal(intbv(0)[1:])

    mtime_full = Signal(intbv(0)[CSR_COUNTER_WIDTH:])
    mecode = Signal(intbv(0)[ECODE_WIDTH:])

    padded_prv = Signal(intbv(0)[XPR_LEN:])

    @always_comb
    def assign_1():
        padded_prv.next = prv

    @always_comb
    def csr_setup():

        handler_PC.next = mtvec + (padded_prv << 5)

        prv.next = priv_stack[2:1]
        ie.next = priv_stack[0]

        host_wen.next = (htif_state == HTIF_STATE_IDLE) & htif_pcr_req_valid & htif_pcr_req_rw
        system_en.next = cmd[2]
        system_wen.next = cmd[1] | cmd[0]
        wen_internal.next = host_wen | system_wen

        illegal_region.next = (system_wen & (addr[12:10] == 3)) | (system_en & addr[10:8] > prv)
        illegal_access.next = illegal_region | (system_en & ~defined)

        wdata_internal.next = wdata
        if host_wen:
            wdata_internal.next = htif_pcr_req_data
        elif system_wen:
            if cmd == CSR_SET:
                wdata_internal.next = rdata | wdata
            elif cmd == CSR_CLEAR:
                wdata_internal.next = rdata & ~wdata
            else:
                wdata_internal.next = wdata

        uinterrupt.next = intbv(0)[1:]
        interrupt_pending.next = reduced_or(mip)
        minterrupt.next = reduced_or(mie & mip)

    @always_comb
    def interrupt_setup():
        interrupt_code.next = ICODE_TIMER
        if prv.next == PRV_U:
            interrupt_taken.next = (ie & uinterrupt) | minterrupt
        elif prv.next == PRV_M:
            interrupt_taken.next = (ie & minterrupt)
        else:
            interrupt_taken.next = intbv(1)[1:]

    @always(clock.posedge)
    def htif_setup():
        if htif_reset:
            htif_state.next = HTIF_STATE_IDLE
        else:
            htif_state.next = next_htif_state
        if htif_fire:
            htif_resp_data.next = htif_rdata

    @always_comb
    def htif_comb():
        htif_fire.next = intbv(0)[1:]
        next_htif_state.next = htif_state
        if htif_state == HTIF_STATE_IDLE:
            if htif_pcr_req_valid:
                htif_fire.next = intbv(1)[1:]
                next_htif_state.next = HTIF_STATE_WAIT
        elif htif_state == HTIF_STATE_WAIT:
            if htif_pcr_resp_ready:
                next_htif_state.next = HTIF_STATE_IDLE

        htif_pcr_req_ready.next = (htif_state == HTIF_STATE_IDLE)
        htif_pcr_resp_valid.next = (htif_state == HTIF_STATE_WAIT)
        htif_pcr_resp_data.next = htif_resp_data

        mcpuid.next = (1 << 20) | (1 << 8)
        mimpid.next = intbv(int('8000', 16))[32:]
        mhartid.next = 0

    @always(clock.posedge)
    def priv_stack_setup():
        if reset:
            priv_stack.next = intbv(int('000110', 2))[6:]
        elif wen_internal & addr == CSR_ADDR_MSTATUS:
            priv_stack.next = wdata_internal[5:0]
        elif exception:
            priv_stack.next = concat(priv_stack[3:0], intbv(int('110', 2))[3:])
        elif eret:
            priv_stack.next = concat(intbv(int('001', 2))[3:], priv_stack[6:3])

        epc.next = mepc

        mstatus.next = concat(intbv(0)[26:], priv_stack)
        mtdeleg.next = 0
        mtimer_expired.next = (mtimecmp == mtime_full[XPR_LEN:])

    @always(clock.posedge)
    def mtimer_setup():
        if reset:
            mtip.next = 0
            msip.next = 0
        else:
            if mtimer_expired:
                mtip.next = 1
            if wen_internal & addr == CSR_ADDR_MTIMECMP:
                mtip.next = 0
            if wen_internal & addr == CSR_ADDR_MIP:
                mtip.next = wdata_internal[7]
                msip.next = wdata_internal[3]

        mip.next = concat(ext_interrupts, mtip, intbv(0)[3:], msip, intbv(0)[3:])

    @always(clock.posedge)
    def wen_setup():
        if reset:
            mie.next = 0
        elif wen_internal & addr == CSR_ADDR_MIE:
            mie.next = wdata_internal

    @always(clock.posedge)
    def exception_setup():
        if interrupt_taken:
            mepc.next = (exception_PC & concat(intbv(1)[30:], intbv(0)[2:])) + intbv(int('4', 16))[XPR_LEN:]
        if exception:
            mepc.next = exception_PC & concat(intbv(1)[30:], intbv(0)[2:])
        if wen_internal & addr == CSR_ADDR_MEPC:
            mepc.next = wdata_internal & concat(intbv(1)[30:], intbv(0)[2:])

    @always(clock.posedge)
    def interrupt_exception_setup():
        if reset:
            mecode.next = 0
            mint.next = 0
        elif wen_internal & addr == CSR_ADDR_MCAUSE:
            mecode.next = wdata_internal[4:0]
            mint.next = wdata_internal[31]
        else:
            if interrupt_taken:
                mecode.next = interrupt_code
                mint.next = intbv(1)[1:]
            elif exception:
                mecode.next = exception_code
                mint.next = intbv(1)[1:]

    @always_comb
    def assign_2():
        mcause.next = concat(mint, intbv(0)[27:], mecode)
        code_imem.next = (exception_code == ECODE_INST_ADDR_MISALIGNED) | (exception_code == ECODE_INST_ADDR_MISALIGNED)

    @always(clock.posedge)
    def exception_load():
        if exception:
            if code_imem:
                mbadaddr.next = exception_PC
            else:
                mbadaddr.next = exception_load_addr
        if wen_internal & addr == CSR_ADDR_MBADADDR:
            mbadaddr.next = wdata_internal

    @always_comb
    def host_setup():
        if htif_pcr_req_addr == CSR_ADDR_TO_HOST:
            htif_rdata.next = to_host
        elif htif_pcr_req_addr == CSR_ADDR_FROM_HOST:
            htif_rdata.next = from_host
        else:
            htif_rdata.next = 0

    @always_comb
    def csr_addr_logic():
        if addr == CSR_ADDR_CYCLE:
            rdata.next = cycle_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_TIME:
            rdata.next = time_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_INSTRET:
            rdata.next = instret_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_CYCLEH:
            rdata.next = cycle_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_TIMEH:
            rdata.next = time_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_INSTRETH:
            rdata.next = instret_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MCPUID:
            rdata.next = mcpuid
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MIMPID:
            rdata.next = mimpid
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MHARTID:
            rdata.next = mhartid
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MSTATUS:
            rdata.next = mstatus
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MTVEC:
            rdata.next = mtvec
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MTDELEG:
            rdata.next = mtdeleg
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MIE:
            rdata.next = mie
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MTIMECMP:
            rdata.next = mtimecmp
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MTIME:
            rdata.next = mtime_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MTIMEH:
            rdata.next = mtime_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MSCRATCH:
            rdata.next = mscratch
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MEPC:
            rdata.next = mepc
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MCAUSE:
            rdata.next = mcause
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MBADADDR:
            rdata.next = mbadaddr
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_MIP:
            rdata.next = mip
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_CYCLEW:
            rdata.next = cycle_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_TIMEW:
            rdata.next = time_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_INSTRETW:
            rdata.next = instret_full[XPR_LEN:]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_CYCLEHW:
            rdata.next = cycle_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_TIMEHW:
            rdata.next = time_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_INSTRETHW:
            rdata.next = instret_full[2 * XPR_LEN:XPR_LEN]
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_TO_HOST:
            rdata.next = to_host
            defined.next = intbv(1)[1:]
        elif addr == CSR_ADDR_FROM_HOST:
            rdata.next = from_host
            defined.next = intbv(1)[1:]
        else:
            rdata.next = 0
            defined.next = intbv(0)[1:]

    @always(clock.posedge)
    def csr_seq_logic():
        if reset:
            cycle_full.next = 0
            time_full.next = 0
            instret_full.next = 0
            mtime_full.next = 0
            to_host.next = 0
            from_host.next = 0
            mtvec.next = intbv(int('100', 16))[12:]
            mtimecmp.next = 0
            mscratch.next = 0
        else:
            cycle_full.next = cycle_full + 1
            time_full.next = time_full + 1
            if retire:
                instret_full.next = instret_full + 1
            mtime_full.next = mtime_full + 1
            if wen_internal:
                if addr == CSR_ADDR_CYCLE:
                    cycle_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_TIME:
                    time_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_INSTRET:
                    instret_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_CYCLEH:
                    cycle_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TIMEH:
                    time_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_INSTRETH:
                    instret_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_MTVEC:
                    mtvec.next = wdata_internal & concat(intbv(1)[30:], intbv(0)[2:])
                elif addr == CSR_ADDR_MTIMECMP:
                    mtimecmp.next = wdata_internal
                elif addr == CSR_ADDR_MTIME:
                    mtime_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_MTIMEH:
                    mtime_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_MSCRATCH:
                    mscratch.next = wdata_internal
                elif addr == CSR_ADDR_CYCLEW:
                    cycle_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_TIMEW:
                    time_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_INSTRETW:
                    instret_full.next[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_CYCLEHW:
                    cycle_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TIMEHW:
                    time_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_INSTRETHW:
                    instret_full.next[2 * XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TO_HOST:
                    to_host.next = wdata_internal
                elif addr == CSR_ADDR_FROM_HOST:
                    from_host.next = wdata_internal
            if htif_fire & htif_pcr_req_addr == CSR_ADDR_TO_HOST & ~system_wen:
                to_host.next = 0

    return instances
