from random import randint

from myhdl import block, instance, Signal, modbv, delay, always

from riscv.opcode_constants import REG_ADDR_WIDTH, XPR_LEN
from riscv.register_file import register_file


@block
def test_register_file():

    clock, write_enable = [Signal(False) for _ in range(2)]
    read_addr1, read_addr2, write_addr = [Signal(modbv(0)[REG_ADDR_WIDTH:]) for _ in range(3)]
    read_data1, read_data2, write_data = [Signal(modbv(0)[XPR_LEN:]) for _ in range(3)]

    reg_file_inst = register_file(clock, read_addr1, read_data1, read_addr2, read_data2, write_enable, write_addr, write_data)
    reg_file_inst.convert(hdl='Verilog')

    rand_value = randint(1, (1 << XPR_LEN) - 1)
    rand_addr = randint(1, (1 << REG_ADDR_WIDTH) - 1)

    @always(delay(1))
    def drive_clock():
        clock.next = not clock

    @instance
    def test():
        write_enable.next = True
        yield clock.posedge
        write_data.next = rand_value
        write_addr.next = rand_addr
        yield clock.posedge
        read_addr1.next = rand_addr
        read_addr2.next = rand_addr
        yield clock.posedge
        assert rand_value == read_data1 == read_data2

    return test, reg_file_inst, drive_clock

test_inst = test_register_file()
test_inst.run_sim(10)
test_inst.quit_sim()
