# RISC-V 

## Pure Python RISC-V 2.0 Decoder

The most important tool whilst implementing an ISA is to have a robust decoder in place. The `riscv` module supports a decoder that takes in any instruction bitstring from RISC-V instruction set and returns the instruction name and the arglist in a python dictionary. 

The decoding processing now is as simple as explained in the below example : 

**Example code**
```
from riscv import decoder

instruction = '10000000000100010000000011100011'
decoded_instruction = decoder.decode(instruction)
decoder.decoder.print_dic(decoded_instruction)
```
which should output something like this : 

**Example output**
```
{
    "instr": "beq",
    "imm12lo": "000000",
    "rs2": "00010",
    "imm12hi": "110000",
    "rs1": "00001"
}
```

## myHDL RV32I Decoder

The RV32I decoder is based on myHDL and implements the decoding based on the main `opcode` and the `funct3` and `funct7` of the instruction. The module takes the instrucition bits as input and generates the output with the active high `arg_select` signal which is a bit string that determines the signal select for the outcoming signals. 

The decoding processing now is as simple as explained in the below example : 

**Example code**
```
from riscv import hdl_decoder

# Signal initialization
	arg_select = Signal(intbv(int('0000000000', 2)))
    opcode = Signal(intbv(int('0000000', 2)))
    funct3 = Signal(intbv(int('000', 2)))
    funct7 = Signal(intbv(int('0000000', 2)))

    rd = Signal(intbv(int('00000', 2)))
    rm = Signal(intbv(int('00000', 2)))
    rs1 = Signal(intbv(int('00000', 2)))
    rs2 = Signal(intbv(int('00000', 2)))
    shamt = Signal(intbv(int('00000', 2)))
    shamtw = Signal(intbv(int('00000', 2)))
    imm12lo = Signal(intbv(int('000000', 2)))
    imm12hi = Signal(intbv(int('000000', 2)))
    imm12 = Signal(intbv(int('000000000000', 2)))
    imm20 = Signal(intbv(int('00000000000000000000', 2)))

    output = hdl_decoder(instruction, arg_select, rs1, rs2, rd, rm, imm12lo, imm12hi, imm12, imm20, shamt, shamtw, opcode, funct3, funct7)

    def stimulus():
    ....

```

## Vscale RV32I Core

The riscv module now supports a fully working RV32I core, an adaptation of the [Zscale](https://github.com/ucb-bar/zscale) Core. The core can be simply called by importing the top level module 

```
from riscv import core

my_core_instance = core(arg1,arg2)

```

A few modules of the core and their functions are discussed below so that they can be reused in other modules/cores:

###### [Source A MUX](https://github.com/jck/riscv/blob/master/riscv/src_a_mux.py)

Multiplexer needed for the first source of operand.

###### [Source B MUX](https://github.com/jck/riscv/blob/master/riscv/src_b_mux.py)

Multiplexer needed for the second source of operand.

###### [PC MUX](https://github.com/jck/riscv/blob/master/riscv/PC_mux.py)

Multiplexer needed for the input to the program counter of the processor.

###### [ALU](https://github.com/jck/riscv/blob/master/riscv/alu.py)

Arithmetic logic unit of the processor with performs the logic-arithmetic calculations for the processor.

###### [Register File](https://github.com/jck/riscv/blob/master/riscv/register_file.py)

Register File for the internal registers of the processor.

###### [Multiply Divide Unit](https://github.com/jck/riscv/blob/master/riscv/mult_div.py)

Multiply and Divide unit of the processor with performs the mult-div calculations for the processor.

###### [Immediate Generators](https://github.com/jck/riscv/blob/master/riscv/immediate_gen.py)

Immediate value generators for the processor.

###### [Hasti Bridge](https://github.com/jck/riscv/blob/master/riscv/hasti_bridge.py)

Memory Bridge for the processor.

###### [Controller](https://github.com/jck/riscv/blob/master/riscv/controller.py)

Control Unit of the processor.

###### [CSR File](https://github.com/jck/riscv/blob/master/riscv/csr_file.py)

Command Status Register File for the processor.

###### [Pipeline](https://github.com/jck/riscv/blob/master/riscv/pipeline.py)

Pipeline Assembly of the different stages of the pipeline. 

###### [SRAM](https://github.com/jck/riscv/blob/master/riscv/dp_hasti_sram.py)

Static Random Access Memory for simulation perpuses

###### [Top Level](https://github.com/jck/riscv/blob/master/riscv/top_level.py)

Top Level module for simulation and verification of the core. Call this module if you need to quickly instantiate the vscale core.

## Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

