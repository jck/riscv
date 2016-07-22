from myhdl import block, always_comb, Signal, modbv, always

from riscv.opcode_constants import XPR_LEN


@block
def register_file(clock, read_addr1, read_data1, read_addr2, read_data2, write_enable, write_addr, write_data):

    """
    Read and write from memory.

    :param Signal clock: Clock signal
    :param Signal read_addr1: Read address for first register
    :param Signal read_data1: Read address for second regidter
    :param Signal read_addr2: Read data from first register
    :param Signal read_data2: Read data from second register
    :param Signal write_enable: write enable
    :param Signal write_addr: write address
    :param Signal write_data: Data to be written
    """

    wen_internal = Signal(False)
    data = [Signal(modbv(0)[XPR_LEN:]) for _ in range(32)]

    @always_comb
    def assign():
        if write_addr == 0:
            wen_internal.next = 0
        else:
            wen_internal.next = write_enable

        if read_addr1 == 0:
            read_data1.next = 0
        else:
            read_data1.next = data[read_addr1]

        if read_addr2 == 0:
            read_data2.next = 0
        else:
            read_data2.next = data[read_addr2]

    @always(clock.posedge)
    def sequential():
        if wen_internal:
            data[write_addr].next = write_data

    return assign, sequential
