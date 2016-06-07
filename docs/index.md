# RISC-V 

## Pure Python RISC-V 2.0 Decoder

The most important tool whilst creating implementing an ISA is to have a robust decoder in place. The `riscv` module supports a decoder that takes in any instruction bitstring from RISC-V instruction set and returns the instruction name and the arglist in a python dictionary. 

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


## Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

