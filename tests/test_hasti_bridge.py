from myhdl import Signal, modbv

from riscv.hasti_bridge import hasti_bridge
from riscv.hasti_constants import *


def test_hasti_bridge():
    haddr, core_mem_addr = [Signal(modbv(0)[HASTI_ADDR_WIDTH:]) for _ in range(2)]
    hsize, core_mem_size = [Signal(modbv(0)[HASTI_SIZE_WIDTH:]) for _ in range(2)]
    hwrite, hmastlock, hready, core_mem_wn, core_mem_wen, core_mem_en, core_mem_wait, core_badmem_e = [Signal(False) for
                                                                                                       _ in range(8)]
    hburst = Signal(modbv(0)[HASTI_BURST_WIDTH:])
    hprot = Signal(modbv(0)[HASTI_PROT_WIDTH:])
    htrans = Signal(modbv(0)[HASTI_TRANS_WIDTH:])
    hwdata, hrdata, core_mem_wdata_delayed, core_mem_rdata = [Signal(modbv(0)[HASTI_BUS_WIDTH:]) for _ in range(4)]
    hresp = Signal(modbv(0)[HASTI_RESP_WIDTH:])

    hasti_bridge_inst = hasti_bridge(haddr, hwrite, hsize, hburst, hmastlock, hprot, htrans, hwdata, core_mem_rdata,
                                     core_mem_wait, core_badmem_e, hrdata, hready, hresp, core_mem_en, core_mem_wen,
                                     core_mem_size, core_mem_addr, core_mem_wdata_delayed)
    hasti_bridge_inst.convert(hdl='Verilog')


test_hasti_bridge()
