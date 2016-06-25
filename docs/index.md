# RISC-V 

## Pure Python RISC-V 2.0 Decoder

The most important tool whilst implementing an ISA is to have a robust decoder in place. The `riscv` module supports a decoder that takes in any instruction bitstring from RISC-V instruction set and returns the instruction name and the arglist in a python dictionary. 

The decoding processing now is as simple as explained in the below example : 

#### Example code
```
from riscv import decoder

instruction = '10000000000100010000000011100011'
decoded_instruction = decoder.decode(instruction)
decoder.decoder.print_dic(decoded_instruction)
```
which should output something like this : 

#### Example output
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

#### Example code
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

## Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

