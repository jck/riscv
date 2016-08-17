from myhdl import instance, delay

from riscv.csr_file import *
from riscv.hasti_bridge import *
from riscv.pipeline import pipeline


@block
def core(clock,
         ext_interrupts,
         imem_haddr,
         imem_hwrite,
         imem_hsize,
         imem_hburst,
         imem_hmastlock,
         imem_hprot,
         imem_htrans,
         imem_hwdata,
         imem_hrdata,
         imem_hready,
         imem_hresp,
         dmem_haddr,
         dmem_hwrite,
         dmem_hsize,
         dmem_hburst,
         dmem_hmastlock,
         dmem_hprot,
         dmem_htrans,
         dmem_hwdata,
         dmem_hrdata,
         dmem_hready,
         dmem_hresp,
         htif_reset,
         htif_id,
         htif_pcr_req_valid,
         htif_pcr_req_ready,
         htif_pcr_req_rw,
         htif_pcr_req_addr,
         htif_pcr_req_data,
         htif_pcr_resp_valid,
         htif_pcr_resp_ready,
         htif_pcr_resp_data,
         htif_ipi_req_ready,
         htif_ipi_req_valid,
         htif_ipi_req_data,
         htif_ipi_resp_ready,
         htif_ipi_resp_data,
         htif_ipi_resp_valid,
         htif_debug_stats_pcr):
    """
    Vscale : Core module assembly
    """

    imem_wait = Signal(intbv(0)[1:])
    imem_addr = Signal(intbv(0)[HASTI_ADDR_WIDTH:0])
    imem_rdata = Signal(intbv(0)[HASTI_BUS_WIDTH:0])
    imem_badmem_e = Signal(intbv(0)[1:])
    dmem_wait = Signal(intbv(0)[1:])
    dmem_en = Signal(intbv(0)[1:])
    dmem_wen = Signal(intbv(0)[1:])
    dmem_size = Signal(intbv(0)[HASTI_SIZE_WIDTH:0])
    dmem_addr = Signal(intbv(0)[HASTI_ADDR_WIDTH:0])
    dmem_wdata_delayed = Signal(intbv(0)[HASTI_BUS_WIDTH:0])
    dmem_rdata = Signal(intbv(0)[HASTI_BUS_WIDTH:0])
    dmem_badmem_e = Signal(intbv(0)[1:])

    @instance
    def assign():
        htif_ipi_req_valid.next = intbv(0)[1:]
        htif_ipi_req_data.next = intbv(0)[1:]
        htif_ipi_resp_ready.next = intbv(1)[1:]
        htif_debug_stats_pcr.next = intbv(0)[1:]
        yield delay(1)

    imem_bridge = hasti_bridge(haddr=imem_haddr,
                               hwrite=imem_hwrite,
                               hsize=imem_hsize,
                               hburst=imem_hburst,
                               hmastlock=imem_hmastlock,
                               hprot=imem_hprot,
                               htrans=imem_htrans,
                               hwdata=imem_hwdata,
                               hrdata=imem_hrdata,
                               hready=imem_hready,
                               hresp=imem_hresp,
                               core_mem_en=intbv(1)[1:],
                               core_mem_wen=intbv(0)[1:],
                               core_mem_size=HASTI_SIZE_WORD,
                               core_mem_addr=imem_addr,
                               core_mem_wdata_delayed=intbv(0)[32:],
                               core_mem_rdata=imem_rdata,
                               core_mem_wait=imem_wait,
                               core_badmem_e=imem_badmem_e)

    dmem_bridge = hasti_bridge(haddr=dmem_haddr,
                               hwrite=dmem_hwrite,
                               hsize=dmem_hsize,
                               hburst=dmem_hburst,
                               hmastlock=dmem_hmastlock,
                               hprot=dmem_hprot,
                               htrans=dmem_htrans,
                               hwdata=dmem_hwdata,
                               hrdata=dmem_hrdata,
                               hready=dmem_hready,
                               hresp=dmem_hresp,
                               core_mem_en=dmem_en,
                               core_mem_wen=dmem_wen,
                               core_mem_size=dmem_size,
                               core_mem_addr=dmem_addr,
                               core_mem_wdata_delayed=dmem_wdata_delayed,
                               core_mem_rdata=dmem_rdata,
                               core_mem_wait=dmem_wait,
                               core_badmem_e=dmem_badmem_e)

    pipeline_inst = pipeline(clock=clock,
                             ext_interrupts=ext_interrupts,
                             reset=htif_reset,
                             imem_wait=imem_wait,
                             imem_addr=imem_addr,
                             imem_rdata=imem_rdata,
                             imem_badmem_e=imem_badmem_e,
                             dmem_wait=dmem_wait,
                             dmem_en=dmem_en,
                             dmem_wen=dmem_wen,
                             dmem_size=dmem_size,
                             dmem_addr=dmem_addr,
                             dmem_wdata_delayed=dmem_wdata_delayed,
                             dmem_rdata=dmem_rdata,
                             dmem_badmem_e=dmem_badmem_e,
                             htif_reset=htif_reset,
                             htif_pcr_req_valid=htif_pcr_req_valid,
                             htif_pcr_req_ready=htif_pcr_req_ready,
                             htif_pcr_req_rw=htif_pcr_req_rw,
                             htif_pcr_req_addr=htif_pcr_req_addr,
                             htif_pcr_req_data=htif_pcr_req_data,
                             htif_pcr_resp_valid=htif_pcr_resp_valid,
                             htif_pcr_resp_ready=htif_pcr_resp_ready,
                             htif_pcr_resp_data=htif_pcr_resp_data)

    return instances()
