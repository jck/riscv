# RISC-V

[![Build Status](https://travis-ci.org/meetshah1995/riscv.svg?branch=master)](https://travis-ci.org/meetshah1995/riscv)
[![Code Health](https://landscape.io/github/meetshah1995/riscv/master/landscape.svg?style=flat)](https://landscape.io/github/meetshah1995/riscv/master)
[![Coverage Status](https://coveralls.io/repos/github/meetshah1995/riscv/badge.svg?branch=dev)](https://coveralls.io/github/meetshah1995/riscv?branch=dev)
[![Documentation Status](https://readthedocs.org/projects/riscv/badge/?version=latest)](http://riscv.readthedocs.io/en/latest/?badge=latest)

## RISC-V implementation and tools.

### Available tools : 

* Pure Python RISC-V 2.0 decoder.
* myHDL based decoder module.
* myHDL version of RISC-V core [Zscale](https://github.com/ucb-bar/zscale/)
* myHDL based Zscale core modules with individual module tests.

### In Progress :

* Tests for core assembly.


### Installation and Usage

*Cloning the repo*

```
git clone https://github.com/jck/riscv.git
```

*Installing dependencies*

```
cd riscv
python -m pip install -r requirements.txt
```

*Usage*

The core modules can be imported by:

```
from riscv import alu
```

*Running tests*

```
python -m pytest
```

