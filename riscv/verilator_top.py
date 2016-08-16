from myhdl import block, Signal, intbv, always, instance, instances

from riscv.control_constants import HTIF_PCR_WIDTH
from riscv.csr_constants import CSR_ADDR_TO_HOST
from riscv.top_level import top_level


@block
def verilator_top(clock, reset):

    hexfile_words = 8192

    htif_pcr_resp_valid = Signal(intbv(0)[1:])
    htif_pcr_resp_data = Signal(intbv(0)[HTIF_PCR_WIDTH:])

    max_cycles = Signal(intbv(0)[64:])
    trace_count = Signal(intbv(0)[64:])
    reason = Signal(intbv(0)[256:])
    loadmem = Signal(intbv(0)[1024:])
    stderr = intbv(int(80000002, 16))[32:]

    hexfile = [0 for _ in range(hexfile_words)]

    htif_pcr_req_ready = Signal(intbv(0)[1:])

    DUT = top_level(clock, reset, Signal(True), htif_pcr_req_ready, Signal(False), intbv(CSR_ADDR_TO_HOST),
                    Signal(intbv(0))[HTIF_PCR_WIDTH:], htif_pcr_resp_valid, Signal(True), htif_pcr_resp_data)

    loadmem = 0
    reason = 0
    max_cycles = 0
    trace_count = 0

    @instance
    def initial():
        global loadmem, reason, max_cycles, trace_count, hexfile
        loadmem = 0
        reason = 0
        max_cycles = 0
        trace_count = 0
        with open('rv32ui-p-add.hex') as file:
            hexfile = file.read().splitlines()
            for i in range(hexfile_words):
                for j in range(4):
                    DUT.hasti_mem.mem[4 * i + j] = hexfile[i][32 * j + 32:32 * j]

    @always(clock.posedge)
    def seq_logic():
        global trace_count, reason, stderr
        trace_count += 1
        print("Current: " + str(trace_count) + ", max: " + str(max_cycles) + "\n")
        if 0 < max_cycles < trace_count:
            reason = "timeout"

        if not reset:
            if htif_pcr_resp_valid and htif_pcr_resp_data != 0:
                if htif_pcr_resp_data == 1:
                    return
                else:
                    reason = "tohost = " + str(htif_pcr_resp_data >> 1)

        if reason:
            stderr = "*** FAILED *** (" + reason + ") after " + trace_count + " simulation cycles"
            return

    return instances()
