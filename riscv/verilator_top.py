from myhdl import block, Signal, intbv, always, instance

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

    hexfile = [Signal(intbv(0)[128:]) for _ in range(hexfile_words)]

    htif_pcr_req_ready = Signal(intbv(0)[1:])

    DUT = top_level(clock, reset, Signal(True), htif_pcr_req_ready, Signal(False), intbv(CSR_ADDR_TO_HOST),
                    Signal(intbv(0))[HTIF_PCR_WIDTH:], htif_pcr_resp_valid, Signal(True), htif_pcr_resp_data)

    i = 0
    j = 0
    tmp = 0
    loadmem = 0
    reason = 0
    max_cycles = 0
    trace_count = 0

    @instance
    def initial():
        global loadmem, reason, max_cycles, trace_count
        loadmem = 0
        reason = 0
        max_cycles = 0
        trace_count = 0
        # if ($value$plusargs("max-cycles=%d", max_cycles) & & $value$plusargs("loadmem=%s", loadmem)) begin
            # $readmemh(loadmem, hexfile);
            # for (i = 0; i < hexfile_words; i = i + 1) begin
            # for (j = 0; j < 4; j = j + 1) begin
            # DUT.hasti_mem.mem[4 * i+j] = hexfile[i][32 * j+:32];

    @always(clock.posedge)
    def seq_logic():
        global trace_count, reason
        trace_count += 1
        # $display("Current: %d, max: %d\n", trace_count, max_cycles);
        if 0 < max_cycles < trace_count:
            reason = "timeout"

        if not reset:
            if htif_pcr_resp_valid and htif_pcr_resp_data != 0:
                if htif_pcr_resp_data == 1:
                    exit()
                else:
                    # $sformat(reason, "tohost = %d", htif_pcr_resp_data >> 1)
                    pass

        if reason:
            # $fdisplay(stderr, "*** FAILED *** (%s) after %d simulation cycles", reason, trace_count);
            exit()
