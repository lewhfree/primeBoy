class Cartridge:
    def read(self, addr):
        raise NotImplementedError

    def write(self, addr, val):
        raise NotImplementedError

class NoMapper(Cartridge):
    def __init__(self, romarray):
        self.rom = romarray

    def read(self, addr):
        return self.rom[addr]

    def write(self, addr, val):
        pass

def loadCart(rom):
    type = rom[0x147]
    if type == 0:
        return NoMapper(rom)
