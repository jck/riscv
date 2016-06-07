from setuptools import setup

setup(
    name='riscv',
    author='Keerthan Jaic',
    author_email='jckeerthan@gmail.com',
    url='http://github.com/jck/riscv',
    packages=['riscv','tests'],
    description='RISC-V implementation and tools',
    install_requires = ['myhdl >= 1.0.dev0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
