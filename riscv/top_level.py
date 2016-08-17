from myhdl import delay

from riscv.core import *
from riscv.dp_hasti_sram import *


@block
def top_level():
    """
    Top level module for simulation
    """

    clock, reset, htif_pcr_req_valid, htif_pcr_req_ready, htif_pcr_req_rw, htif_pcr_resp_valid, htif_pcr_resp_ready = \
        [Signal(intbv(0)[1:]) for _ in range(7)]
    htif_pcr_req_addr = Signal(intbv(0)[CSR_ADDR_WIDTH:])
    htif_pcr_req_data = Signal(intbv(0)[HTIF_PCR_WIDTH:])
    htif_pcr_resp_data = Signal(intbv(0)[HTIF_PCR_WIDTH:])

    resetn = Signal(intbv(0)[1:])

    imem_haddr = Signal(intbv(0)[HASTI_ADDR_WIDTH:])
    imem_hwrite = Signal(intbv(0)[1:])
    imem_hsize = Signal(intbv(0)[HASTI_SIZE_WIDTH:])
    imem_hburst = Signal(intbv(0)[HASTI_BURST_WIDTH:])

    imem_hmastlock = Signal(intbv(0)[1:])
    imem_hprot = Signal(intbv(0)[HASTI_PROT_WIDTH:])
    imem_htrans = Signal(intbv(0)[HASTI_TRANS_WIDTH:])
    imem_hwdata = Signal(intbv(0)[HASTI_BUS_WIDTH:])

    imem_hrdata = Signal(intbv(0)[HASTI_BUS_WIDTH:])
    imem_hready = Signal(intbv(0)[1:])
    imem_hresp = Signal(intbv(0)[HASTI_RESP_WIDTH:])

    dmem_haddr = Signal(intbv(0)[HASTI_ADDR_WIDTH:])
    dmem_hwrite = Signal(intbv(0)[1:])
    dmem_hsize = Signal(intbv(0)[HASTI_SIZE_WIDTH:])
    dmem_hburst = Signal(intbv(0)[HASTI_BURST_WIDTH:])
    dmem_hmastlock = Signal(intbv(0)[1:])
    dmem_hprot = Signal(intbv(0)[HASTI_PROT_WIDTH:])
    dmem_htrans = Signal(intbv(0)[HASTI_TRANS_WIDTH:])
    dmem_hwdata = Signal(intbv(0)[HASTI_BUS_WIDTH:])
    dmem_hrdata = Signal(intbv(0)[HASTI_BUS_WIDTH:])
    dmem_hready = Signal(intbv(0)[1:])
    dmem_hresp = Signal(intbv(0)[HASTI_RESP_WIDTH:])

    htif_reset = Signal(intbv(0)[1:])

    htif_ipi_req_ready = Signal(intbv(0)[1:])
    htif_ipi_req_valid = Signal(intbv(0)[1:])
    htif_ipi_req_data = Signal(intbv(0)[1:])
    htif_ipi_resp_ready = Signal(intbv(0)[1:])
    htif_ipi_resp_valid = Signal(intbv(0)[1:])
    htif_ipi_resp_data = Signal(intbv(0)[1:])
    htif_debug_stats_pcr = Signal(intbv(0)[1:])

    resetn = not reset
    htif_reset = reset

    @always(delay(10))
    def clock_drive():
        clock.next = not clock

    vscale_core = core(clock=clock,
                       ext_interrupts=Signal(intbv(0)[1:]),
                       imem_haddr=imem_haddr,
                       imem_hwrite=imem_hwrite,
                       imem_hsize=imem_hsize,
                       imem_hburst=imem_hburst,
                       imem_hmastlock=imem_hmastlock,
                       imem_hprot=imem_hprot,
                       imem_htrans=imem_htrans,
                       imem_hwdata=imem_hwdata,
                       imem_hrdata=imem_hrdata,
                       imem_hready=imem_hready,
                       imem_hresp=imem_hresp,
                       dmem_haddr=dmem_haddr,
                       dmem_hwrite=dmem_hwrite,
                       dmem_hsize=dmem_hsize,
                       dmem_hburst=dmem_hburst,
                       dmem_hmastlock=dmem_hmastlock,
                       dmem_hprot=dmem_hprot,
                       dmem_htrans=dmem_htrans,
                       dmem_hwdata=dmem_hwdata,
                       dmem_hrdata=dmem_hrdata,
                       dmem_hready=dmem_hready,
                       dmem_hresp=dmem_hresp,
                       htif_reset=htif_reset,
                       htif_id=Signal(intbv(0)[1:]),
                       htif_pcr_req_valid=htif_pcr_req_valid,
                       htif_pcr_req_ready=htif_pcr_req_ready,
                       htif_pcr_req_rw=htif_pcr_req_rw,
                       htif_pcr_req_addr=htif_pcr_req_addr,
                       htif_pcr_req_data=htif_pcr_req_data,
                       htif_pcr_resp_valid=htif_pcr_resp_valid,
                       htif_pcr_resp_ready=htif_pcr_resp_ready,
                       htif_pcr_resp_data=htif_pcr_resp_data,
                       htif_ipi_req_ready=htif_ipi_req_ready,
                       htif_ipi_req_valid=htif_ipi_req_valid,
                       htif_ipi_req_data=htif_ipi_req_data,
                       htif_ipi_resp_ready=htif_ipi_resp_ready,
                       htif_ipi_resp_valid=htif_ipi_resp_valid,
                       htif_ipi_resp_data=htif_ipi_resp_data,
                       htif_debug_stats_pcr=htif_debug_stats_pcr)

    hasti_mem = dp_hasti_sram(hclk=clock,
                              hresetn=resetn,
                              p1_haddr=imem_haddr,
                              p1_hwrite=imem_hwrite,
                              p1_hsize=imem_hsize,
                              p1_hburst=imem_hburst,
                              p1_hmastlock=imem_hmastlock,
                              p1_hprot=imem_hprot,
                              p1_htrans=imem_htrans,
                              # p1_hwdata=imem_hwdata,
                              p1_hrdata=imem_hrdata,
                              p1_hready=imem_hready,
                              p1_hresp=imem_hresp,
                              p0_haddr=dmem_haddr,
                              p0_hwrite=dmem_hwrite,
                              p0_hsize=dmem_hsize,
                              p0_hburst=dmem_hburst,
                              p0_hmastlock=dmem_hmastlock,
                              p0_hprot=dmem_hprot,
                              p0_htrans=dmem_htrans,
                              p0_hwdata=dmem_hwdata,
                              p0_hrdata=dmem_hrdata,
                              p0_hready=dmem_hready,
                              p0_hresp=dmem_hresp)

    return instances()

inst = top_level()
inst.run_sim(10000)
