from myhdl import block, always_comb

from riscv.hasti_constants import *


@block
def hasti_bridge(haddr, hwrite, hsize, hburst, hmastlock, hprot, htrans, hwdata, core_mem_rdata, core_mem_wait, core_badmem_e,
                 hrdata, hready, hresp, core_mem_en, core_mem_wen, core_mem_size, core_mem_addr, core_mem_wdata_delayed):

    @always_comb
    def assign():
        haddr.next = core_mem_addr

        hwrite.next = core_mem_en and core_mem_wen

        hsize.next = core_mem_size

        hburst.next = HASTI_BURST_SINGLE

        hmastlock.next = HASTI_MASTER_NO_LOCK

        hprot.next = HASTI_NO_PROT

        if core_mem_en:
            htrans.next = HASTI_TRANS_NONSEQ
        else:
            htrans.next = HASTI_TRANS_IDLE

        hwdata.next = core_mem_wdata_delayed

        core_mem_rdata.next = hrdata

        core_mem_wait.next = not hready

        core_badmem_e.next = (hresp == HASTI_RESP_ERROR)

    return assign
