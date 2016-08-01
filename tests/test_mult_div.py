# from myhdl import block, Signal, modbv, instance, always, delay
# from riscv.md_constants import *
# from riscv.mult_div import mult_div
# from riscv.opcode_constants import XPR_LEN
#
#
# @block
# def test_mult_div():
#     clock, reset, req_valid, req_ready, req_in_1_signed, req_in_2_signed = [Signal(False) for _ in range(6)]
#     req_op = Signal(modbv(0)[MD_OP_WIDTH:])
#     req_out_sel = Signal(modbv(0)[MD_OUT_SEL_WIDTH:])
#     req_in_1, req_in_2, resp_result = [Signal(modbv(0)[XPR_LEN:]) for _ in range(3)]
#     resp_valid = Signal(False)
#
#     mul_div_inst = mult_div(clock, reset, req_valid, req_ready, req_in_1_signed, req_in_2_signed, req_op,
#                             req_out_sel, req_in_1, req_in_2, resp_valid, resp_result)
#     mul_div_inst.convert(hdl='Verilog')
#
#     @always(delay(10))
#     def clock_drive():
#         clock.next = not clock
#         # print(resp_result, resp_valid)
#
#     @instance
#     def test():
#         req_valid.next = True
#         req_op.next = MD_OP_MUL
#         req_out_sel.next = MD_OUT_LO
#         req_in_1.next = 5
#         req_in_2.next = 7
#         yield req_valid.posedge
#         print(resp_result, resp_valid)
#
#     return mul_div_inst, test, clock_drive
#
# test_inst = test_mult_div()
# test_inst.run_sim()
