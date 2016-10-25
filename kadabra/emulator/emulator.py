from random import getrandbits
from collections import OrderedDict
from kadabra.arch.arch import Architecture
from kadabra.emulator.memory import PAGESIZE

from kadabra.emulator.hooks import *


class Emulator:
    def __init__(self, arch_id):

        arch = Architecture(arch_id)
        self.arch = arch

        self.registers = arch.registers
        self.mu = Uc(arch.uc_arch, arch.uc_mode)
        self.arch = arch

    def reg_read(self, reg):
        reg = self.registers[reg]
        return self.mu.reg_read(reg)

    def reg_write(self, reg, val):
        reg = self.registers[reg]
        self.mu.reg_write(reg, val)

    def mem_read(self, addr, size):
        return self.mu.mem_read(addr, size)

    def mem_write(self, addr, val):
        self.mu.mem_write(addr, val)

    def start_execution(self, start, end):
        self.mu.emu_start(start, end)

    def stop_execution(self):
        self.mu.emu_stop()

    def mem_map(self, addr, size):
        alignment = addr % PAGESIZE
        base_addr = addr - alignment

        page_size = (int(size / PAGESIZE) * PAGESIZE) + PAGESIZE

        self.mu.mem_map(base_addr, page_size)

    def mem_unmap(self, addr, size):
        self.mu.mem_unmap(addr, size)

    def add_hooks(self):
        self.mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED,
                         hook_mem_invalid, self)

        self.mu.hook_add(UC_HOOK_CODE, hook_code)
        self.mu.hook_add(UC_HOOK_BLOCK, hook_block)

    def initialise_regs_random(self):
        for reg in self.registers:
            if reg == self.arch.IP or reg == self.arch.FLAGS:
                continue
            self.reg_write(reg, getrandbits(self.arch.size))

    def dump_registers(self):
        dump = OrderedDict()
        for reg in self.registers:
            value = self.reg_read(reg)
            dump.update({reg: value})

        return dump