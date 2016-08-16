CSR_ADDR_WIDTH     = 12
CSR_COUNTER_WIDTH  = 64


CSR_ADDR_CYCLE     = 0xC00
CSR_ADDR_TIME      = 0xC01
CSR_ADDR_INSTRET   = 0xC02
CSR_ADDR_CYCLEH    = 0xC80
CSR_ADDR_TIMEH     = 0xC81
CSR_ADDR_INSTRETH  = 0xC82
CSR_ADDR_MCPUID    = 0xF00
CSR_ADDR_MIMPID    = 0xF01
CSR_ADDR_MHARTID   = 0xF10
CSR_ADDR_MSTATUS   = 0x300
CSR_ADDR_MTVEC     = 0x301
CSR_ADDR_MTDELEG   = 0x302
CSR_ADDR_MIE       = 0x304
CSR_ADDR_MTIMECMP  = 0x321
CSR_ADDR_MTIME     = 0x701
CSR_ADDR_MTIMEH    = 0x741
CSR_ADDR_MSCRATCH  = 0x340
CSR_ADDR_MEPC      = 0x341
CSR_ADDR_MCAUSE    = 0x342
CSR_ADDR_MBADADDR  = 0x343
CSR_ADDR_MIP       = 0x344
CSR_ADDR_CYCLEW    = 0x900
CSR_ADDR_TIMEW     = 0x901
CSR_ADDR_INSTRETW  = 0x902
CSR_ADDR_CYCLEHW   = 0x980
CSR_ADDR_TIMEHW    = 0x981
CSR_ADDR_INSTRETHW = 0x982

CSR_ADDR_TO_HOST   = 0x780
CSR_ADDR_FROM_HOST = 0x781

CSR_CMD_WIDTH = 3
CSR_IDLE      = 0
CSR_READ      = 4
CSR_WRITE     = 5
CSR_SET       = 6
CSR_CLEAR     = 7

ECODE_WIDTH                      = 4
ECODE_INST_ADDR_MISALIGNED       = 0
ECODE_INST_ADDR_FAULT            = 1
ECODE_ILLEGAL_INST               = 2
ECODE_BREAKPOINT                 = 3
ECODE_LOAD_ADDR_MISALIGNED       = 4
ECODE_LOAD_ACCESS_FAULT          = 5
ECODE_STORE_AMO_ADDR_MISALIGNED  = 6
ECODE_STORE_AMO_ACCESS_FAULT     = 7
ECODE_ECALL_FROM_U               = 8
ECODE_ECALL_FROM_S               = 9
ECODE_ECALL_FROM_H               = 10
ECODE_ECALL_FROM_M               = 11

ICODE_SOFTWARE = 0
ICODE_TIMER    = 1

PRV_WIDTH     = 2
PRV_U         = 0
PRV_S         = 1
PRV_H         = 2
PRV_M         = 3


# Platform constants 
N_EXT_INTS = 24
