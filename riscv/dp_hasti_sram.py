from myhdl import block, intbv, instances, concat
from riscv.hasti_constants import *


@block
def dp_hasti_sram(hclk,
                  hresetn,
                  p0_haddr,
                  p0_hwrite,
                  p0_hsize,
                  p0_hburst,
                  p0_hmastlock,
                  p0_hprot,
                  p0_htrans,
                  p0_hwdata,
                  p0_hrdata,
                  p0_hready,
                  p0_hresp,
                  p1_haddr,
                  p1_hwrite,
                  p1_hsize,
                  p1_hburst,
                  p1_hmastlock,
                  p1_hprot,
                  p1_htrans,
                  p1_hwdata,
                  p1_hready,
                  p1_hresp):
    """
    S-RAM module for simulation and verification
    """

    nwords = 65536
    s_w1 = 0
    s_w2 = 1

    mem = [intbv(0)[HASTI_BUS_WIDTH:] for i in range(nwords - 1)]

    p0_waddr = intbv(0)[HASTI_ADDR_WIDTH:]
    p0_wdata = intbv(0)[HASTI_BUS_WIDTH:]
    p0_wvalid = intbv(0)[1:]
    p0_wsize = intbv(0)[HASTI_SIZE_WIDTH:]
    p0_state = intbv(0)[1:]

    if p0_wsize == 0:
        p0_wmask_lut = intbv(0x1)[HASTI_BUS_NBYTES:]
    elif p0_wsize == 1:
        p0_wmask_lut = intbv(0x3)[HASTI_BUS_NBYTES:]
    else:
        p0_wmask_lut = intbv(0xf)[HASTI_BUS_NBYTES:]

    wmask_concat = concat(intbv(p0_wmask_shift[3])[8:],
                          intbv(p0_wmask_shift[2])[8:],
                          intbv(p0_wmask_shift[1])[8:],
                          intbv(p0_wmask_shift[0])[8:])
    p0_wmask = intbv(wmask_concat)[HASTI_BUS_WIDTH:]

    p0_wmask_shift = intbv(p0_wmask_lut << p0_waddr[1:0])[HASTI_BUS_NBYTES:]
    p0_word_waddr = intbv(p0_waddr >> 2)[HASTI_ADDR_WIDTH:]

    p0_raddr = intbv(p0_haddr >> 2)[HASTI_ADDR_WIDTH:]
    p0_ren = intbv(p0_htrans == HASTI_TRANS_NONSEQ and not p0_hwrite)[1:]
    p0_bypass = intbv(0)[1:]
    p0_reg_raddr = intbv(0)[HASTI_ADDR_WIDTH:]

    @always(hclk.posedge)
    def p0():
        p0_reg_raddr = p0_raddr
        if not hresetn:
            p0_state = s_w1
            p0_wvalid = intbv(0)[1:]
            p0_bypass = intbv(0)[1:]
            p0_waddr = intbv(0)[1:]
            p0_wdata = intbv(0)[1:]
            p0_reg_raddr = intbv(0)[1:]
        else:
            if (p0_state == s_w2):
                p0_wdata = p0_hwdata
                p0_state = s_w1
            if (p0_htrans == HASTI_TRANS_NONSEQ):
                if p0_hwrite:
                    p0_waddr = p0_haddr
                    p0_wsize = p0_hsize
                    p0_wvalid = intbv(1)[1:]
                    if (p0_wvalid):
                        mem[p0_word_waddr] = (mem[p0_word_waddr] & (not p0_wmask)) | (p0_wdata & p0_wmask)
                    p0_state = s_w2
                else:
                    p0_bypass = p0_wvalid & p0_word_waddr == p0_raddr

    p0_rdata = intbv(mem[p0_reg_raddr])[HASTI_BUS_WIDTH:]
    p0_rmask = intbv(intbv(p0_bypass)[32:] & p0_wmask)[HASTI_BUS_WIDTH:]
    p0_hrdata = (p0_wdata & p0_rmask) | (p0_rdata & (not p0_rmask))
    p0_hready = intbv(1)[1:]
    p0_hresp = HASTI_RESP_OKAY

    p1_raddr = intbv(p1_haddr >> 2)[HASTI_ADDR_WIDTH:]
    p1_ren = intbv((p1_htrans == HASTI_TRANS_NONSEQ & (not p1_hwrite)))[1:]
    p1_bypass = intbv(0)[1:]
    p1_reg_raddr = intbv(0)[HASTI_ADDR_WIDTH:]

    @always(hclk.posedge)
    def p1():
        p1_reg_raddr = p1_raddr
        if not hresetn:
            p1_bypass = 0
        else:
            if p1_htrans == HASTI_TRANS_NONSEQ:
                if p1_hwrite:
                    pass
                else:
                    p1_bypass = p0_wvalid & p0_word_waddr == p1_raddr

    p1_rdata = intbv(mem[p1_reg_raddr])[HASTI_BUS_WIDTH:]
    p1_rmask = intbv(intbv(p1_bypass)[32:] and p0_wmask)[HASTI_BUS_WIDTH:]
    p1_hrdata = (p0_wdata & p1_rmask) | (p1_rdata & (not p1_rmask))
    p1_hready = intbv(1)[1:]
    p1_hresp = HASTI_RESP_OKAY

    return instances()
