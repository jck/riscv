from myhdl import block, always_comb, concat, modbv

from riscv.opcode_constants import *
from riscv.opcode_constants import *
from riscv.control_constants import *

def reduced_or(input):
    """
    Returns the reduced or of the input
    :param Signal input: Input 
    :param modbv output: Ouput 
    """
    out = modbv(0)[1:]
    for i in range(input._nrbits):
        out = out | input[i]
    return out

@block
def csr_file(clk,
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

    htif_rdata     = modbv(0)[HTIF_PCR_WIDTH-1:]
    htif_resp_data = modbv(0)[HTIF_PCR_WIDTH-1:]

    htif_state      = modbv(0)[1:]
    htif_fire       = modbv(0)[1:]
    next_htif_state = modbv(0)[1:]

    cycle_full   = modbv(0)[CSR_COUNTER_WIDTH-1:]
    time_full    = modbv(0)[CSR_COUNTER_WIDTH-1:]
    instret_full = modbv(0)[CSR_COUNTER_WIDTH-1:]
    priv_stack   = modbv(0)[5:]

    mtvec      = modbv(0)[XPR_LEN-1:]
    mie        = modbv(0)[XPR_LEN-1:]
    mtimecmp   = modbv(0)[XPR_LEN-1:]
    mscratch   = modbv(0)[XPR_LEN-1:]
    mepc       = modbv(0)[XPR_LEN-1:]
    mbadaddr   = modbv(0)[XPR_LEN-1:]
    mcpuid     = modbv(0)[XPR_LEN-1:]
    mimpid     = modbv(0)[XPR_LEN-1:]
    mhartid    = modbv(0)[XPR_LEN-1:]
    mstatus    = modbv(0)[XPR_LEN-1:]
    mtdeleg    = modbv(0)[XPR_LEN-1:]
    mip        = modbv(0)[XPR_LEN-1:]
    mcause     = modbv(0)[XPR_LEN-1:]
    to_host    = modbv(0)[XPR_LEN-1:]
    from_host  = modbv(0)[XPR_LEN-1:]

    wdata_internal = modbv(0)[XPR_LEN-1:]
    interrupt_code = modbv(0)[ECODE_WIDTH-1:]

    mtip = modbv(0)[1:]
    msip = modbv(0)[1:]
    mint = modbv(0)[1:]
    ie   = modbv(0)[1:]

    host_wen       = modbv(0)[1:]
    system_en      = modbv(0)[1:]
    system_wen     = modbv(0)[1:]
    wen_internal   = modbv(0)[1:]
    illegal_region = modbv(0)[1:]
    defined        = modbv(0)[1:]

    uinterrupt     = modbv(0)[1:]
    minterrupt     = modbv(0)[1:]
    code_imem      = modbv(0)[1:]
    mtimer_expired = modbv(0)[1:]

    mtime_full = modbv(0)[CSR_COUNTER_WIDTH-1:]
    mecode     = modbv(0)[ECODE_WIDTH-1:]

    padded_prv = prv
    handler_PC.next = mtvec + (padded_prv << 5)

    prv = priv_stack[2:1]
    ie = priv_stack[0]

    host_wen = (htif_state == HTIF_STATE_IDLE) & htif_pcr_req_valid & htif_pcr_req_rw
    system_en = cmd[2]
    system_wen = cmd[1] | cmd[0]
    wen_internal = host_wen | system_wen

    illegal_region = (system_wen & (addr[11:10] == 3)) | (system_en & addr[9:8] > prv)
    illegal_access.next = illegal_region | (system_en & ~defined)

    @always_comb
    def csr_setup():
        wdata_internal = wdata
        if host_wen:
            wdata_internal = htif_pcr_req_data
        elif system_wen:
            if cmd == CSR_SET:
                wdata_internal = rdata | wdata
            elif cmd == CSR_CLEAR:
                wdata_internal = rdata & ~wdata
            else:
                wdata_internal = wdata


    uinterrupt = modbv(0)[1:]
    interrupt_pending = reduced_or(mip)
    minterrupt = reduced_or(mie & mip)

    @always_comb
    def interrupt_setup():
        interrupt_code = ICODE_TIMER
        if prv.next == PRV_U:
            interrupt_taken = (ie & uinterrupt) | minterrupt
        elif prv.next == PRV_M:
            interrupt_taken = (ie & minterrupt)
        else:
            interrupt_taken = modbv(1)[1:]

    htif_state 

    htif_fire
    htif_reset

    @always_seq(clk.posedge)
    def htif_setup():
        if htif_reset:
            htif_state = HTIF_STATE_IDLE
        else:
            htif_state = next_htif_state
        if htif_fire:
            htif_resp_data = htif_rdata

    @always_comb
    def htif_comb():
        htif_fire = modbv(0)[1:]
        next_htif_state = htif_state
        if htif_state == HTIF_STATE_IDLE:
            if htif_pcr_req_valid:

                htif_fire = modbv(1)[1:]
                next_htif_state = HTIF_STATE_WAIT
        elif htif_state == HTIF_STATE_WAIT:
            if htif_pcr_resp_ready:
                next_htif_state = HTIF_STATE_IDLE

    htif_pcr_req_ready.next= (htif_state == HTIF_STATE_IDLE)
    htif_pcr_resp_valid.next = (htif_state == HTIF_STATE_WAIT)
    htif_pcr_resp_data.next = htif_resp_data

    mcpuid = (1 << 20) | (1 << 8)
    mimpid = modbv(int('8000', 16))[32:]
    mhartid = 0

    @always_seq(clk.posedge)
    def priv_stack_setup():
        if reset:
            priv_stack = modbv(int('000110', 2))[6:]
        elif wen_internal & addr == CSR_ADDR_MSTATUS:
            priv_stack = wdata_internal[5:0]
        elif exception:
            priv_stack = concat(priv_stack[2:0], modbv(int('110', 2))[3:])
        elif eret:
            priv_stack = concat(modbv(int('001', 2))[3:], priv_stack[5:3])

    epc.next = mpc

    mstatus = concat(modbv(0)[26:], priv_stack)
    mtdeleg = 0
    mtimer_expired = (mtimecmp == mtime_full[XPR_LEN:])

    @always_seq(clk.posedge)
    def mtimer_setup():
        if reset:
            mtip = 0
            msip = 0
        else:
            if mtimer_expired:
                mtip = 1
            if (wen_internal & addr == CSR_ADDR_MTIMECMP):
                mtip = 0
            if (wen_internal & addr == CSR_ADDR_MIP):
                mtip = wdata_internal[7]
                msip = wdata_internal[3]

    mip = concat(ext_interrupts, mtip, modbv(0)[3:], msip, modbv(0)[3:])


    @always_seq(clk.posedge)
    def wen_setup():
        if reset:
            mie = 0
        elif wen_internal & addr == CSR_ADDR_MIE:
            mie = wdata_internal

    @always_seq(clk.posedge)
    def exception_setup():
        if interrupt_taken:
            mepc = (exception_PC & concat(modbv(1)[30:], modbv(0)[2:])) + modbv(int('4', 16))[XPR_LEN:]
        if exception:
            mepc = exception_PC & concat(modbv(1)[30:], modbv(0)[2:])
        if (wen_internal & addr == CSR_ADDR_MEPC):
            mepc = wdata_internal & concat(modbv(1)[30:], modbv(0)[2:])

    @always_seq(clk.posedge)
    def interrupt_exception_setup():
        if reset:
            mecode = 0
            mint = 0
        elif (wen_internal & addr == CSR_ADDR_MCAUSE):
            mecode = wdata_internal[3:0]
            mint = wdata_internal[31]
        else:
            if interrupt_taken:
                mecode = interrupt_code
                mint = modbv(1)[1:]
            elif exception:
                mecode = exception_code
                mint = modbv(1)[1:]

    mcause = concat(mint, momdbv(0)[27:], mecode)

    code_imem = (exception_code == ECODE_INST_ADDR_MISALIGNED) | (exception_code == ECODE_INST_ADDR_MISALIGNED)

    @always_seq(clk.posedge)
    def exception_load():
        if exception:
            if code_imem:
                mbadaddr = exception_PC
            else:
                mbadaddr = exception_load_addr
        if (wen_internal & addr == CSR_ADDR_MBADADDR):
            mbadaddr = wdata_internal

    @always_comb 
    def host_setup():
        if htif_pcr_req_addr == CSR_ADDR_TO_HOST:
            htif_rdata = to_host
        elif htif_pcr_req_addr == CSR_ADDR_FROM_HOST:
            htif_rdata = from_host
        else:
            htif_rdata = 0

    @always_comb
    def csr_addr_logic():
        if addr == CSR_ADDR_CYCLE:
            rdata.next = cycle_full[XPR_LEN:]
            defined = modbv(1)[1:]
        elif addr == CSR_ADDR_TIME:
            rdata.next = time_full[XPR_LEN:]
            defined = modbv(1)[1:]
        elif addr == CSR_ADDR_INSTRET:
            rdata.next = instret_full[XPR_LEN:]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_CYCLEH:
            rdata.next = cycle_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_TIMEH:
            rdata.next = time_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_INSTRETH:
            rdata.next = instret_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MCPUID:
            rdata.next = mcpuid
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MIMPID:
            rdata.next = mimpid
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MHARTID:
            rdata.next = mhartid
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MSTATUS:
            rdata.next = mstatus
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MTVEC:
            rdata.next = mtvec
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MTDELEG:
            rdata.next = mtdeleg
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MIE:
            rdata.next = mie
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MTIMECMP:
            rdata.next = mtimecmp
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MTIME:
            rdata.next = mtime_full[XPR_LEN:]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MTIMEH:
            rdata.next = mtime_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MSCRATCH:
            rdata.next = mscratch
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MEPC:
            rdata.next = mepc
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MCAUSE:
            rdata.next = mcause
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MBADADDR:
            rdata.next = mbadaddr
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_MIP:
            rdata.next = mip
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_CYCLEW:
            rdata.next = cycle_full[XPR_LEN:]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_TIMEW:
            rdata.next = time_full[XPR_LEN:]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_INSTRETW:
            rdata.next = instret_full[XPR_LEN:]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_CYCLEHW:
            rdata.next = cycle_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_TIMEHW:
            rdata.next = time_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_INSTRETHW:
            rdata.next = instret_full[2*XPR_LEN:XPR_LEN]
            defined = modv(1)[1:]
        elif addr == CSR_ADDR_TO_HOST:
            rdata.next = to_host
            defined = modbv(1)[1:]
        elif addr == CSR_ADDR_FROM_HOST:
            rdata.next = from_host
            defined = modbv(1)[1:]
        else:
            rdata.next = 0
            defined = modbv(0)[1:]

    @always_seq(clk.posedge)
    def csr_seq_logic():
        if reset:
            cycle_full = 0
            time_full = 0
            instret_full = 0
            mtime_full = 0
            to_host = 0
            from_host = 0
            mtvec = modbv(int('100', 16))[12:]
            mtimecmp = 0
            mscratch = 0
        else:
            cycle_full = cycle_full + 1
            time_full = time_full + 1
            if retire:
                instret_full = instret_full + 1
            mtime_full = mtime_full + 1
            if wen_internal:
                if addr == CSR_ADDR_CYCLE:
                    cycle_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_TIME:
                    time_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_INSTRET:
                    instret_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_CYCLEH:
                    cycle_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TIMEH:
                    time_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_INSTRETH:
                    instret_full[2*XPR_LEN:XPR_LEN] = wdata_internal;
                elif addr == CSR_ADDR_MTVEC:
                    mtvec = wdata_internal & concat(modbv(1)[30:], modbv(0)[2:])
                elif addr == CSR_ADDR_MTIMECMP:
                    mtimecmp = wdata_internal
                elif addr == CSR_ADDR_MTIME:
                    mtime_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_MTIMEH:
                    mtime_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_MSCRATCH:
                    mscratch <= wdata_internal
                elif addr == CSR_ADDR_CYCLEW:
                    cycle_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_TIMEW:
                    time_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_INSTRETW:
                    instret_full[XPR_LEN:] = wdata_internal
                elif addr == CSR_ADDR_CYCLEHW:
                    cycle_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TIMEHW:
                    time_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_INSTRETHW:
                    instret_full[2*XPR_LEN:XPR_LEN] = wdata_internal
                elif addr == CSR_ADDR_TO_HOST:
                    to_host <= wdata_internal
                elif addr == CSR_ADDR_FROM_HOST:
                    from_host <= wdata_internal
            if (htif_fire & htif_pcr_req_addr == CSR_ADDR_TO_HOST & ~system_wen):
                to_host = 0

    return csr_setup, interrupt_setup, htif_setup, htif_comb, priv_stack_setup
