from myhdl import always_comb, block, modbv, concat, Signal, always, intbv

from riscv.md_constants import *
from riscv.opcode_constants import *


@block
def mult_div(clock, reset, req_valid, req_ready, req_in_1_signed, req_in_2_signed,
             req_op, req_out_sel, req_in_1, req_in_2, resp_valid, resp_result):

    md_state_width = 2
    s_idle = 0
    s_compute = 1
    s_setup_output = 2
    s_done = 3

    state = Signal(modbv(0)[md_state_width:])
    next_state = Signal(modbv(0)[md_state_width:])

    op = Signal(modbv(0)[MD_OP_WIDTH:])
    out_sel = Signal(modbv(0)[MD_OUT_SEL_WIDTH:])

    a = Signal(modbv(0)[DOUBLE_XPR_LEN:])
    b = Signal(modbv(0)[DOUBLE_XPR_LEN:])
    result = Signal(modbv(0)[DOUBLE_XPR_LEN:])
    counter = Signal(modbv(0)[LOG2_XPR_LEN:])

    negate_output = Signal(False)
    sign_in_1 = Signal(False)
    sign_in_2 = Signal(False)
    a_geq = Signal(False)
    abs_in_1 = Signal(modbv(0)[XPR_LEN:])
    abs_in_2 = Signal(modbv(0)[XPR_LEN:])

    result_muxed = Signal(modbv(0)[DOUBLE_XPR_LEN:])
    result_muxed_negated = Signal(modbv(0)[DOUBLE_XPR_LEN:])
    final_result = Signal(modbv(0)[XPR_LEN:])

    def abs_input(data, is_signed):
        if data[XPR_LEN - 1] and is_signed:
            return intbv(-data)[XPR_LEN:]
        else:
            return intbv(+data)[XPR_LEN:]

    @always_comb
    def assign_1():
        req_ready.next = (state == s_idle)
        resp_valid.next = (state == s_done)
        resp_result.next = result[XPR_LEN:0]

        abs_in_1.next = abs_input(req_in_1, req_in_1_signed)
        sign_in_1.next = req_in_1_signed and req_in_1[XPR_LEN - 1]
        abs_in_2.next = abs_input(req_in_2, req_in_2_signed)
        sign_in_2.next = req_in_2_signed and req_in_2[XPR_LEN - 1]

        a_geq.next = a >= b
        if out_sel == MD_OUT_REM:
            result_muxed.next = a
        else:
            result_muxed.next = result
        if out_sel == MD_OUT_HI:
            final_result.next = result_muxed_negated[2 * XPR_LEN:XPR_LEN]
        else:
            final_result.next = result_muxed_negated[XPR_LEN:0]

    @always_comb
    def assign_2():
        if negate_output:
            result_muxed_negated.next = -result_muxed
        else:
            result_muxed_negated.next = result_muxed

    @always(clock.posedge)
    def change_state():
        if reset:
            state.next = s_idle
        else:
            state.next = next_state

    @always_comb
    def state_assign():
        if state == s_idle:
            if req_valid:
                next_state.next = s_compute
            else:
                next_state.next = s_idle
        elif state == s_compute:
            if counter:
                next_state.next = s_compute
            else:
                next_state.next = s_setup_output
        elif state == s_setup_output:
            next_state.next = s_done
        elif state == s_done:
            next_state.next = s_idle
        else:
            next_state.next = s_idle

    @always(clock.posedge)
    def state_machine():
        if state == s_idle:
            if req_valid:
                result.next = 0
                a.next = abs_in_1
                b.next = concat(abs_in_2, modbv(0)[XPR_LEN:]) >> 1
                if op == MD_OP_REM:
                    negate_output.next = sign_in_1
                else:
                    negate_output.next = sign_in_1 ^ sign_in_2
                out_sel.next = req_out_sel
                op.next = req_op
                counter.next = XPR_LEN - 1
        elif state == s_compute:
            counter.next = counter + 1
            b.next = b >> 1
            if op == MD_OP_MUL:
                if a[counter]:
                    result.next = result + b
            else:
                b.next = b + 1
                if a_geq:
                    a.next = a - b
                    result.next = modbv(1 << counter)[DOUBLE_XPR_LEN:] | result
        elif state == s_setup_output:
            result.next = concat(modbv(0)[XPR_LEN:], final_result)

    return assign_1, assign_2, change_state, state_assign, state_machine
